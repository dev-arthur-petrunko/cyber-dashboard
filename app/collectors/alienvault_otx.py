"""
Коллектор pulses (отчетов/кампаний) из AlienVault OTX.
API: https://otx.alienvault.com/api/

Ищем пульсы по ключевым словам: Ukraine, UAC-0010, Sandworm, Gamaredon.
Бесплатный API-ключ: https://otx.alienvault.com/ → профиль → API key → OTX_API_KEY в .env.
Без ключа коллектор пропускается.
"""
import logging
import os
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

OTX_API_URL = "https://otx.alienvault.com/api/v1/search/pulses"
UKRAINE_QUERIES = ["Ukraine", "UAC-0010", "Sandworm", "Gamaredon"]


def _parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return datetime.utcnow()


class AlienVaultOTXCollector(BaseCollector):
    source_name = "AlienVault OTX"

    def fetch(self) -> list[Threat]:
        api_key = os.getenv("OTX_API_KEY")
        if not api_key:
            logger.warning(
                "OTX_API_KEY не задан в .env — AlienVault OTX пропущен. "
                "Получить бесплатный ключ: https://otx.alienvault.com/"
            )
            return []

        headers = {"X-OTX-API-KEY": api_key}
        threats: list[Threat] = []
        seen_ids: set[str] = set()

        for query in UKRAINE_QUERIES:
            try:
                resp = requests.get(
                    OTX_API_URL,
                    params={"q": query, "limit": 10},
                    headers=headers,
                    timeout=30,
                )
                resp.raise_for_status()
            except requests.RequestException as e:
                logger.error("OTX fetch failed for query %s: %s", query, e)
                continue

            data = resp.json()
            for pulse in data.get("results", []):
                pulse_id = pulse.get("id")
                if not pulse_id or pulse_id in seen_ids:
                    continue
                seen_ids.add(pulse_id)

                tags = pulse.get("tags") or []
                indicators = pulse.get("indicators") or []
                indicator_summary = ", ".join(
                    f"{i.get('type')}:{i.get('indicator')}" for i in indicators[:5]
                )

                threats.append(
                    Threat(
                        external_id=f"otx-{pulse_id}",
                        title=pulse.get("name", "Untitled pulse"),
                        source=self.source_name,
                        type=ThreatType.ioc,
                        severity=Severity.high,
                        region=Region.ua,
                        published=_parse_date(pulse.get("created")),
                        summary=(pulse.get("description", "")[:300] + (f" | IoCs: {indicator_summary}" if indicator_summary else ""))[:500],
                        tags=list(set(tags + [query, "Ukraine"]))[:8],
                        url=f"https://otx.alienvault.com/pulse/{pulse_id}/",
                    )
                )

        logger.info("AlienVault OTX fetched %s pulses", len(threats))
        return threats
