"""Колектор активних шкідливих URL із URLhaus."""
import logging
import os
from datetime import datetime

import requests

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

URLHAUS_RECENT_URL = "https://urlhaus-api.abuse.ch/v2/files/exports/{auth_key}/recent.json"


class URLhausCollector(BaseCollector):
    source_name = "URLhaus"

    def fetch(self) -> list[Threat]:
        auth_key = os.getenv("ABUSECH_AUTH_KEY")
        if not auth_key:
            logger.warning("ABUSECH_AUTH_KEY не задано — URLhaus пропущено")
            return []

        try:
            response = requests.get(
                URLHAUS_RECENT_URL.format(auth_key=auth_key),
                timeout=30,
                headers={"User-Agent": "UA-Cyber-Dashboard"},
            )
            response.raise_for_status()
            records = response.json()
        except (requests.RequestException, ValueError) as error:
            logger.error("URLhaus недоступний: %s", error)
            return []

        threats: list[Threat] = []
        for record in records[:200]:
            url = record.get("url")
            url_id = str(record.get("id") or url or "")
            if not url or not url_id:
                continue
            date_added = record.get("dateadded")
            try:
                published = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S")
            except (TypeError, ValueError):
                published = datetime.utcnow()

            threats.append(
                Threat(
                    external_id=f"urlhaus-{url_id}",
                    title=f"Malware URL: {record.get('host') or url}",
                    source=self.source_name,
                    type=ThreatType.ioc,
                    severity=Severity.high,
                    region=Region.world,
                    published=published,
                    summary=f"Статус: {record.get('url_status', 'unknown')}; malware: {record.get('threat', 'unknown')}",
                    tags=["URLhaus", record.get("url_status", "unknown"), record.get("threat", "unknown")],
                    url=url,
                )
            )
        logger.info("URLhaus: %d шкідливих URL", len(threats))
        return threats
