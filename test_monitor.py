from types import SimpleNamespace

import httpx
import pytest

from monitor import check_endpoint


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

def test_connection_error(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.ConnectError("Connection failed")

    monkeypatch.setattr(httpx, "get", fake_get)

    result = check_endpoint("https://example.com/health")

    assert result["status_code"] is None
    assert result["success"] is False
    assert result["error"] == "ConnectError"