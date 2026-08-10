"""Тести для app/timeline.py — Cyber Timeline для одного CVE."""
from datetime import datetime, timedelta

from app.db import ThreatORM
from app.models.threat import ExploitMaturity, Severity, Threat, ThreatType
from app.storage import bulk_upsert
from app.timeline import build_timeline, _event_type, _event_date

from tests.conftest import _default_threat


def _cve_threat(external_id, source, published, maturity="Unknown", cve="CVE-2026-2001"):
    return _default_threat(
        external_id=external_id,
        source=source,
        cve_id=cve,
        published=published,
        exploit_maturity=maturity,
        title=f"{cve}: sample",
    )


def test_unknown_cve_returns_not_found(db_session):
    result = build_timeline(db_session, "CVE-2099-9999")
    assert result["found"] is False
    assert result["events"] == []


def test_timeline_orders_events_by_date(db_session):
    base = datetime(2026, 2, 1, 10, 0, 0)
    threats = [
        _cve_threat("nvd", "NVD", base),
        _cve_threat("gh", "GitHub", base + timedelta(days=1), maturity="PoC"),
        _cve_threat("kev", "CISA KEV", base + timedelta(days=5), maturity="In the wild"),
    ]
    bulk_upsert(db_session, threats)

    result = build_timeline(db_session, "CVE-2026-2001")
    assert result["found"] is True
    types = [e["type"] for e in result["events"]]
    assert types == ["published", "poc", "kev"]
    assert result["days_to_poc"] == 1
    assert result["days_to_kev"] == 5


def test_critical_verdict_for_fast_kev(db_session):
    base = datetime(2026, 2, 1, 10, 0, 0)
    bulk_upsert(
        db_session,
        [
            _cve_threat("nvd", "NVD", base),
            _cve_threat("kev", "CISA KEV", base + timedelta(hours=6), maturity="In the wild"),
        ],
    )
    result = build_timeline(db_session, "CVE-2026-2001")
    assert "Критична швидкість" in result["verdict"]


def test_slow_kev_verdict(db_session):
    base = datetime(2026, 2, 1, 10, 0, 0)
    bulk_upsert(
        db_session,
        [
            _cve_threat("nvd", "NVD", base),
            _cve_threat("kev", "CISA KEV", base + timedelta(days=30), maturity="In the wild"),
        ],
    )
    result = build_timeline(db_session, "CVE-2026-2001")
    assert "не миттєво" in result["verdict"]


def test_no_exploitation_verdict(db_session):
    base = datetime(2026, 2, 1, 10, 0, 0)
    bulk_upsert(db_session, [_cve_threat("nvd", "NVD", base)])
    result = build_timeline(db_session, "CVE-2026-2001")
    assert "Поки що немає" in result["verdict"]


def test_kev_date_prefers_added_to_kev(db_session):
    base = datetime(2026, 2, 1, 10, 0, 0)
    threats = [
        _cve_threat("nvd", "NVD", base),
        _cve_threat("kev", "CISA KEV", base + timedelta(days=3), maturity="In the wild"),
    ]
    threats[1] = threats[1].model_copy(
        update={"added_to_kev": base + timedelta(days=7)}
    )
    bulk_upsert(db_session, threats)
    result = build_timeline(db_session, "CVE-2026-2001")
    assert result["days_to_kev"] == 7


def test_cvss_and_epss_are_picked(db_session):
    base = datetime(2026, 2, 1, 10, 0, 0)
    threats = [
        _default_threat(
            external_id="nvd",
            source="NVD",
            cve_id="CVE-2026-2001",
            published=base,
            cvss_score=9.1,
            epss_score=0.9,
        ),
    ]
    bulk_upsert(db_session, threats)
    result = build_timeline(db_session, "CVE-2026-2001")
    assert result["cvss_score"] == 9.1
    assert result["epss_score"] == 0.9


def test_event_type_mapping():
    assert _event_type(ThreatORM(source="NVD")) == "published"
    assert _event_type(ThreatORM(source="GitHub")) == "poc"
    assert _event_type(ThreatORM(source="Exploit-DB")) == "weaponized"
    assert _event_type(ThreatORM(source="CISA KEV")) == "kev"
    assert _event_type(ThreatORM(source="CERT-UA")) == "advisory"
    assert _event_type(ThreatORM(source="BleepingComputer")) == "mention"


def test_event_date_prefers_added_to_kev_for_kev_rows():
    added = datetime(2026, 3, 1)
    published = datetime(2026, 2, 1)
    row = ThreatORM(source="CISA KEV", added_to_kev=added, published=published)
    assert _event_date(row) == added
