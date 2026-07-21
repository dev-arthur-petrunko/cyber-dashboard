from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.db import ThreatORM, get_session, init_db
from app.timeline import build_timeline

app = FastAPI(
    title="UA Cyber Threat Dashboard API",
    description="Агрегатор угроз кибербезопасности для Украины",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # сузить до домена фронтенда перед продакшеном
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": "UA Cyber Threat Dashboard API",
        "docs": "/docs",
        "endpoints": ["/health", "/stats", "/threats", "/threats/{id}"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/threats")
def list_threats(
    db: Session = Depends(get_session),
    source: Optional[str] = None,
    severity: Optional[str] = None,
    region: Optional[str] = Query(default=None, description="UA | World"),
    type: Optional[str] = None,
    days: int = Query(default=30, le=365),
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    q = db.query(ThreatORM).filter(
        ThreatORM.published >= datetime.utcnow() - timedelta(days=days)
    )
    if source:
        q = q.filter(ThreatORM.source == source)
    if severity:
        q = q.filter(ThreatORM.severity == severity)
    if region:
        q = q.filter(ThreatORM.region == region)
    if type:
        q = q.filter(ThreatORM.type == type)

    total = q.count()
    rows = (
        q.order_by(ThreatORM.published.desc()).offset(offset).limit(limit).all()
    )
    return {
        "total": total,
        "items": [_serialize(r) for r in rows],
    }


@app.get("/timeline/{cve_id}")
def get_timeline(cve_id: str, db: Session = Depends(get_session)):
    return build_timeline(db, cve_id)


@app.get("/threats/{threat_id}")
def get_threat(threat_id: int, db: Session = Depends(get_session)):
    row = db.query(ThreatORM).filter(ThreatORM.id == threat_id).first()
    if not row:
        return {"error": "not found"}
    return _serialize(row)


@app.get("/stats")
def stats(db: Session = Depends(get_session), region: Optional[str] = None):
    last_24h = datetime.utcnow() - timedelta(hours=24)

    base = db.query(ThreatORM)
    if region:
        base = base.filter(ThreatORM.region == region)

    total = base.count()
    critical = base.filter(ThreatORM.severity == "Critical").count()
    new_24h = base.filter(ThreatORM.published >= last_24h).count()
    active_exploits = base.filter(
        ThreatORM.exploit_maturity.in_(["Weaponized", "In the wild"])
    ).count()
    ua_alerts = base.filter(ThreatORM.region == "UA").count()
    high_epss = base.filter(ThreatORM.epss_score >= 0.5).count()

    # For UA region (news-type threats without CVEs), use severity-based risk
    # For World/All, use EPSS-based risk
    if region == "UA" or (total > 0 and high_epss == 0):
        high_severity = base.filter(
            ThreatORM.severity.in_(["Critical", "High"])
        ).count()
        risk_value = high_severity
        risk_label = "High/Critical"
    else:
        risk_value = high_epss
        risk_label = "EPSS risk"

    # Use vendor when available, fall back to source for news-type threats
    vendor_or_source = case(
        (ThreatORM.vendor.isnot(None), ThreatORM.vendor),
        else_=ThreatORM.source,
    ).label("vendor_or_source")

    top_vendors = (
        base.with_entities(vendor_or_source, func.count(ThreatORM.id).label("count"))
        .group_by(vendor_or_source)
        .order_by(func.count(ThreatORM.id).desc())
        .limit(5)
        .all()
    )

    by_source = (
        base.with_entities(ThreatORM.source, func.count(ThreatORM.id).label("count"))
        .group_by(ThreatORM.source)
        .order_by(func.count(ThreatORM.id).desc())
        .all()
    )

    last_update = db.query(func.max(ThreatORM.fetched_at)).scalar()

    return {
        "critical_threats": critical,
        "active_exploits": active_exploits,
        "new_cve_24h": new_24h,
        "ua_alerts": ua_alerts,
        "high_epss_risk": risk_value,
        "risk_label": risk_label,
        "top_vendors": [{"vendor": v, "count": c} for v, c in top_vendors],
        "by_source": [{"source": s, "count": c} for s, c in by_source],
        "total_threats": total,
        "last_update": last_update,
    }


def _serialize(row: ThreatORM) -> dict:
    return {
        "id": row.id,
        "external_id": row.external_id,
        "title": row.title,
        "source": row.source,
        "type": row.type,
        "severity": row.severity,
        "country": row.country,
        "region": row.region,
        "vendor": row.vendor,
        "products": row.products,
        "published": row.published,
        "tags": row.tags,
        "summary": row.summary,
        "url": row.url,
        "cve_id": row.cve_id,
        "cvss_score": row.cvss_score,
        "epss_score": row.epss_score,
        "exploit_maturity": row.exploit_maturity,
    }
