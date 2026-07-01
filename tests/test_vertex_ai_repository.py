from unittest.mock import patch, MagicMock
from services.knowledge.vertex_ai_repository import VertexAISearchRepository

def test_search_articles_missing_config(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "")
    monkeypatch.setenv("GCP_DATA_STORE_ID", "")
    repo = VertexAISearchRepository()
    results = repo.search_articles("wifi issue")
    assert results == []

@patch("google.cloud.discoveryengine_v1.SearchServiceClient")
@patch("google.cloud.discoveryengine_v1.SearchRequest")
def test_search_articles_success(mock_request, mock_client_cls, monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "test-proj")
    monkeypatch.setenv("GCP_DATA_STORE_ID", "test-store")
    monkeypatch.setenv("GCP_RAG_TIMEOUT_SECONDS", "3.5")

    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.serving_config_path.return_value = "projects/test-proj/locations/global/dataStores/test-store/servingConfigs/default_serving_config"

    mock_doc = MagicMock()
    mock_doc.id = "doc-123"
    mock_doc.struct_data = {"title": "Router Guide", "content": "Reset router"}
    mock_res_item = MagicMock()
    mock_res_item.document = mock_doc

    mock_response = MagicMock()
    mock_response.results = [mock_res_item]
    mock_client.search.return_value = mock_response

    repo = VertexAISearchRepository("test-proj", "global", "test-store")
    results = repo.search_articles("router")

    assert len(results) == 1
    assert results[0] == {"id": "doc-123", "title": "Router Guide", "content": "Reset router"}
    mock_client.search.assert_called_once()
    _, kwargs = mock_client.search.call_args
    assert kwargs.get("timeout") == 3.5

@patch("google.cloud.discoveryengine_v1.SearchServiceClient")
def test_search_articles_exception_error_log(mock_client_cls, monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "test-proj")
    monkeypatch.setenv("GCP_DATA_STORE_ID", "test-store")

    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.search.side_effect = Exception("gRPC deadline exceeded")

    repo = VertexAISearchRepository("test-proj", "global", "test-store")
    results = repo.search_articles("billing")

    assert results == []
