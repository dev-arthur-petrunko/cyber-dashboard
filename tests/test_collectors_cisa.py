"""Тести для CISA KEV-колектора з мокнутим HTTP."""
import requests

from app.collectors.cisa_kev import CISA_KEV_URL, CISAKEVCollector


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


KEV_PAYLOAD = {
    "vulnerabilities": [
        {
            "cveID": "CVE-2026-1234",
            "vulnerabilityName": "Test RCE",
            "vendorProject": "Acme",
            "product": "Widget",
            "dateAdded": "2026-07-01T00:00:00.000Z",
            "shortDescription": "Attacker can execute code remotely.",
            "knownRansomwareCampaignUse": "Known",
        },
        {
            "cveID": "CVE-2026-5678",
            "vulnerabilityName": "Test Bypass",
            "vendorProject": "BetaCorp",
            "product": "Thing",
            "dateAdded": "2026-07-02T00:00:00.000Z",
            "shortDescription": "Auth bypass.",
            "knownRansomwareCampaignUse": "Unknown",
        },
        {},  # без cveID — має бути пропущений
    ]
}


def test_fetch_returns_kev_threats(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse(KEV_PAYLOAD)
    )
    threats = CISAKEVCollector().fetch()
    assert len(threats) == 2


def test_fetch_normalizes_fields(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse(KEV_PAYLOAD)
    )
    threat = CISAKEVCollector().fetch()[0]
    assert threat.external_id == "CVE-2026-1234"
    assert threat.cve_id == "CVE-2026-1234"
    assert threat.source == "CISA KEV"
    assert threat.type == "CVE"
    assert threat.severity == "Critical"  # ransomware campaign Known
    assert threat.exploit_maturity == "In the wild"
    assert threat.vendor == "Acme"
    assert threat.products == ["Widget"]
    assert threat.tags == ["known-exploited", "ransomware"]


def test_high_severity_for_non_ransomware(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse(KEV_PAYLOAD)
    )
    threat = CISAKEVCollector().fetch()[1]
    assert threat.severity == "High"
    assert threat.tags == ["known-exploited"]


def test_empty_vulnerabilities(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse({"vulnerabilities": []})
    )
    assert CISAKEVCollector().fetch() == []


def test_request_failure_returns_empty(monkeypatch):
    def _boom(*a, **k):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", _boom)
    assert CISAKEVCollector().fetch() == []


def test_uses_expected_url(monkeypatch):
    captured = {}

    def _capture(url, **kwargs):
        captured["url"] = url
        return _FakeResponse({"vulnerabilities": []})

    monkeypatch.setattr(requests, "get", _capture)
    CISAKEVCollector().fetch()
    assert captured["url"] == CISA_KEV_URL
