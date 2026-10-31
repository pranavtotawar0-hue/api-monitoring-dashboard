from types import SimpleNamespace

import httpx
import pytest

from monitor import check_endpoint, generate_summary, get_latency_status


def test_successful_response(monkeypatch):
    def fake_get(url, timeout):
        return SimpleNamespace(
            status_code=200,
            is_success=True,
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    result = check_endpoint("https://example.com/health")

    assert result["status_code"] == 200
    assert result["success"] is True
    assert result["error"] is None
    assert result["latency_status"] in ["Normal", "Slow"]


def test_server_error(monkeypatch):
    def fake_get(url, timeout):
        return SimpleNamespace(
            status_code=500,
            is_success=False,
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    result = check_endpoint("https://example.com/health")

    assert result["status_code"] == 500
    assert result["success"] is False
    assert result["error"] is None


def test_empty_url():
    with pytest.raises(ValueError):
        check_endpoint("")


def test_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.TimeoutException("Request timed out")

    monkeypatch.setattr(httpx, "get", fake_get)

    result = check_endpoint("https://example.com/health")

    assert result["status_code"] is None
    assert result["success"] is False
    assert result["error"] == "Timeout"
    assert result["latency_status"] in ["Normal", "Slow"]

def test_connection_error(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.ConnectError("Connection failed")

    monkeypatch.setattr(httpx, "get", fake_get)

    result = check_endpoint("https://example.com/health")

    assert result["status_code"] is None
    assert result["success"] is False
    assert result["error"] == "ConnectError"

def test_generate_summary():
    results = [
        {"success": True, "latency_ms": 100},
        {"success": False, "latency_ms": 200},
        {"success": True, "latency_ms": 300}
    ]

    summary = generate_summary(results)

    assert summary["total"] == 3
    assert summary["successful"] == 2
    assert summary["failed"] == 1
    assert summary["success_rate"] == 66.67
    assert summary["average_latency_ms"] == 200.0
    assert summary["minimum_latency_ms"] == 100
    assert summary["maximum_latency_ms"] == 300
    assert summary["p95_latency_ms"] == 300


def test_generate_summary_all_failed():
    results = [
        {"success": False, "latency_ms": 100},
        {"success": False, "latency_ms": 200}
    ]

    summary = generate_summary(results)

    assert summary["total"] == 2
    assert summary["successful"] == 0
    assert summary["failed"] == 2
    assert summary["success_rate"] == 0
    assert summary["average_latency_ms"] == 150.0
    assert summary["minimum_latency_ms"] == 100
    assert summary["maximum_latency_ms"] == 200
    assert summary["p95_latency_ms"] == 200

def test_generate_summary_empty():
    results = []

    summary = generate_summary(results)

    assert summary["total"] == 0
    assert summary["successful"] == 0
    assert summary["failed"] == 0
    assert summary["success_rate"] == 0
    assert summary["minimum_latency_ms"] == 0
    assert summary["maximum_latency_ms"] == 0 
    assert summary["average_latency_ms"] == 0
    assert summary["p95_latency_ms"] == 0  

def test_generate_summary_average_latency():
    results = [
        {"success": True, "latency_ms": 50},
        {"success": True, "latency_ms": 150},
        {"success": False, "latency_ms": 250},
        {"success": True, "latency_ms": 350}
    ]

    summary = generate_summary(results)

    assert summary["average_latency_ms"] == 200.0 

def test_latency_status_normal():
    assert get_latency_status(1000) == "Normal"


def test_latency_status_at_threshold():
    assert get_latency_status(1500) == "Normal"


def test_latency_status_slow():
    assert get_latency_status(2000) == "Slow"

def test_p95_with_unsorted_latencies():
    results = [
        {"success": True, "latency_ms": 300},
        {"success": True, "latency_ms": 100},
        {"success": False, "latency_ms": 200}
    ]

    summary = generate_summary(results)

    assert summary["p95_latency_ms"] == 300