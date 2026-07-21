"""
Коллектор NCSC UK (National Cyber Security Centre) Threat Reports.
Подтверждённый рабочий RSS: https://www.ncsc.gov.uk/api/1/services/v1/report-rss-feed.xml
"""
import hashlib
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser

from app.collectors.base import BaseCollector
from app.models.threat import Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

NCSC_RSS_URL = "https://www.ncsc.gov.uk/api/1/services/v1/report-rss-feed.xml"


class NCSCCollector(BaseCollector):
    source_name = "NCSC UK"

    def fetch(self) -> list[Threat]:
        try:
            feed = feedparser.parse(NCSC_RSS_URL)
        except Exception as e:
            logger.error("NCSC fetch failed: %s", e)
            return []

        if feed.bozo and not feed.entries:
            logger.error("NCSC feed parse error: %s", feed.bozo_exception)
            return []

        threats = []
        for entry in feed.entries:
            link = entry.get("link", "")
            external_id = link or hashlib.sha1(entry.get("title", "").encode()).hexdigest()

            published = entry.get("published") or entry.get("updated")
            try:
                published_dt = parsedate_to_datetime(published) if published else datetime.utcnow()
            except (TypeError, ValueError):
                published_dt = datetime.utcnow()

            threats.append(
                Threat(
                    external_id=external_id,
                    title=entry.get("title", "Untitled"),
                    source=self.source_name,
                    type=ThreatType.advisory,
                    severity=Severity.medium,
                    published=published_dt,
                    summary=entry.get("summary", "")[:800],
                    url=link or None,
                )
            )
        return threats
