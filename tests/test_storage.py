"""Тести для app/storage.py — bulk_upsert з дедуплікацією."""
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.db import ThreatORM
from app.models.threat import Severity, Threat, ThreatType
from app.storage import bulk_upsert

from tests.conftest import _default_threat


def _threat(external_id, source="NVD", **overrides):
    return _default_threat(
        external_id=external_id,
        source=source,
        title=f"Threat {external_id}",
        cve_id=external_id if external_id.startswith("CVE-") else None,
        **overrides,
    )


def test_empty_list_returns_zero_counts(db_session):
    result = bulk_upsert(db_session, [])
    assert result == {
        "inserted": 0,
        "updated": 0,
        "skipped_duplicates": 0,
        "skipped_invalid": 0,
        "total": 0,
    }


def test_insert_new_threats(db_session):
    threats = [_threat("CVE-2026-1001"), _threat("CVE-2026-1002")]
    result = bulk_upsert(db_session, threats)
    assert result["inserted"] == 2
    assert db_session.query(ThreatORM).count() == 2


def test_duplicates_within_batch_are_skipped(db_session):
    threats = [_threat("CVE-2026-1001"), _threat("CVE-2026-1001")]
    result = bulk_upsert(db_session, threats)
    assert result["inserted"] == 1
    assert result["skipped_duplicates"] == 1


def test_same_external_id_different_source_is_unique(db_session):
    threats = [
        _threat("CVE-2026-1001", source="NVD"),
        _threat("CVE-2026-1001", source="CISA KEV"),
    ]
    result = bulk_upsert(db_session, threats)
    assert result["inserted"] == 2


def test_second_run_updates_instead_of_insert(db_session):
    bulk_upsert(db_session, [_threat("CVE-2026-1001", severity=Severity.medium)])
    result = bulk_upsert(db_session, [_threat("CVE-2026-1001", severity=Severity.high)])
    assert result["inserted"] == 0
    assert result["updated"] == 1
    row = db_session.query(ThreatORM).one()
    assert row.severity == "High"


def test_blank_external_id_is_skipped(db_session):
    threats = [_threat("  ")]
    result = bulk_upsert(db_session, threats)
    assert result["skipped_invalid"] == 1
    assert result["total"] == 0


def test_whitespace_in_external_id_is_stripped(db_session):
    bulk_upsert(db_session, [_threat("  CVE-2026-1001  ")])
    row = db_session.query(ThreatORM).one()
    assert row.external_id == "CVE-2026-1001"


def test_url_serialized_to_string(db_session):
    threats = [_threat("CVE-2026-1001")]
    bulk_upsert(db_session, threats)
    row = db_session.query(ThreatORM).one()
    assert isinstance(row.url, str)


def test_fetched_at_updated_on_every_run(db_session):
    bulk_upsert(db_session, [_threat("CVE-2026-1001")])
    first = db_session.query(ThreatORM).one().fetched_at
    bulk_upsert(db_session, [_threat("CVE-2026-1001")])
    second = db_session.query(ThreatORM).one().fetched_at
    assert second >= first


def test_invalid_threat_raises_validation_error(db_session):
    with pytest.raises(ValidationError):
        Threat(
            external_id="x",
            title="no published date",
            source="NVD",
            type=ThreatType.cve,
            severity=Severity.high,
        )
