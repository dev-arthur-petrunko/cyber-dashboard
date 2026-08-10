"""Тести моделі Threat — валідація та значення за замовчуванням."""
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.threat import Region, Severity, Threat, ThreatType


def _threat(**overrides):
    base = {
        "external_id": "X-1",
        "title": "test",
        "source": "NVD",
        "type": ThreatType.cve,
        "severity": Severity.high,
        "published": datetime(2026, 1, 1),
    }
    base.update(overrides)
    return Threat(**base)


def test_minimal_threat_has_defaults():
    threat = _threat()
    assert threat.region == Region.world
    assert threat.country == []
    assert threat.products == []
    assert threat.tags == []
    assert threat.summary == ""
    assert threat.url is None
    assert threat.exploit_maturity == "Unknown"
    assert threat.cvss_score is None
    assert threat.epss_score is None


def test_missing_external_id_raises():
    with pytest.raises(ValidationError):
        Threat(
            title="no id",
            source="NVD",
            type=ThreatType.cve,
            severity=Severity.high,
            published=datetime(2026, 1, 1),
        )


def test_missing_title_raises():
    with pytest.raises(ValidationError):
        Threat(
            external_id="X",
            source="NVD",
            type=ThreatType.cve,
            severity=Severity.high,
            published=datetime(2026, 1, 1),
        )


def test_enum_values_serialize_to_string():
    threat = _threat()
    dumped = threat.model_dump()
    assert dumped["type"] == "CVE"
    assert dumped["severity"] == "High"
    assert dumped["region"] == "World"


def test_region_accepts_ua_and_world():
    assert _threat(region=Region.ua).region == Region.ua
    assert _threat(region="UA").region == "UA"
    assert _threat(region="World").region == "World"


def test_invalid_region_raises():
    with pytest.raises(ValidationError):
        _threat(region="Mars")


def test_fetched_at_defaults_to_now():
    threat = _threat()
    assert isinstance(threat.fetched_at, datetime)
    assert threat.fetched_at.year == datetime.utcnow().year
