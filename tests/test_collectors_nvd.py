"""Тести для NVD-колектора з мокнутим HTTP."""
import requests

from app.collectors.nvd import NVDCollector


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


NVD_PAYLOAD = {
    "vulnerabilities": [
        {
            "cve": {
                "id": "CVE-2026-9999",
                "descriptions": [
                    {"lang": "en", "value": "A critical flaw in thing."},
                    {"lang": "es", "value": "Un fallo crítico."},
                ],
                "configurations": [
                    {
                        "nodes": [
                            {
                                "cpeMatch": [
                                    {"criteria": "cpe:2.3:a:microsoft:exchange_server:2026:*"}
                                ]
                            }
                        ]
                    }
                ],
                "metrics": {
                    "cvssMetricV31": [
                        {
                            "cvssData": {
                                "baseSeverity": "HIGH",
                                "baseScore": 8.1,
                            }
                        }
                    ]
                },
                "published": "2026-01-10T09:00:00.000",
            }
        },
        {"cve": {}},  # без id — пропускаємо
    ]
}


def test_fetch_parses_cve(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(NVD_PAYLOAD))
    threats = NVDCollector().fetch()
    assert len(threats) == 1


def test_fetch_normalizes_fields(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(NVD_PAYLOAD))
    threat = NVDCollector().fetch()[0]
    assert threat.external_id == "CVE-2026-9999"
    assert threat.cve_id == "CVE-2026-9999"
    assert threat.source == "NVD"
    assert threat.severity == "High"
    assert threat.cvss_score == 8.1
    assert threat.vendor == "microsoft"
    assert threat.products == ["exchange_server"]
    assert "critical flaw" in threat.summary
    assert threat.url == "https://nvd.nist.gov/vuln/detail/CVE-2026-9999"


def test_metrics_fallback_to_v2(monkeypatch):
    payload = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2026-1111",
                    "descriptions": [],
                    "metrics": {
                        "cvssMetricV2": [
                            {"cvssData": {"baseSeverity": "MEDIUM", "baseScore": 5.4}}
                        ]
                    },
                    "published": "2026-01-10T09:00:00.000",
                }
            }
        ]
    }
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(payload))
    threat = NVDCollector().fetch()[0]
    assert threat.severity == "Medium"
    assert threat.cvss_score == 5.4


def test_no_metrics_yields_unknown(monkeypatch):
    payload = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2026-2222",
                    "descriptions": [],
                    "metrics": {},
                    "published": "2026-01-10T09:00:00.000",
                }
            }
        ]
    }
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(payload))
    threat = NVDCollector().fetch()[0]
    assert threat.severity == "Unknown"
    assert threat.cvss_score is None


def test_request_failure_returns_empty(monkeypatch):
    def _boom(*a, **k):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", _boom)
    assert NVDCollector().fetch() == []


def test_products_deduplicated_and_limited(monkeypatch):
    payload = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2026-3333",
                    "descriptions": [],
                    "configurations": [
                        {
                            "nodes": [
                                {
                                    "cpeMatch": [
                                        {"criteria": "cpe:2.3:a:acme:app:1.0"},
                                        {"criteria": "cpe:2.3:a:acme:app:1.1"},
                                    ]
                                }
                            ]
                        }
                    ],
                    "metrics": {},
                    "published": "2026-01-10T09:00:00.000",
                }
            }
        ]
    }
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(payload))
    threat = NVDCollector().fetch()[0]
    assert threat.vendor == "acme"
    assert threat.products == ["app"]
