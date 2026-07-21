"""
Коллектор IOC (Indicators of Compromise) из ThreatFox (abuse.ch).

Формат first_seen от API: "2026-07-20 19:30:58 UTC" — обрезаем " UTC".

API: https://threatfox-api.abuse.ch/api/v1/  Docs: https://threatfox.abuse.ch/api/

С 2025 года abuse.ch требует бесплатный Auth-Key для всех своих API (раньше
можно было без ключа). Получить: https://auth.abuse.ch/ → зарегистрироваться →
сгенерировать API key → положить в .env как ABUSECH_AUTH_KEY.
Без ключа коллектор просто пропускается (не роняет весь пайплайн).
"""
import logging
import os
from datetime import datetime

import requests

from app.collectors.base import BaseCollector
from app.models.threat import Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

THREATFOX_API_URL = "https://threatfox-api.abuse.ch/api/v1/"


class ThreatFoxCollector(BaseCollector):
    source_name = "ThreatFox"

    def fetch(self) -> list[Threat]:
        auth_key = os.getenv("ABUSECH_AUTH_KEY")
        if not auth_key:
            logger.warning(
                "ABUSECH_AUTH_KEY не задан в .env — ThreatFox пропущен. "
                "Получить бесплатный ключ: https://auth.abuse.ch/"
            )
            return []

        try:
            resp = requests.post(
                THREATFOX_API_URL,
                json={"query": "get_iocs", "days": 1},
                headers={"Auth-Key": auth_key},
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("ThreatFox fetch failed: %s", e)
            return []

        data = resp.json()
        if data.get("query_status") != "ok":
            logger.warning("ThreatFox returned status: %s", data.get("query_status"))
            return []

        threats = []
        def _parse_first_seen(value):
            if not value:
                return datetime.utcnow()
            if isinstance(value, str):
                value = value.replace(" UTC", "").strip()
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        pass
            return datetime.utcnow()

        for ioc in data.get("data", []):
            ioc_id = str(ioc.get("id"))
            malware = ioc.get("malware_printable", "Unknown malware")
            ioc_value = ioc.get("ioc", "")
            ioc_type = ioc.get("ioc_type", "")

            # confidence_level (0-100) от abuse.ch -> грубая severity
            confidence = ioc.get("confidence_level", 0)
            severity = (
                Severity.critical if confidence >= 90 else
                Severity.high if confidence >= 70 else
                Severity.medium
            )

            threats.append(
                Threat(
                    external_id=ioc_id,
                    title=f"{malware}: {ioc_type} indicator",
                    source=self.source_name,
                    type=ThreatType.ioc,
                    severity=severity,
                    published=_parse_first_seen(ioc.get("first_seen")),
                    summary=f"{ioc_type}: {ioc_value} | malware: {malware}"[:500],
                    tags=(ioc.get("tags") or [])[:5],
                    url=f"https://threatfox.abuse.ch/ioc/{ioc_id}/",
                )
            )
        return threats
