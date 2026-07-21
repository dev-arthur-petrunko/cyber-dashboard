"""
Коллектор для CERT-UA (Урядова команда реагування на кіберінциденти).
RSS: https://cert.gov.ua/api/articles/rss
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

CERT_UA_RSS_URL = "https://cert.gov.ua/api/articles/rss"

# Простая эвристика: если в заголовке/тексте встречаются такие слова —
# считаем severity выше. Это заменяется на AI-классификацию на Этапе 5.
CRITICAL_MARKERS = re.compile(r"критич|ransomware|шифрувальник|0-?day|zero-?day", re.I)
HIGH_MARKERS = re.compile(r"apt|шкідлив|malware|фішинг|phishing", re.I)


class CertUACollector(BaseCollector):
    source_name = "CERT-UA"

    def _guess_severity(self, text: str) -> Severity:
        if CRITICAL_MARKERS.search(text):
            return Severity.critical
        if HIGH_MARKERS.search(text):
            return Severity.high
        return Severity.medium

    def fetch(self) -> list[Threat]:
        try:
            feed = feedparser.parse(CERT_UA_RSS_URL)
        except Exception as e:
            logger.error("CERT-UA fetch failed: %s", e)
            return []

        if feed.bozo and not feed.entries:
            logger.error("CERT-UA feed parse error: %s", feed.bozo_exception)
            return []

        threats = []
        for entry in feed.entries:
            link = entry.get("link", "")
            external_id = link or hashlib.sha1(
                entry.get("title", "").encode()
            ).hexdigest()

            summary = entry.get("summary", "") or entry.get("description", "")
            full_text = f"{entry.get('title', '')} {summary}"

            published = entry.get("published") or entry.get("updated")
            try:
                published_dt = parsedate_to_datetime(published) if published else datetime.utcnow()
            except (TypeError, ValueError):
                published_dt = datetime.utcnow()

            # CERT-UA часто указывает ID вида CERT-UA#9688 в тексте — вытаскиваем как tag
            cert_id_match = re.search(r"CERT-UA#\d+", full_text)

            threats.append(
                Threat(
                    external_id=external_id,
                    title=entry.get("title", "Без заголовка"),
                    source=self.source_name,
                    type=ThreatType.advisory,
                    severity=self._guess_severity(full_text),
                    country=["Ukraine"],
                    region=Region.ua,
                    published=published_dt,
                    summary=re.sub("<[^<]+?>", "", summary)[:1000],
                    tags=[cert_id_match.group(0)] if cert_id_match else [],
                    url=link or None,
                )
            )
        return threats
