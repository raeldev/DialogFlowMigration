import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from api.models import ChatRequest, ChatResponse, TurnInsight
from services.knowledge.in_memory_repository import InMemoryKnowledgeRepository
from services.agent.gecx_agent_service import GECXAgentService
from services.knowledge.vertex_ai_repository import VertexAISearchRepository
from services.telemetry.gcp_logger import setup_gcp_telemetry

logger = logging.getLogger("gecx.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    use_gcp = os.getenv("USE_REAL_GCP", "").lower() in ("true", "1", "yes")
    if use_gcp:
        setup_gcp_telemetry()
        knowledge_repo = VertexAISearchRepository()
    else:
        knowledge_repo = InMemoryKnowledgeRepository()
    
    agent_svc = GECXAgentService(knowledge_provider=knowledge_repo)
    app.state.knowledge_provider = knowledge_repo
    app.state.agent_service = agent_svc
    logger.info(json.dumps({"event": "startup", "status": "Dependencies initialized", "use_real_gcp": use_gcp}))
    yield
    logger.info(json.dumps({"event": "shutdown"}))

app = FastAPI(title="GECX Agent POC API", lifespan=lifespan)

def simulate_ccai_insights(user_message: str, tools_executed: list) -> TurnInsight:
    msg_lower = user_message.lower()
    if "angry" in msg_lower or "terrible" in msg_lower or "cancel" in msg_lower:
        sentiment_score = -0.7
        sentiment_mag = 0.8
    elif "thank" in msg_lower or "great" in msg_lower:
        sentiment_score = 0.8
        sentiment_mag = 0.6
    else:
        sentiment_score = 0.1
        sentiment_mag = 0.2
        
    if "invoice" in msg_lower or "bill" in msg_lower or "get_invoice_status" in tools_executed:
        topic = "Billing & Payments"
    elif "router" in msg_lower or "wifi" in msg_lower or "run_network_diagnostic" in tools_executed:
        topic = "Technical Support - Network"
    else:
        topic = "General Customer Service"
        
    insight = TurnInsight(
        sentiment_score=sentiment_score,
        sentiment_magnitude=sentiment_mag,
        detected_topic=topic
    )
    logger.info(json.dumps({
        "event": "ccai_insights_simulation",
        "topic": topic,
        "sentiment_score": sentiment_score,
        "sentiment_magnitude": sentiment_mag
    }))
    return insight

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, req: Request):
    agent_svc: GECXAgentService = req.app.state.agent_service
    result = agent_svc.process_message(request.session_id, request.user_message)
    
    insights = simulate_ccai_insights(request.user_message, result["tools_executed"])
    
    return ChatResponse(
        session_id=result["session_id"],
        reply=result["reply"],
        latency_ms=result["latency_ms"],
        tools_executed=result["tools_executed"],
        insights=insights
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "gecx-agent-poc"}

@app.post("/simulate/benchmark")
async def simulate_benchmark_endpoint(req: Request):
    from services.simulator.benchmarker import MigrationBenchmarker
    agent_svc: GECXAgentService = req.app.state.agent_service
    benchmarker = MigrationBenchmarker(gecx_agent=agent_svc)
    return benchmarker.run_benchmark()

