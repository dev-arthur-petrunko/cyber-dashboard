"""
Новостной коллектор. Источники — публичные RSS без ключей:
  - The Hacker News: https://feeds.feedburner.com/TheHackersNews
  - BleepingComputer: https://www.bleepingcomputer.com/feed/
"""
import hashlib
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser

from app.collectors.base import BaseCollector
from app.models.threat import Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
}

# Exclude non-threat content (competitions, CTFs, education events)
EXCLUDE_KEYWORDS = [
    "ctf", "shehack", "конкурс", "змагання", "соревнован",
    "challenge", "чемпіонат", "першість", "турнір", "хакатон", "hackathon",
    "конференц", "conference", "форум", "навчанн", "обучен",
]


class NewsCollector(BaseCollector):
    source_name = "News"

    def fetch(self) -> list[Threat]:
        threats = []
        for outlet, url in FEEDS.items():
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                logger.error("News fetch failed for %s: %s", outlet, e)
                continue

            if feed.bozo and not feed.entries:
                logger.error("News feed parse error for %s: %s", outlet, feed.bozo_exception)
                continue

            for entry in feed.entries[:30]:
                title = entry.get("title", "Untitled")
                # Skip non-threat content
                title_lower = title.lower()
                if any(kw in title_lower for kw in EXCLUDE_KEYWORDS):
                    continue

                link = entry.get("link", "")
                external_id = link or hashlib.sha1(
                    entry.get("title", "").encode()
                ).hexdigest()

                published = entry.get("published") or entry.get("updated")
                try:
                    published_dt = (
                        parsedate_to_datetime(published) if published else datetime.utcnow()
                    )
                except (TypeError, ValueError):
                    published_dt = datetime.utcnow()

                summary = entry.get("summary", "")

                threats.append(
                    Threat(
                        external_id=external_id,
                        title=title,
                        source=outlet,
                        type=ThreatType.news,
                        severity=Severity.unknown,
                        published=published_dt,
                        summary=summary[:800],
                        tags=[t["term"] for t in entry.get("tags", [])][:5],
                        url=link or None,
                    )
                )
        return threats
