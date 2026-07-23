"""
Headless-колектор новин СБУ (ssu.gov.ua/novyny) з фільтрацією за
кіберпов'язаними ключовими словами.

ssu.gov.ua віддає Access Denied через Akamai bot-захист, тому
використовуємо Playwright + playwright-stealth для обходу.

Вимоги:
  pip install playwright playwright-stealth
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

EXCLUDE_KEYWORDS = [
    "ctf", "shehack", "конкурс", "змагання", "соревнован",
    "challenge", "чемпіонат", "першість", "турнір", "хакатон", "hackathon",
    "конференц", "conference", "форум", "навчанн", "обучен",
]


def _matches_cyber(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
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
            from playwright_stealth import Stealth
        except ImportError:
            logger.warning(
                "Playwright/playwright-stealth не встановлено — СБУ пропущено. "
                "pip install playwright playwright-stealth && playwright install chromium"
            )
            return []

        threats: list[Threat] = []
        try:
            with Stealth().use_sync(sync_playwright()) as p:
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
                page.wait_for_timeout(3000)

                # .news-title цепляет и <a class="news-title">, и <h2 class="news-title">
                # (внутри <a class="big-preview">) — картиночные "пустые" ссылки без текста
                # этот класс не имеют, дублей не будет.
                title_elements = page.locator(".news-title").all()
                logger.info("SSU: found %d news-title elements", len(title_elements))

                seen_hrefs = set()
                for el in title_elements[:40]:
                    title = (el.text_content() or "").strip()
                    if not title or len(title) < 10:
                        continue

                    tag_name = el.evaluate("e => e.tagName.toLowerCase()")
                    href = ""
                    date_text = ""
                    try:
                        if tag_name == "a":
                            href = el.get_attribute("href") or ""
                        else:
                            anchor = el.locator("xpath=ancestor::a[1]")
                            href = anchor.get_attribute("href") or ""
                            date_el = anchor.locator(".news-date").first
                            date_text = date_el.text_content() or ""
                    except Exception:
                        pass

                    if not href or href in seen_hrefs:
                        continue
                    seen_hrefs.add(href)

                    if not _matches_cyber(title, ""):
                        continue

                    threats.append(
                        Threat(
                            external_id=href,
                            title=title,
                            source=self.source_name,
                            type=ThreatType.news,
                            severity=Severity.high,
                            region=Region.ua,
                            published=_parse_date(date_text),
                            summary="",
                            tags=["Ukraine", "SBU", "cyber"],
                            url=urljoin(SSU_NEWS_URL, href),
                        )
                    )

                browser.close()
        except Exception as e:
            logger.error("SSU Playwright collector failed: %s", e)
            return []

        logger.info("SSU fetched %s cyber-related news", len(threats))
        return threats