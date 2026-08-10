"""Общие фикстуры: изолированная SQLite-БД и тестовый клиент FastAPI."""
import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///./data/test_threats.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, ThreatORM, engine, init_db
from app.main import app
from app.models.threat import Region, Severity, Threat, ThreatType

TEST_APP_ID = "NVD"


def _default_threat(**overrides) -> Threat:
    from datetime import datetime, timedelta

    base = {
        "external_id": "CVE-2026-0001",
        "title": "Critical vulnerability in test software",
        "source": "NVD",
        "type": ThreatType.cve,
        "severity": Severity.critical,
        "region": Region.world,
        "published": datetime.utcnow() - timedelta(hours=6),
        "cve_id": "CVE-2026-0001",
        "cvss_score": 9.8,
        "epss_score": 0.75,
        "exploit_maturity": "In the wild",
        "summary": "Remote code execution in test software.",
        "url": "https://nvd.nist.gov/vuln/detail/CVE-2026-0001",
    }
    base.update(overrides)
    return Threat(**base)


@pytest.fixture(scope="session", autouse=True)
def _db_setup():
    init_db()
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_db(_db_setup):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db_session(_clean_db):
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def seed_threat(db_session):
    """Создаёт один тестовый Threat и возвращает его ORM-запись."""

    def _seed(threat: Threat | None = None):
        threat = threat or _default_threat()
        from app.storage import bulk_upsert

        bulk_upsert(db_session, [threat])
        return (
            db_session.query(ThreatORM)
            .filter(ThreatORM.source == threat.source)
            .first()
        )

    return _seed


@pytest.fixture()
def client(_db_setup):
    with TestClient(app) as c:
        yield c
