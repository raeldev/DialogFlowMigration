import pytest
from services.knowledge.in_memory_repository import InMemoryKnowledgeRepository
from services.agent.gecx_agent_service import GECXAgentService

class MockLLMResponse:
    def __init__(self, text, function_calls=None):
        self.text = text
        self.function_calls = function_calls or []

class MockModels:
    def generate_content(self, model, contents, config):
        return MockLLMResponse(
            text="I have checked your bill. Everything is paid.",
            function_calls=[]
        )

class MockClient:
    def __init__(self):
        self.models = MockModels()

def test_agent_process_message_with_mock_llm():
    repo = InMemoryKnowledgeRepository()
    mock_client = MockClient()
    agent = GECXAgentService(knowledge_provider=repo, llm_client=mock_client)
    
    response = agent.process_message(session_id="SESS-101", user_message="Check my billing invoice")
    assert response["session_id"] == "SESS-101"
    assert "paid" in response["reply"].lower()
    assert response["latency_ms"] >= 0.0

def test_agent_process_message_fallback_local():
    repo = InMemoryKnowledgeRepository()
    # Passing no llm_client and letting fallback trigger if API key is invalid/mock
    agent = GECXAgentService(knowledge_provider=repo, llm_client=None)
    agent.client = None # Force local fallback
    
    response = agent.process_message(session_id="SESS-102", user_message="My wifi internet is slow")
    assert "get_invoice_status" in response["tools_executed"] or "run_network_diagnostic" in response["tools_executed"]
    assert response["latency_ms"] >= 0.0
