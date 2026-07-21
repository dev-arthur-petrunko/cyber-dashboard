"""
Headless-коллектор новин СБУ (ssu.gov.ua/novyny) з фільтрацією за
кібербезпековими ключовими словами.

ssu.gov.ua віддає 403 при звичайному requests (бот-захист), тому
використовуємо Playwright для рендерингу сторінки у реальному браузері.

Вимоги:
  pip install playwright
  playwright install chromium
"""
import logging
from datetime import datetime
from urllib.parse import urljoin

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

SSU_NEWS_URL = "https://ssu.gov.ua/novyny"

CYBER_KEYWORDS = [
    "кібер", "кибер", "фішинг", "фишинг", "хакер", "ddos", "дідос",
    "кібератака", "кибератака", "кіберзагроза", "кібербезпека",
    "інформаційна безпека", "информационная безопасность", "злам",
    "шпигун", "розвідка", "ботнет", "вірус", "шкідливе", "malware",
]

# Exclude non-threat content (competitions, CTFs, education events)
EXCLUDE_KEYWORDS = [
    "ctf", "shehack", "конкурс", "змагання", "соревнован",
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


class SSUCollector(BaseCollector):
    source_name = "СБУ / Департамент кібербезпеки"

    def fetch(self) -> list[Threat]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning(
                "Playwright не встановлено — СБУ пропущено. "
                "Для обходу бот-захисту ssu.gov.ua встанови: "
                "pip install playwright && playwright install chromium"
            )
            return []

        threats: list[Threat] = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.goto(SSU_NEWS_URL, wait_until="networkidle", timeout=60000)

                # SSU, як і більшість сайтів, має карточки новин з посиланнями
                links = page.locator("article a, .news-item a, .item-news a, .post a, .news-card a").all()
                if not links:
                    links = page.locator("a[href*='/novyny/']").all()

                seen = set()
                for link in links[:40]:
                    title = (link.text_content() or "").strip()
                    href = link.get_attribute("href") or ""
                    if not title or len(title) < 10 or not href:
                        continue

                    url = urljoin(SSU_NEWS_URL, href)
                    if url in seen:
                        continue
                    seen.add(url)

                    if not _matches_cyber(title, ""):
                        continue

                    # Пробуємо отримати дату з карточки або сторінки
                    published = datetime.utcnow()
                    try:
                        parent = link.locator("..").first
                        date_text = ""
                        for sel in ".date, .published, time, [class*='date']":
                            date_els = parent.locator(sel).all()
                            if date_els:
                                date_text = date_els[0].text_content() or ""
                                break
                        if not date_text:
                            # шукаємо дату у батьківських елементах
                            for i in range(3):
                                parent = parent.locator("..").first
                                for sel in ".date, .published, time, [class*='date']":
                                    date_els = parent.locator(sel).all()
                                    if date_els:
                                        date_text = date_els[0].text_content() or ""
                                        break
                                if date_text:
                                    break
                        published = _parse_date(date_text)
                    except Exception:
                        pass

                    threats.append(
                        Threat(
                            external_id=url,
                            title=title,
                            source=self.source_name,
                            type=ThreatType.news,
                            severity=Severity.high,
                            region=Region.ua,
                            published=published,
                            summary="",
                            tags=["Ukraine", "SBU", "cyber"],
                            url=url,
                        )
                    )

                browser.close()
        except Exception as e:
            logger.error("SSU Playwright collector failed: %s", e)
            return []

        logger.info("SSU fetched %s cyber-related news", len(threats))
        return threats
