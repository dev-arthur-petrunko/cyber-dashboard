"""
Кураторські записи з data/curated_threats.json — ручно додані посилання та advisories.
"""
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

from app.collectors.base import BaseCollector
from app.models.threat import ExploitMaturity, Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

CURATED_PATH = Path(__file__).resolve().parents[2] / "data" / "curated_threats.json"


class CuratedCollector(BaseCollector):
    source_name = "Curated"

    def fetch(self) -> list[Threat]:
        if not CURATED_PATH.exists():
            logger.warning("Curated threats file not found: %s", CURATED_PATH)
            return []

        try:
            raw = json.loads(CURATED_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to read curated threats: %s", e)
            return []

        threats: list[Threat] = []
        for item in raw:
            url = item.get("url", "")
            if not url:
                continue

            external_id = item.get("external_id") or hashlib.sha256(url.encode()).hexdigest()[:20]

            try:
                published = datetime.fromisoformat(item["published"])
            except (KeyError, ValueError):
                published = datetime.utcnow()

            threats.append(
                Threat(
                    external_id=external_id,
                    title=item["title"],
                    source=item["source"],
                    type=ThreatType(item.get("type", "News")),
                    severity=Severity(item.get("severity", "High")),
                    country=item.get("country", []),
                    region=Region(item.get("region", "World")),
                    vendor=item.get("vendor"),
                    products=item.get("products", []),
                    published=published,
                    tags=item.get("tags", []),
                    summary=item.get("summary", ""),
                    url=url,
                    exploit_maturity=ExploitMaturity(item.get("exploit_maturity", "Unknown")),
                )
            )
        return threats
