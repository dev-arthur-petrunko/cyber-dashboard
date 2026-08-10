"""Тести для app/http_utils.py — жорсткий таймаут через окремий потік."""
import time

import pytest
import requests

from app.http_utils import hard_timeout_get


def test_returns_response_quickly(monkeypatch):
    class _FakeResponse:
        pass

    captured = {}

    def _fake_get(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return _FakeResponse()

    monkeypatch.setattr(requests, "get", _fake_get)
    result = hard_timeout_get("https://example.com", hard_timeout=5, params={"q": "x"})
    assert isinstance(result, _FakeResponse)
    assert captured["url"] == "https://example.com"
    assert captured["kwargs"]["params"] == {"q": "x"}


def test_raises_timeout_when_slow(monkeypatch):
    def _slow_get(*a, **k):
        time.sleep(2)
        return "done"

    monkeypatch.setattr(requests, "get", _slow_get)
    with pytest.raises(requests.exceptions.Timeout):
        hard_timeout_get("https://example.com", hard_timeout=0.1)


def test_propagates_request_exceptions(monkeypatch):
    def _boom(*a, **k):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(requests, "get", _boom)
    with pytest.raises(requests.ConnectionError):
        hard_timeout_get("https://example.com", hard_timeout=5)
