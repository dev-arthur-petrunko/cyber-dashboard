"""
Скрапер новин НКЦК при РНБО (rnbo.gov.ua/ua/Novyny/).

Моніторить стрічку новин і залишає записи, де в заголовку/анонсі
є слова: кібератака, кіберзагроза, хакерська атака, DDoS, фішинг,
критична інфраструктура, кібербезпека, штучний інтелект (AI).
"""
import logging
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

RNBO_NEWS_URL = "https://rnbo.gov.ua/ua/Novyny/"

CYBER_KEYWORDS = [
    "кібератака", "кибератака", "кіберзагроза", "киберзагроза",
    "хакерська атака", "хакерская атака", "ddos", "дідос", "фішинг", "фишинг",
    "критична інфраструктура", "критическая инфраструктура",
    "кібербезпека", "кибербезопасность", "інформаційна безпека",
    "комунікаційна інфраструктура", "зламу", "взлом", "ботнет",
    "штучний інтелект", "artificial intelligence", "кібер",
]

# Exclude non-threat content (competitions, CTFs, education events)
EXCLUDE_KEYWORDS = [
    "ctf", "shehack", "конкурс", "конкурс", "змагання", "соревнован",
    "challenge", "чемпіонат", "першість", "турнір", "хакатон", "hackathon",
    "конференц", "conference", "форум", "навчанн", "обучен",
]


def _matches_cyber(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
    # Exclude non-threat content (CTF, competitions, etc.)
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False
    return any(kw in text for kw in CYBER_KEYWORDS)


def _parse_date(text: str | None) -> datetime:
    if not text:
        return datetime.utcnow()
    text = text.strip()
    for fmt in ("%d.%m.%Y", "%d.%m.%Y %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return datetime.utcnow()


class RNBOCollector(BaseCollector):
    source_name = "НКЦК при РНБО"

    def fetch(self) -> list[Threat]:
        try:
            resp = requests.get(
                RNBO_NEWS_URL,
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("RNBO fetch failed: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # Новини RNBO: <a class="title" href="/ua/Diialnist/XXXX.html">...</a>
        links = soup.select('a.title[href*="/Diialnist/"]')
        if not links:
            links = soup.select('a[href*="/Diialnist/"]')

        threats: list[Threat] = []
        seen = set()

        for link in links[:30]:
            title = (link.get_text(strip=True) or "").strip()
            href = link.get("href", "")
            if not title or not href:
                continue

            url = urljoin(RNBO_NEWS_URL, href)
            if url in seen:
                continue
            seen.add(url)

            if not _matches_cyber(title, ""):
                continue

            # Пробуємо отримати дату та короткий опис зі сторінки новини
            summary = ""
            published = datetime.utcnow()
            try:
                article_resp = requests.get(
                    url,
                    timeout=15,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                        ),
                    },
                )
                if article_resp.status_code == 200:
                    article_soup = BeautifulSoup(article_resp.text, "html.parser")
                    date_el = article_soup.find("time") or article_soup.find(class_=lambda x: x and "date" in x.lower())
                    if date_el:
                        published = _parse_date(date_el.get_text(strip=True) or date_el.get("datetime"))
                    content_el = article_soup.find("article") or article_soup.find("main") or article_soup.find("div", class_=lambda x: x and "content" in x.lower())
                    if content_el:
                        summary = content_el.get_text(separator=" ", strip=True)[:400]
            except Exception as e:
                logger.debug("RNBO article fetch failed for %s: %s", url, e)

            threats.append(
                Threat(
                    external_id=url,
                    title=title,
                    source=self.source_name,
                    type=ThreatType.news,
                    severity=Severity.high,
                    region=Region.ua,
                    published=published,
                    summary=summary,
                    tags=["Ukraine", "RNBO", "cyber"],
                    url=url,
                )
            )

        logger.info("RNBO fetched %s cyber-related news", len(threats))
        return threats
