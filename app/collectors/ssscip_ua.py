"""
Headless-коллектор для сайту Держспецзв'язку (SSSCIP / cip.gov.ua).
cip.gov.ua віддає 403 при звичайному requests (бот-захист Cloudflare),
тому використовуємо Playwright для рендерингу сторінки у реальному браузері.

Вимоги:
  pip install playwright
  playwright install chromium

Якщо Playwright не встановлено — колектор логує інструкцію і повертає пустий
список, не падаючи.
"""
import logging
from datetime import datetime
from urllib.parse import urljoin

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

SSSCIP_NEWS_URL = "https://cip.gov.ua/ua/news"


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


class SSSCIPCollector(BaseCollector):
    source_name = "Держспецзв'язку (SSSCIP)"

    def fetch(self) -> list[Threat]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning(
                "Playwright не встановлено — SSSCIP пропущено. "
                "Для обходу бот-захисту cip.gov.ua встанови: "
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
                page.goto(SSSCIP_NEWS_URL, wait_until="networkidle", timeout=60000)

                # Шукаємо типові елементи новин: заголовки з посиланнями
                # Селектори — універсальні, оскільки точна структура може змінюватися
                items = page.locator("article, .news-item, .news-card, [class*='news']").all()
                if not items:
                    # fallback — будь-які посилання, що містять 'news' в URL
                    links = page.locator("a[href*='/news/']").all()
                    for link in links[:20]:
                        title = (link.text_content() or "").strip()
                        href = link.get_attribute("href") or ""
                        if not title or len(title) < 10:
                            continue
                        threats.append(
                            Threat(
                                external_id=href,
                                title=title,
                                source=self.source_name,
                                type=ThreatType.news,
                                severity=Severity.medium,
                                region=Region.ua,
                                published=datetime.utcnow(),
                                summary="",
                                tags=["Ukraine", "SSSCIP"],
                                url=urljoin(SSSCIP_NEWS_URL, href),
                            )
                        )
                else:
                    for item in items[:20]:
                        title_el = item.locator("h2, h3, .title, a").first
                        title = (title_el.text_content() or "").strip()
                        href = title_el.get_attribute("href") or ""
                        if not title or len(title) < 10:
                            continue
                        date_text = ""
                        for sel in ".date, .published, time, [class*='date']":
                            date_els = item.locator(sel).all()
                            if date_els:
                                date_text = date_els[0].text_content() or ""
                                break

                        threats.append(
                            Threat(
                                external_id=href or title,
                                title=title,
                                source=self.source_name,
                                type=ThreatType.news,
                                severity=Severity.medium,
                                region=Region.ua,
                                published=_parse_date(date_text),
                                summary="",
                                tags=["Ukraine", "SSSCIP"],
                                url=urljoin(SSSCIP_NEWS_URL, href) if href else None,
                            )
                        )

                browser.close()
        except Exception as e:
            logger.error("SSSCIP Playwright collector failed: %s", e)
            return []

        logger.info("SSSCIP fetched %s news items", len(threats))
        return threats
