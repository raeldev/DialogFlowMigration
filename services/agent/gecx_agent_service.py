import os
import time
import json
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types

from services.interfaces.agent_provider import IAgentProvider
from services.interfaces.knowledge_provider import IKnowledgeProvider
from services.tools.crm_tools import AVAILABLE_TOOLS

logger = logging.getLogger("gecx.agent")

SYSTEM_INSTRUCTIONS = """You are GECX Assist, an enterprise customer experience AI agent for Apex Telecom & Financial Services.
Your job is to assist customers with telecom technical support, billing inquiries, and contract terms.
Always ground your responses on the provided knowledge articles (RAG) and invoke tools when account or equipment diagnostics are needed.
Maintain a polite, professional, and empathetic brand voice."""

class GECXAgentService(IAgentProvider):
    """
    Concrete implementation of GECX Agent engine using google-genai SDK.
    Manages in-memory session history, RAG grounding injection, and tool calling.
    """
    def __init__(self, knowledge_provider: IKnowledgeProvider, llm_client: Any = None):
        self.knowledge_provider = knowledge_provider
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        use_gcp = os.getenv("USE_REAL_GCP", "").lower() in ("true", "1", "yes")
        self.model_name = os.getenv("GCP_GEMINI_MODEL", "gemini-1.5-flash-002") if use_gcp else "gemini-2.5-flash"
        if llm_client:
            self.client = llm_client
        elif use_gcp:
            project_id = os.getenv("GCP_PROJECT_ID")
            location = os.getenv("GCP_LOCATION", "us-central1")
            try:
                self.client = genai.Client(vertexai=True, project=project_id, location=location)
            except Exception as e:
                logger.warning(f"Could not initialize genai.Client in Vertex AI mode: {e}")
                self.client = None
        else:
            api_key = os.getenv("GEMINI_API_KEY", "mock_key_for_testing")
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.warning(f"Could not initialize genai.Client: {e}")
                self.client = None

    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # Initialize session history if new
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Retrieve RAG articles
        rag_articles = self.knowledge_provider.search_articles(user_message)
        grounding_context = "\n".join([f"[{a['id']}] {a['title']}: {a['content']}" for a in rag_articles])
        
        augmented_prompt = f"Grounding Knowledge:\n{grounding_context}\n\nUser Message: {user_message}" if grounding_context else user_message
        self.sessions[session_id].append({"role": "user", "text": user_message})
        
        tools_executed = []
        reply = ""

        if self.client and hasattr(self.client, "models") and hasattr(self.client.models, "generate_content"):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                    tools=AVAILABLE_TOOLS,
                    temperature=0.2
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=augmented_prompt,
                    config=config
                )
                reply = response.text or "Processed request successfully."
                if hasattr(response, "function_calls") and response.function_calls:
                    for fc in response.function_calls:
                        tools_executed.append(fc.name)
            except Exception as err:
                logger.error(f"LLM generation error: {err}")
                reply = f"System notice: Executed fallback processing due to LLM connectivity ({err})."
        else:
            # Local mock fallback for deterministic testing without external API calls
            if "invoice" in user_message.lower() or "bill" in user_message.lower():
                from services.tools.crm_tools import get_invoice_status
                res = get_invoice_status("DEMO-123")
                tools_executed.append("get_invoice_status")
                reply = f"Your invoice status for DEMO-123 is {res['status']} ({res['invoice_amount']})."
            elif "internet" in user_message.lower() or "wifi" in user_message.lower() or "slow" in user_message.lower():
                from services.tools.crm_tools import run_network_diagnostic
                res = run_network_diagnostic("ROUTER-DEMO")
                tools_executed.append("run_network_diagnostic")
                reply = f"Network diagnostic for ROUTER-DEMO completed: {res['status']} (Packet loss: {res['packet_loss_pct']}%)."
            else:
                reply = "Thank you for contacting Apex Telecom & Financial Services. How can I assist you with your account or connection today?"

        self.sessions[session_id].append({"role": "agent", "text": reply})
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        logger.info(json.dumps({
            "event": "gecx_agent_turn",
            "session_id": session_id,
            "latency_ms": round(latency_ms, 2),
            "tools_executed": tools_executed,
            "rag_articles_matched": len(rag_articles)
        }))
        
        return {
            "session_id": session_id,
            "reply": reply,
            "latency_ms": round(latency_ms, 2),
            "tools_executed": tools_executed
        }
