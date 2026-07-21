"""
Коллектор публичных PoC-репозиториев на GitHub для последних CVE.
Использует GitHub Code/Repo Search API (без токена: 10 запросов/мин,
с GITHUB_TOKEN в .env — 30/мин).

Стратегия: ищем репозитории, где в названии/описании упоминается CVE-ID
за последние N дней. Если репозиторий появился раньше, чем через несколько
дней после публикации CVE — это готовый эксплойт, а не просто анализ.
"""
import logging
import os
import re
from datetime import datetime, timedelta, timezone

import requests

from app.collectors.base import BaseCollector
from app.models.threat import ExploitMaturity, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.I)


class GitHubPoCCollector(BaseCollector):
    source_name = "GitHub"

    def __init__(self, lookback_days: int = 7, max_results: int = 50):
        self.lookback_days = lookback_days
        self.max_results = max_results
        self.token = os.getenv("GITHUB_TOKEN")

    def fetch(self) -> list[Threat]:
        since = (datetime.now(timezone.utc) - timedelta(days=self.lookback_days)).strftime(
            "%Y-%m-%d"
        )
        # ищем репозитории с CVE в названии, созданные недавно —
        # характерный паттерн для PoC-репозиториев
        query = f"CVE-20 in:name created:>={since}"
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            resp = requests.get(
                GITHUB_SEARCH_URL,
                params={
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": self.max_results,
                },
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("GitHub PoC fetch failed: %s", e)
            return []

        data = resp.json()
        threats = []
        for repo in data.get("items", []):
            match = CVE_PATTERN.search(repo.get("name", "") + " " + (repo.get("description") or ""))
            if not match:
                continue
            cve_id = match.group(0).upper()

            threats.append(
                Threat(
                    external_id=f"gh-{repo['id']}",
                    cve_id=cve_id,
                    title=f"PoC: {repo['name']}",
                    source=self.source_name,
                    type=ThreatType.exploit,
                    severity=Severity.unknown,  # реальная severity берётся из NVD по cve_id
                    exploit_maturity=ExploitMaturity.poc,
                    published=repo.get("created_at"),
                    summary=(repo.get("description") or "")[:500],
                    tags=["poc", cve_id],
                    url=repo.get("html_url"),
                )
            )
        return threats
