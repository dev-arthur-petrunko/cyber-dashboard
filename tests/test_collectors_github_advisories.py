"""Тести для GitHub Advisory Database-колектора."""
from datetime import datetime, timedelta, timezone

import pytest
import requests

from app.collectors.github_advisories import GitHubAdvisoriesCollector


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def _recent_iso(days_ago: int = 1) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


ADVISORY = {
    "ghsa_id": "GHSA-aaaa-bbbb-cccc",
    "cve_id": "CVE-2026-1234",
    "summary": "Test advisory",
    "severity": "high",
    "published_at": _recent_iso(),
    "cvss": {"score": 8.8},
    "epss": {"percentage": 0.45, "percentile": 0.2},
    "vulnerabilities": [
        {
            "package": {"ecosystem": "npm", "name": "some-pkg"},
            "vulnerable_version_range": "<1.2.3",
        }
    ],
}


def test_epss_percentage_converted_to_0_1_scale(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse([ADVISORY])
    )
    threat = GitHubAdvisoriesCollector().fetch()[0]
    assert threat.epss_score == pytest.approx(0.0045)


def test_epss_missing_is_none(monkeypatch):
    payload = dict(ADVISORY, epss=None)
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse([payload])
    )
    threat = GitHubAdvisoriesCollector().fetch()[0]
    assert threat.epss_score is None


def test_fetch_normalizes_fields(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse([ADVISORY])
    )
    threat = GitHubAdvisoriesCollector().fetch()[0]
    assert threat.external_id == "GHSA-aaaa-bbbb-cccc"
    assert threat.cve_id == "CVE-2026-1234"
    assert threat.source == "GitHub Advisory Database"
    assert threat.type == "CVE"
    assert threat.severity == "High"
    assert threat.cvss_score == 8.8
    assert threat.products == ["npm:some-pkg"]


def test_old_advisories_are_dropped(monkeypatch):
    old = dict(ADVISORY, published_at=_recent_iso(days_ago=30))
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse([old])
    )
    assert GitHubAdvisoriesCollector(lookback_days=7).fetch() == []


def test_request_failure_returns_empty(monkeypatch):
    def _boom(*a, **k):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", _boom)
    assert GitHubAdvisoriesCollector().fetch() == []
