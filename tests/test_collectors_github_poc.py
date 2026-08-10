"""Тести для GitHub PoC-колектора з мокнутим HTTP."""
import requests

from app.collectors.github_poc import GitHubPoCCollector


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


REPO_PAYLOAD = {
    "items": [
        {
            "id": 100,
            "name": "CVE-2026-7777-exploit",
            "description": "Public PoC for CVE-2026-7777",
            "created_at": "2026-05-01T10:00:00Z",
            "html_url": "https://github.com/user/repo",
        },
        {
            "id": 101,
            "name": "no-cve-here",
            "description": "unrelated project",
            "created_at": "2026-05-01T10:00:00Z",
            "html_url": "https://github.com/user/other",
        },
    ]
}


def test_fetch_filters_repos_without_cve(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(REPO_PAYLOAD))
    threats = GitHubPoCCollector().fetch()
    assert len(threats) == 1


def test_fetch_normalizes_poc_fields(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(REPO_PAYLOAD))
    threat = GitHubPoCCollector().fetch()[0]
    assert threat.external_id == "gh-100"
    assert threat.cve_id == "CVE-2026-7777"
    assert threat.source == "GitHub"
    assert threat.type == "Exploit"
    assert threat.exploit_maturity == "PoC"
    assert threat.title == "PoC: CVE-2026-7777-exploit"
    assert threat.tags == ["poc", "CVE-2026-7777"]
    assert threat.url == "https://github.com/user/repo"


def test_uses_token_when_configured(monkeypatch):
    captured = {}

    def _capture(url, **kwargs):
        captured.update(kwargs)
        return _FakeResponse({"items": []})

    monkeypatch.setattr(requests, "get", _capture)
    collector = GitHubPoCCollector()
    collector.token = "secret-token"
    collector.fetch()
    assert captured["headers"]["Authorization"] == "Bearer secret-token"


def test_request_failure_returns_empty(monkeypatch):
    def _boom(*a, **k):
        raise requests.RequestException("rate limited")

    monkeypatch.setattr(requests, "get", _boom)
    assert GitHubPoCCollector().fetch() == []
