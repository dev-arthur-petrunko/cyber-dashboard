"""Інтеграційні тести API через TestClient (FastAPI)."""
from datetime import datetime, timedelta

from app.storage import bulk_upsert

from tests.conftest import _default_threat


def _seed_bundle(db_session):
    now = datetime.utcnow()
    threats = [
        _default_threat(
            external_id="CVE-2026-0001",
            title="Critical RCE in sharepoint",
            source="NVD",
            cve_id="CVE-2026-0001",
            severity="Critical",
            region="World",
            published=now - timedelta(days=1),
            cvss_score=9.8,
            epss_score=0.9,
            exploit_maturity="In the wild",
            tags=["exploit", "sharepoint"],
        ),
        _default_threat(
            external_id="CERT-UA-2026-001",
            title="Атака на державні установи",
            source="CERT-UA",
            type="News",
            severity="High",
            region="UA",
            published=now - timedelta(days=2),
            cve_id=None,
            exploit_maturity="Unknown",
            epss_score=None,
        ),
    ]
    bulk_upsert(db_session, threats)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_lists_endpoints(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "/stats" in response.json()["endpoints"]


def test_threats_empty_db(client):
    response = client.get("/threats")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_threats_returns_seeded(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/threats")
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_threats_filter_by_region(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/threats", params={"region": "UA"})
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["region"] == "UA"


def test_threats_filter_by_severity(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/threats", params={"severity": "Critical"})
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["severity"] == "Critical"


def test_threats_filter_by_source(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/threats", params={"source": "CERT-UA"})
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["source"] == "CERT-UA"


def test_threats_pagination(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/threats", params={"limit": 1})
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1


def test_threats_days_filter(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/threats", params={"days": 1})
    data = response.json()
    assert data["total"] == 0  # всі записи старіші за 1 день


def test_stats_shape(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/stats")
    data = response.json()
    assert data["total_threats"] == 2
    assert data["critical_threats"] == 1
    assert data["active_exploits"] == 1
    assert data["ua_alerts"] == 1
    assert data["high_epss_risk"] == 1
    assert data["last_update"] is not None


def test_stats_region_filter(client, db_session):
    _seed_bundle(db_session)
    response = client.get("/stats", params={"region": "UA"})
    data = response.json()
    assert data["total_threats"] == 1


def test_threat_detail_includes_explanation(client, db_session):
    _seed_bundle(db_session)
    threat_id = client.get("/threats").json()["items"][0]["id"]
    response = client.get(f"/threats/{threat_id}")
    data = response.json()
    assert "explanation" in data
    assert "recommendations" in data["explanation"]
    assert data["local_score"] is not None


def test_threat_detail_missing_returns_not_found(client):
    response = client.get("/threats/999999")
    assert response.status_code == 200
    assert response.json()["error"] == "not found"


def test_timeline_unknown_cve(client):
    response = client.get("/timeline/CVE-2099-9999")
    data = response.json()
    assert data["found"] is False


def test_threat_actors_returns_list(client):
    response = client.get("/threat-actors")
    assert response.status_code == 200
    assert "items" in response.json()
