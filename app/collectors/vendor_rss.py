"""
RSS-коллектор вендорів, які регулярно публікують аналітику про загрози для України:
  - ESET WeLiveSecurity
  - Cisco Talos Intelligence

Фільтрація за ключовими словами в title/summary: ukraine, ukrainian, sandworm,
gamaredon, wipers, hermeticwiper, caddywiper, cert-ua.
"""
import hashlib
import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

FEEDS = {
    "ESET WeLiveSecurity": "https://www.welivesecurity.com/feed/",
    "Cisco Talos Intelligence": "https://blog.talosintelligence.com/rss/",
}

UKRAINE_KEYWORDS = [
    "ukraine", "ukrainian", "kyiv", "kiev",
    "sandworm", "gamaredon", "uac-0010", "uac0010",
    "wiper", "wipers", "hermeticwiper", "caddywiper", "doublezero",
    "cert-ua", "cert ua",
]


def _matches_ukraine(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in UKRAINE_KEYWORDS)


class VendorRSSCollector(BaseCollector):
    source_name = "Vendor RSS"

    def fetch(self) -> list[Threat]:
        threats: list[Threat] = []
        for outlet, url in FEEDS.items():
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                logger.error("Vendor RSS fetch failed for %s: %s", outlet, e)
                continue

            if feed.bozo and not feed.entries:
                logger.error("Vendor RSS parse error for %s: %s", outlet, feed.bozo_exception)
                continue

            for entry in feed.entries[:30]:
                title = entry.get("title", "Untitled")
                summary = entry.get("summary", "")

                if not _matches_ukraine(title, summary):
                    continue

                link = entry.get("link", "")
                external_id = link or hashlib.sha1(title.encode()).hexdigest()

                published = entry.get("published") or entry.get("updated")
                try:
                    published_dt = parsedate_to_datetime(published) if published else datetime.utcnow()
                except (TypeError, ValueError):
                    published_dt = datetime.utcnow()

                # Оцінюємо severity за ключовими словами
                text_lower = f"{title} {summary}".lower()
                if any(w in text_lower for w in ["wiper", "destructive", "supply chain", "critical"]):
                    severity = Severity.critical
                elif any(w in text_lower for w in ["apt", "espionage", "steal", "backdoor"]):
                    severity = Severity.high
                else:
                    severity = Severity.medium

                threats.append(
                    Threat(
                        external_id=external_id,
                        title=title,
                        source=outlet,
                        type=ThreatType.news,
                        severity=severity,
                        region=Region.ua,
                        published=published_dt,
                        summary=summary[:800],
                        tags=[t["term"] for t in entry.get("tags", [])][:5] + ["Ukraine"],
                        url=link or None,
                    )
                )

        logger.info("Vendor RSS fetched %s Ukraine-related posts", len(threats))
        return threats
