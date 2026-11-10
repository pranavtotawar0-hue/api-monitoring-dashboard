
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


def test_monitor_batch_endpoint(monkeypatch):

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
        "/monitor/batch",
        json={
            "urls": [
                "https://example.com",
                "https://httpbin.org/get"
            ]
        }
    )

    assert response.status_code == 200
    assert response.json()["summary"]["total"] == 2
    assert response.json()["summary"]["successful"] == 2
    assert response.json()["summary"]["failed"] == 0
    assert len(response.json()["results"]) == 2

def test_monitor_batch_mixed_results(monkeypatch):

    call_count = 0

    def fake_check_endpoint(url):
        nonlocal call_count
        call_count += 1

        if call_count == 2:
            return {
                "url": url,
                "status_code": 500,
                "latency_ms": 200.0,
                "latency_status": "Normal",
                "success": False,
                "error": None
            }

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
        "/monitor/batch",
        json={
            "urls": [
                "https://example.com",
                "https://httpbin.org/get",
                "https://httpbin.org/status/500"
            ]
        }
    )

    assert response.status_code == 200
    assert response.json()["summary"]["total"] == 3
    assert response.json()["summary"]["successful"] == 2
    assert response.json()["summary"]["failed"] == 1
    assert response.json()["summary"]["success_rate"] == 66.67

def test_monitor_batch_empty_urls():
    response = client.post(
        "/monitor/batch",
        json={"urls": []}
    )

    assert response.status_code == 422

def test_monitor_batch_invalid_url():
    response = client.post(
        "/monitor/batch",
        json={
            "urls": [
                "https://example.com",
                "hello",
                "https://httpbin.org/get"
            ]
        }
    )

    assert response.status_code == 422