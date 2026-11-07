from fastapi.testclient import TestClient

from main import app, buscar_resposta

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_home_serves_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "Recruta Cidadão" in response.text

def test_faq_lookup():
    item = buscar_resposta("Quem deve se alistar?")
    assert item is not None
    assert "Serviço Militar" in item["resposta"]

def test_chat_faq_does_not_need_ai():
    response = client.post("/chat", json={"text": "Quem deve se alistar?"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "faq"
    assert data["response"]
