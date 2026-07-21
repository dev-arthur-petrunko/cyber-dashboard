"""
Коллектор для NVD (National Vulnerability Database).
API docs: https://nvd.nist.gov/developers/vulnerabilities
Без API-ключа лимит ~5 запросов/30 сек — этого достаточно для 1 запуска в день/час.
С ключом (NVD_API_KEY в .env) лимит выше.
"""
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import datetime, timedelta, timezone

from typing import Optional

import requests

from app.collectors.base import BaseCollector
from app.models.threat import Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

CVSS_TO_SEVERITY = {
    "CRITICAL": Severity.critical,
    "HIGH": Severity.high,
    "MEDIUM": Severity.medium,
    "LOW": Severity.low,
}


class NVDCollector(BaseCollector):
    source_name = "NVD"

    def __init__(self, lookback_hours: int = 24):
        self.lookback_hours = lookback_hours
        self.api_key = os.getenv("NVD_API_KEY")

    def _severity_and_score(self, cve: dict) -> tuple[Severity, Optional[float]]:
        metrics = cve.get("metrics", {})
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if key in metrics and metrics[key]:
                cvss_data = metrics[key][0].get("cvssData", {})
                base_severity = cvss_data.get("baseSeverity") or metrics[key][0].get(
                    "baseSeverity"
                )
                base_score = cvss_data.get("baseScore")
                severity = CVSS_TO_SEVERITY.get(
                    (base_severity or "").upper(), Severity.unknown
                )
                return severity, base_score
        return Severity.unknown, None

    def fetch(self) -> list[Threat]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=self.lookback_hours)

        params = {
            "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "resultsPerPage": 200,
        }
        headers = {"apiKey": self.api_key} if self.api_key else {}

        def _do_request():
            return requests.get(NVD_API_URL, params=params, headers=headers, timeout=(10, 20))

        pool = ThreadPoolExecutor(max_workers=1)
        try:
            future = pool.submit(_do_request)
            resp = future.result(timeout=35)  # жёсткий предел на ВЕСЬ запрос
            resp.raise_for_status()
        except FutureTimeoutError:
            logger.error("NVD fetch timed out after 35s (hard limit) — skipping")
            return []
        except requests.RequestException as e:
            logger.error("NVD fetch failed: %s", e)
            return []
        finally:
            # wait=False: не блокируем скрипт, если поток всё ещё висит на медленном сокете —
            # процесс python завершится сам и заберёт поток с собой
            pool.shutdown(wait=False)

        data = resp.json()
        threats = []
        for item in data.get("vulnerabilities", []):
            cve = item.get("cve", {})
            cve_id = cve.get("id")
            if not cve_id:
                continue

            descriptions = cve.get("descriptions", [])
            summary = next(
                (d["value"] for d in descriptions if d.get("lang") == "en"), ""
            )

            vendor = None
            products = []
            for conf in cve.get("configurations", []):
                for node in conf.get("nodes", []):
                    for match in node.get("cpeMatch", []):
                        cpe = match.get("criteria", "")
                        parts = cpe.split(":")
                        if len(parts) > 4:
                            vendor = vendor or parts[3]
                            products.append(parts[4])

            severity, cvss_score = self._severity_and_score(cve)
            threats.append(
                Threat(
                    external_id=cve_id,
                    cve_id=cve_id,
                    title=cve_id,
                    source=self.source_name,
                    type=ThreatType.cve,
                    severity=severity,
                    cvss_score=cvss_score,
                    vendor=vendor,
                    products=list(set(products))[:10],
                    published=cve.get("published"),
                    summary=summary[:1000],
                    url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                )
            )
        return threats
