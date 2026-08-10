"""Тести для app/explanation.py — пояснення та рекомендації."""
from app.explanation import generate_explanation
from app.models.threat import ExploitMaturity, Severity, Threat, ThreatType

from tests.conftest import _default_threat


def _threat(**overrides):
    return _default_threat(**overrides)


def test_cve_explanation():
    threat = _threat(type=ThreatType.cve, cve_id="CVE-2026-1234", cvss_score=9.8)
    result = generate_explanation(threat)
    assert "CVE-2026-1234" in result["explanation"]
    assert "9.8" in result["explanation"]
    assert result["recommendations"]
    assert len(result["recommendations"]) <= 5


def test_exploit_explanation():
    threat = _threat(
        type=ThreatType.exploit,
        cve_id="CVE-2026-1234",
        exploit_maturity=ExploitMaturity.poc,
    )
    result = generate_explanation(threat)
    assert "Експлойт" in result["explanation"]


def test_poc_without_exploit_type_mentions_poc():
    threat = _threat(
        type=ThreatType.cve,
        cve_id="CVE-2026-1234",
        exploit_maturity=ExploitMaturity.poc,
    )
    result = generate_explanation(threat)
    assert "Proof-of-Concept" in result["explanation"]


def test_ioc_explanation_by_source():
    for source, needle in (
        ("ThreatFox", "ThreatFox"),
        ("MalwareBazaar", "MalwareBazaar"),
        ("AlienVault OTX", "AlienVault OTX"),
        ("Other", "компрометації"),
    ):
        threat = _threat(type=ThreatType.ioc, source=source, cve_id=None)
        result = generate_explanation(threat)
        assert needle in result["explanation"]


def test_ioc_domain_recommendations():
    threat = _threat(
        type=ThreatType.ioc, source="ThreatFox", summary="domain: evil.example.com"
    )
    result = generate_explanation(threat)
    joined = " ".join(result["recommendations"]).lower()
    assert "домен" in joined


def test_cert_ua_news_explanation():
    threat = _threat(type=ThreatType.news, source="CERT-UA", cve_id=None)
    result = generate_explanation(threat)
    assert "CERT-UA" in result["explanation"]


def test_critical_risk_text():
    threat = _threat(severity=Severity.critical)
    result = generate_explanation(threat)
    assert "Критичний ризик" in result["risk"]


def test_unknown_risk_text():
    threat = _threat(severity=Severity.unknown)
    result = generate_explanation(threat)
    assert "не визначено" in result["risk"]


def test_cisa_kev_recommendations():
    threat = _threat(type=ThreatType.advisory, source="CISA KEV", cve_id=None)
    result = generate_explanation(threat)
    joined = " ".join(result["recommendations"]).lower()
    assert "cisa" in joined
