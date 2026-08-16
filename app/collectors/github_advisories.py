"""Колектор глобальних перевірених advisory з GitHub Advisory Database."""
import logging
from datetime import datetime, timedelta, timezone

import requests

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

GITHUB_ADVISORIES_URL = "https://api.github.com/advisories"


def _severity(value: str | None) -> Severity:
    return {
        "critical": Severity.critical,
        "high": Severity.high,
        "medium": Severity.medium,
        "low": Severity.low,
    }.get((value or "").lower(), Severity.unknown)


class GitHubAdvisoriesCollector(BaseCollector):
    source_name = "GitHub Advisory Database"

    def __init__(self, lookback_days: int = 7) -> None:
        self.lookback_days = lookback_days

    def fetch(self) -> list[Threat]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
        try:
            response = requests.get(
                GITHUB_ADVISORIES_URL,
                params={"per_page": 100, "sort": "published", "direction": "desc"},
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2026-03-10",
                    "User-Agent": "UA-Cyber-Dashboard",
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            logger.error("GitHub Advisory Database недоступна: %s", error)
            return []

        threats: list[Threat] = []
        for advisory in response.json():
            published_raw = advisory.get("published_at")
            if not published_raw:
                continue
            try:
                published = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
            except ValueError:
                continue
            if published < cutoff:
                continue

            vulnerabilities = advisory.get("vulnerabilities") or []
            packages = [
                f"{item.get('package', {}).get('ecosystem')}:{item.get('package', {}).get('name')}"
                for item in vulnerabilities[:6]
                if item.get("package", {}).get("name")
            ]
            cve_id = advisory.get("cve_id")
            cvss = (advisory.get("cvss") or {}).get("score")
            # GitHub API отдаёт epss.percentage в шкале 0–100, а модель Threat
            # хранит вероятность 0–1 — приводим к единому диапазону.
            epss_raw = (advisory.get("epss") or {}).get("percentage")
            epss = (epss_raw / 100.0) if isinstance(epss_raw, (int, float)) else None
            ghsa_id = advisory.get("ghsa_id")
            if not ghsa_id:
                continue

            threats.append(
                Threat(
                    external_id=ghsa_id,
                    title=advisory.get("summary") or ghsa_id,
                    source=self.source_name,
                    type=ThreatType.cve,
                    severity=_severity(advisory.get("severity")),
                    region=Region.world,
                    vendor="GitHub",
                    products=packages,
                    cvss_score=cvss,
                    epss_score=epss,
                    published=published,
                    summary=(advisory.get("description") or "")[:1000],
                    tags=["GHSA", *( [cve_id] if cve_id else [] )],
                    url=advisory.get("html_url"),
                    cve_id=cve_id,
                )
            )

        logger.info("GitHub Advisory Database: %d нових advisory", len(threats))
        return threats
