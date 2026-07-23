"""
Отправка сводки по итогам pipeline-запуска в n8n через webhook.
"""
import logging
import os
from datetime import datetime

import requests
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.db import ThreatORM

logger = logging.getLogger("notifications")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


def _build_stats(db: Session) -> dict:
    """Та же логика, что в /stats эндпоинте main.py, но как переиспользуемая функция."""
    base = db.query(ThreatORM)
    total = base.count()
    critical = base.filter(ThreatORM.severity == "Critical").count()
    active_exploits = base.filter(
        ThreatORM.exploit_maturity.in_(["Weaponized", "In the wild"])
    ).count()
    ua_alerts = base.filter(ThreatORM.region == "UA").count()
    high_epss = base.filter(ThreatORM.epss_score >= 0.5).count()

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

    return {
        "total_threats": total,
        "critical_threats": critical,
        "active_exploits": active_exploits,
        "ua_alerts": ua_alerts,
        "high_epss_risk": high_epss,
        "top_vendors": [{"vendor": v, "count": c} for v, c in top_vendors],
    }


def _serialize_new_threats(db: Session, run_start: datetime) -> list[dict]:
    """Все угрозы, добавленные/обновлённые именно в этом запуске pipeline."""
    rows = (
        db.query(ThreatORM)
        .filter(ThreatORM.fetched_at >= run_start)
        .order_by(ThreatORM.published.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "source": r.source,
            "severity": r.severity,
            "region": r.region,
            "cve_id": r.cve_id,
            "cvss_score": r.cvss_score,
            "epss_score": r.epss_score,
            "exploit_maturity": r.exploit_maturity,
            "url": r.url,
            "published": r.published.isoformat() if r.published else None,
        }
        for r in rows
    ]


def notify_n8n(db: Session, run_start: datetime, collectors_summary: dict) -> None:
    if not N8N_WEBHOOK_URL:
        logger.info("N8N_WEBHOOK_URL не задан — пропускаю отправку в n8n")
        return

    payload = {
        "run_at": run_start.isoformat(),
        "stats": _build_stats(db),
        "new_threats": _serialize_new_threats(db, run_start),
        "collectors_summary": collectors_summary,
    }

    try:
        resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
        resp.raise_for_status()
        logger.info("Отправлено в n8n: %s новых угроз", len(payload["new_threats"]))
    except Exception as e:
        logger.exception("Не удалось отправить данные в n8n: %s", e)
