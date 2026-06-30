from fastapi.testclient import TestClient
from services.simulator.dialogflow_legacy import DialogflowSimulator
from services.simulator.benchmarker import MigrationBenchmarker
from services.knowledge.in_memory_repository import InMemoryKnowledgeRepository
from services.agent.gecx_agent_service import GECXAgentService
from api.main import app

def test_dialogflow_simulator_matched():
    sim = DialogflowSimulator()
    res = sim.process_message("S-1", "I need to check my billing invoice")
    assert res["success"] is True
    assert res["matched_intent"] == "billing.invoice"

def test_dialogflow_simulator_unmatched():
    sim = DialogflowSimulator()
    res = sim.process_message("S-2", "Can you explain how solar flares affect satellites?")
    assert res["success"] is False
    assert res["matched_intent"] == "Default Fallback Intent"

def test_benchmarker_run():
    repo = InMemoryKnowledgeRepository()
    agent = GECXAgentService(knowledge_provider=repo, llm_client=None)
    agent.client = None # force local fallback
    bm = MigrationBenchmarker(gecx_agent=agent)
    res = bm.run_benchmark()
    assert "summary" in res
    assert res["summary"]["total_test_cases"] == 4
    assert res["summary"]["gecx_success_rate_pct"] > res["summary"]["dialogflow_success_rate_pct"]

def test_benchmark_api_endpoint():
    with TestClient(app) as client:
        resp = client.post("/simulate/benchmark")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["verdict"] != ""
