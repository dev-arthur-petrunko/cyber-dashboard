"""Колектор активних шкідливих URL із URLhaus."""
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

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
            payload = response.json()
        except requests.RequestException as error:
            # Не логируем error целиком — requests часто включает в текст
            # исключения полный URL запроса, а значит и auth_key.
            status = getattr(getattr(error, "response", None), "status_code", "?")
            logger.error("URLhaus недоступний: HTTP %s", status)
            return []
        except ValueError:
            logger.error("URLhaus повернув невалідний JSON")
            return []

        # Дамп может прийти как голый список ИЛИ как {"query_status": ..., "urls": [...]}
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            # Реальний формат експорту URLhaus — dict з id-ключем і списком
            # записів: {"3898642": [ {url: ...}, ... ]}. Крім того підтримуємо
            # {"urls": [...]} / {"data": [...]}.
            records = payload.get("urls") or payload.get("data") or []
            if not records:
                records = [
                    record
                    for value in payload.values()
                    if isinstance(value, list)
                    for record in value
                ]
        else:
            logger.error("URLhaus: неочікуваний формат відповіді (%s)", type(payload).__name__)
            return []

        threats: list[Threat] = []
        for record in records[:200]:
            url = record.get("url")
            url_id = str(record.get("id") or url or "")
            if not url or not url_id:
                continue

            host = record.get("host") or urlparse(url).netloc or url

            date_added = (record.get("dateadded") or record.get("date_added") or "").replace(" UTC", "")
            try:
                published = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S")
            except (TypeError, ValueError):
                published = datetime.utcnow()

            threats.append(
                Threat(
                    external_id=f"urlhaus-{url_id}",
                    title=f"Malware URL: {host}",
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