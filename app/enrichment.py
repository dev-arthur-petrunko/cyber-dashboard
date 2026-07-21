"""
Обогащение существующих CVE-записей в БД EPSS-скором.
EPSS (Exploit Prediction Scoring System) — открытый API FIRST.org,
без ключа: https://api.first.org/epss/
Даёт вероятность (0-1) того, что уязвимость будет реально
проэксплуатирована в течение следующих 30 дней — дополняет статичный
CVSS "насколько это плохо" метрикой "насколько это вероятно прямо сейчас".
"""
import logging

import requests
from sqlalchemy.orm import Session

from app.db import ThreatORM

logger = logging.getLogger(__name__)

EPSS_API_URL = "https://api.first.org/data/v1/epss"
BATCH_SIZE = 100  # ограничение на длину query string


def enrich_epss(db: Session) -> int:
    cve_ids = [
        row[0]
        for row in db.query(ThreatORM.cve_id)
        .filter(ThreatORM.cve_id.isnot(None), ThreatORM.epss_score.is_(None))
        .distinct()
        .all()
    ]
    if not cve_ids:
        return 0

    updated = 0
    for i in range(0, len(cve_ids), BATCH_SIZE):
        batch = cve_ids[i : i + BATCH_SIZE]
        try:
            resp = requests.get(
                EPSS_API_URL,
                params={"cve": ",".join(batch)},
                headers={"User-Agent": "UA-Cyber-Dashboard/0.1 (+https://github.com)"},
                timeout=30,
            )
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.error("EPSS fetch/parse failed for batch: %s", e)
            continue

        for item in payload.get("data", []):
            cve_id = item.get("cve")
            score = float(item.get("epss", 0))
            db.query(ThreatORM).filter(ThreatORM.cve_id == cve_id).update(
                {"epss_score": score}
            )
            updated += 1

    db.commit()
    return updated
