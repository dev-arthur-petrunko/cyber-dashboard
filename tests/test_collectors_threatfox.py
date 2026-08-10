"""Тести для ThreatFox колектора: auth-key поведінка та парсинг."""
import requests

from app.collectors.threatfox import ThreatFoxCollector


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _make_payload():
    return {
        "query_status": "ok",
        "data": [
            {
                "id": 42,
                "malware_printable": "QakBot",
                "ioc": "evil.example.com",
                "ioc_type": "domain",
                "confidence_level": 95,
                "first_seen": "2026-07-01 12:00:00 UTC",
                "tags": ["qakbot", "emotet"],
            },
            {
                "id": 43,
                "malware_printable": "CobaltStrike",
                "ioc": "1.2.3.4:80",
                "ioc_type": "ip:port",
                "confidence_level": 60,
                "first_seen": "2026-07-02 13:00:00 UTC",
                "tags": [],
            },
        ],
    }


def test_skips_when_no_auth_key(monkeypatch):
    monkeypatch.delenv("ABUSECH_AUTH_KEY", raising=False)
    assert ThreatFoxCollector().fetch() == []


def test_fetch_parses_iocs(monkeypatch):
    monkeypatch.setenv("ABUSECH_AUTH_KEY", "test-key")
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResponse(_make_payload()))
    threats = ThreatFoxCollector().fetch()
    assert len(threats) == 2


def test_severity_from_confidence(monkeypatch):
    monkeypatch.setenv("ABUSECH_AUTH_KEY", "test-key")
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResponse(_make_payload()))
    threats = ThreatFoxCollector().fetch()
    assert threats[0].severity == "Critical"  # 95
    assert threats[1].severity == "Medium"  # 60


def test_normalized_fields(monkeypatch):
    monkeypatch.setenv("ABUSECH_AUTH_KEY", "test-key")
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResponse(_make_payload()))
    threat = ThreatFoxCollector().fetch()[0]
    assert threat.external_id == "42"
    assert threat.source == "ThreatFox"
    assert threat.type == "IOC"
    assert threat.title == "QakBot: domain — evil.example.com"
    assert threat.url == "https://threatfox.abuse.ch/ioc/42/"
    assert threat.tags == ["qakbot", "emotet"]


def test_first_seen_utc_suffix_stripped(monkeypatch):
    monkeypatch.setenv("ABUSECH_AUTH_KEY", "test-key")
    monkeypatch.setattr(requests, "post", lambda *a, **k: _FakeResponse(_make_payload()))
    threat = ThreatFoxCollector().fetch()[0]
    assert threat.published.year == 2026
    assert threat.published.hour == 12


def test_non_ok_status_returns_empty(monkeypatch):
    monkeypatch.setenv("ABUSECH_AUTH_KEY", "test-key")
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: _FakeResponse({"query_status": "no_result"})
    )
    assert ThreatFoxCollector().fetch() == []


def test_request_failure_returns_empty(monkeypatch):
    monkeypatch.setenv("ABUSECH_AUTH_KEY", "test-key")

    def _boom(*a, **k):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "post", _boom)
    assert ThreatFoxCollector().fetch() == []
