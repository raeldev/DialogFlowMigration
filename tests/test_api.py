from fastapi.testclient import TestClient
from api.main import app

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "gecx-agent-poc"}

def test_chat_endpoint_billing():
    with TestClient(app) as client:
        payload = {"session_id": "API-SESS-1", "user_message": "Check my billing invoice status"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "API-SESS-1"
        assert "reply" in data
        assert data["insights"]["detected_topic"] == "Billing & Payments"

def test_chat_endpoint_network():
    with TestClient(app) as client:
        payload = {"session_id": "API-SESS-2", "user_message": "My router wifi is blinking red light"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["insights"]["detected_topic"] == "Technical Support - Network"
