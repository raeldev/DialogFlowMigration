# GECX Enterprise AI Agent and Platform Migration POC

This project is a technical reference implementation designed for the Cloud Platform Engineer (GECX) role. It demonstrates how to migrate legacy rules-based contact center bots built on Dialogflow ES or CX over to a modern Generative AI agent architecture using Google Cloud Gemini Enterprise for Customer Experience (GECX) concepts.

## Project Context and Architectural Highlights

Traditional Contact Center AI implementations rely on rigid intent matching and deterministic state machines (Dialogflow). While effective for simple transactions, they often struggle with multi-intent utterances, unexpected user phrasing, and complex context switching, resulting in intent collision and frequent fallback errors.

This implementation showcases the transition to an autonomous GECX agent architecture:

* **Dynamic Reasoning vs. Rigid Rules:** Replaces Dialogflow's static training phrases with LLM reasoning to handle compound requests and execute tools dynamically.
* **Grounding and RAG Integration:** Grounds agent replies in enterprise knowledge base articles via Google Cloud Vertex AI Search to eliminate hallucinations while maintaining strict CCaaS timeout SLAs.
* **Side-by-Side Migration Benchmarker:** Runs customer queries against both Dialogflow and GECX to prove accuracy gains and migration feasibility.
* **Enterprise Observability:** Emulates CCAI Insights sentiment scoring and emits non-blocking structured JSON logs directly to Google Cloud Logging.

## Application Execution Modes

The platform uses Dependency Inversion to support two operational modes:

1. **Local Mock Mode:** Runs completely offline in memory without requiring cloud billing or active credentials.
2. **Real GCP Production Mode:** Connects to live Google Cloud Platform services including Vertex AI Search (Discovery Engine), Vertex AI Gemini, and Cloud Logging.

## How to Run the Application Locally (Offline Mode)

1. Activate your Python virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the automated test suite across all 23 unit and integration tests:
```bash
./.venv/bin/pytest -v
```

3. Start the API server in local fallback mode:
```bash
export USE_REAL_GCP="false"
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

## How to Configure and Run with Real Google Cloud Services

To verify the live cloud integrations, you need an active Google Cloud project with Vertex AI and Discovery Engine APIs enabled.

### Step 1: GCP Authentication and API Enablement

Authenticate your terminal session using Application Default Credentials (ADC):
```bash
gcloud auth application-default login
gcloud config set project <YOUR_GCP_PROJECT_ID>
```

Enable the required Google Cloud APIs:
```bash
gcloud services enable aiplatform.googleapis.com \
                       discoveryengine.googleapis.com \
                       logging.googleapis.com
```

Ensure your IAM user or service account has the following roles:
* `roles/discoveryengine.viewer` (for searching RAG data stores)
* `roles/aiplatform.user` (for generating answers via Vertex AI Gemini)
* `roles/logging.logWriter` (for writing asynchronous logs to Cloud Logging)

### Step 2: Configure Environment Variables

Export the required configuration variables pointing to your GCP infrastructure:
```bash
export USE_REAL_GCP="true"
export GCP_PROJECT_ID="your-gcp-project-id"
export GCP_LOCATION="us-central1"
export GCP_DATA_STORE_ID="your-discovery-engine-data-store-id"
export GCP_RAG_TIMEOUT_SECONDS="4.0"
export GCP_GEMINI_MODEL="gemini-1.5-flash-002"
```

### Step 3: Start the Connected Application Server

Launch the server with live GCP dependencies wired via the startup lifespan:
```bash
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

## Manual Testing and Dialogflow vs. GECX Comparison

Once the application is running on port 8000 (either in local mode or connected to live GCP services), you can execute manual benchmark comparisons or interactive chat turns. For detailed step-by-step UI testing, refer to the [MANUAL_TESTING_GUIDE.md](file:///Users/admin/Projects/TechnicalTests/EMEA_GECX/MANUAL_TESTING_GUIDE.md).

### Step 1: Run the Side-by-Side Benchmark

Execute the benchmark endpoint from your terminal to simulate realistic customer utterances across both engines simultaneously:

```bash
curl -X POST "http://localhost:8000/simulate/benchmark" -H "Content-Type: application/json"
```

### Step 2: Analyzing the Benchmark Output

The response returns a structured comparison across multiple customer support scenarios:

1. **Simple Intent (TC-01):**
   * Utterance: "Check my billing invoice status"
   * Legacy Dialogflow: Succeeds by matching the exact `billing.invoice` intent pattern.
   * GECX Agent: Succeeds by dynamically identifying the intent and invoking the `get_invoice_status` CRM tool.

2. **Compound Multi-Intent Utterance (TC-03):**
   * Utterance: "I was charged twice on my invoice and now my internet is slow, can you run a check?"
   * Legacy Dialogflow: Fails (`success: false`). The rule-based engine experiences intent collision between billing keywords and technical support keywords, triggering a "Default Fallback Intent".
   * GECX Agent: Succeeds (`success: true`). The generative agent comprehends both issues within the single prompt, executes the diagnostic tool `run_network_diagnostic`, and addresses both the billing inquiry and network latency coherently.

### Step 3: Test Interactive Conversational Turns

To interact directly with the GECX agent and inspect real-time tool executions and CCAI Insights analytics, send a request to the chat endpoint:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "TEST-GCP-01", "user_message": "My router has a blinking red light and speed is slow."}'
```

When running with `USE_REAL_GCP="true"`, the server will retrieve grounding articles directly from your Discovery Engine data store, generate responses via Vertex AI Gemini, and emit non-blocking structured telemetry events directly into Google Cloud Logging.
