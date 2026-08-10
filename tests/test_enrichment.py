"""Тести для app/enrichment.py — EPSS enrichment."""
import requests

from app.db import ThreatORM
from app.enrichment import enrich_epss
from app.storage import bulk_upsert

from tests.conftest import _default_threat


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _seed_cves(db_session, *cve_ids):
    threats = [
        _default_threat(external_id=cve, cve_id=cve, title=f"test {cve}", epss_score=None)
        for cve in cve_ids
    ]
    bulk_upsert(db_session, threats)


def test_no_cves_returns_zero(db_session):
    assert enrich_epss(db_session) == 0


def test_updates_epss_scores(monkeypatch, db_session):
    _seed_cves(db_session, "CVE-2026-7001", "CVE-2026-7002")
    payload = {
        "data": [
            {"cve": "CVE-2026-7001", "epss": 0.91},
            {"cve": "CVE-2026-7002", "epss": 0.05},
        ]
    }
    import app.enrichment as enrichment_module

    monkeypatch.setattr(
        enrichment_module.requests, "get", lambda *a, **k: _FakeResponse(payload)
    )
    updated = enrich_epss(db_session)
    assert updated == 2
    scores = {
        r.cve_id: r.epss_score for r in db_session.query(ThreatORM).all()
    }
    assert scores["CVE-2026-7001"] == 0.91
    assert scores["CVE-2026-7002"] == 0.05


def test_skips_already_scored_cves(db_session):
    threat = _default_threat(
        external_id="CVE-2026-7001", cve_id="CVE-2026-7001", epss_score=0.5
    )
    bulk_upsert(db_session, [threat])
    assert enrich_epss(db_session) == 0


def test_request_failure_keeps_going(monkeypatch, db_session):
    _seed_cves(db_session, "CVE-2026-7001")

    def _boom(*a, **k):
        raise requests.RequestException("timeout")

    import app.enrichment as enrichment_module

    monkeypatch.setattr(enrichment_module.requests, "get", _boom)
    assert enrich_epss(db_session) == 0
