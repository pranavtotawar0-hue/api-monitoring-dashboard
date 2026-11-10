
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "project": "API Monitoring Dashboard"
    }
def test_monitor_endpoint(monkeypatch):

    def fake_check_endpoint(url):
        return {
            "url": url,
            "status_code": 200,
            "latency_ms": 100.0,
            "latency_status": "Normal",
            "success": True,
            "error": None
        }

    monkeypatch.setattr(
        "app.check_endpoint",
        fake_check_endpoint
    )

    response = client.post(
        "/monitor",
        json={"url": "https://example.com/health"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["status_code"] == 200

def test_monitor_invalid_url():
    response = client.post(
        "/monitor",
        json={"url": "hello"}
    )

    assert response.status_code == 422

def test_monitor_missing_url():
    response = client.post(
        "/monitor",
        json={}
    )

    assert response.status_code == 422