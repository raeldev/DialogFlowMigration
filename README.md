# GECX Enterprise AI Agent and Platform Migration POC

This project is a technical reference implementation designed for the Cloud Platform Engineer (GECX) role. It demonstrates how to migrate legacy rules-based contact center bots built on Dialogflow ES or CX over to a modern Generative AI agent architecture using Google Cloud Gemini Enterprise for Customer Experience (GECX) concepts.

## Project Context and Architectural Highlights

Traditional Contact Center AI implementations rely on rigid intent matching and deterministic state machines (Dialogflow). While effective for simple transactions, they often struggle with multi-intent utterances, unexpected user phrasing, and complex context switching, resulting in intent collision and frequent fallback errors.

This implementation showcases the transition to an autonomous GECX agent architecture:

* **Dynamic Reasoning vs. Rigid Rules:** Replaces Dialogflow's static training phrases with LLM reasoning to handle compound requests and execute tools dynamically.
* **Grounding and RAG Integration:** Grounds agent replies in enterprise knowledge base articles to eliminate hallucinations.
* **Side-by-Side Migration Benchmarker:** Runs customer queries against both Dialogflow and GECX to prove accuracy gains and migration feasibility.
* **Enterprise Observability:** Emulates CCAI Insights sentiment scoring and emits structured JSON logs for Google Cloud Logging.

## POC Simplifications and Production Roadmap

To keep this project lightweight, portable, and easy for technical evaluators to verify without requiring GCP IAM provisioning or active cloud billing, several components use simplified implementations. Below is how these map to a live enterprise production deployment on Google Cloud:

* **Knowledge Base (RAG):** Implemented in memory for instant local execution. In production, this replaces the `IKnowledgeProvider` interface with Google Cloud Vertex AI Search or vector search indices.
* **Telephony and CCaaS Integration:** Exposed via clean REST API endpoints (`POST /chat`). In a live environment, this connects to telephony bridges (Genesys Cloud CX, Avaya) or Google Cloud Audio Connector using web sockets and the Gemini Multimodal Live API.
* **Session Storage:** Managed via Python server state. In production, conversation history persists across multi-region clusters using Cloud Spanner or Memorystore for Redis.
* **Infrastructure:** Runs on local FastAPI and Uvicorn. Enterprise deployment provisions containerized Cloud Run or GKE services orchestrated via Terraform and Cloud Build CI/CD pipelines.

## How to Run the Application

1. Activate your Python virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the automated test suite to verify all backend services:
```bash
PYTHONPATH=. rtk pytest -v
```

3. Start the API server locally:
```bash
PYTHONPATH=. uvicorn api.main:app --reload --port 8000
```

## Manual Testing and Dialogflow vs. GECX Comparison

Once the server is running on port 8000, you can execute a manual comparison test to observe the differences between legacy Dialogflow intent handling and modern GECX agent reasoning.

You can run this test directly from your terminal using cURL or by navigating to `http://localhost:8000/docs` in your browser.

### Step 1: Run the Side-by-Side Benchmark

Execute the benchmark endpoint to simulate realistic customer utterances across both engines simultaneously:

```bash
curl -X POST "http://localhost:8000/simulate/benchmark" -H "Content-Type: application/json"
```

### Step 2: Analyzing the Output

The response returns a detailed comparison across multiple customer support scenarios:

1. **Simple Intent (TC-01):**
   * Utterance: "Check my billing invoice status"
   * Legacy Dialogflow: Succeeds by matching the exact `billing.invoice` intent pattern.
   * GECX Agent: Succeeds by dynamically identifying the intent and invoking the `get_invoice_status` CRM tool.

2. **Compound Multi-Intent Utterance (TC-03):**
   * Utterance: "I was charged twice on my invoice and now my internet is slow, can you run a check?"
   * Legacy Dialogflow: Fails (`success: false`). The rule-based engine experiences intent collision between billing keywords and technical support keywords, triggering a "Default Fallback Intent".
   * GECX Agent: Succeeds (`success: true`). The generative agent comprehends both issues within the single prompt, executes the diagnostic tool `run_network_diagnostic`, and addresses both the billing inquiry and network latency coherently.

### Step 3: Test Interactive Conversational Turns

To interact directly with the GECX agent and inspect CCAI Insights analytics, send a message to the chat endpoint:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "TEST-01", "user_message": "My router has a blinking red light and speed is slow."}'
```

The response returns the grounded agent reply, the list of CRM tools invoked automatically (`run_network_diagnostic`), and real-time CCAI Insights metrics including sentiment score and topic classification.
