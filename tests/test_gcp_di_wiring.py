import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.main import app
from services.knowledge.in_memory_repository import InMemoryKnowledgeRepository
from services.knowledge.vertex_ai_repository import VertexAISearchRepository

def test_di_wiring_default_local(monkeypatch):
    monkeypatch.setenv("USE_REAL_GCP", "false")
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert isinstance(app.state.knowledge_provider, InMemoryKnowledgeRepository)

@patch("api.main.setup_gcp_telemetry")
@patch("services.knowledge.vertex_ai_repository.VertexAISearchRepository.__init__", return_value=None)
def test_di_wiring_real_gcp(mock_repo_init, mock_setup_telemetry, monkeypatch):
    monkeypatch.setenv("USE_REAL_GCP", "true")
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert isinstance(app.state.knowledge_provider, VertexAISearchRepository)
        mock_setup_telemetry.assert_called_once()
