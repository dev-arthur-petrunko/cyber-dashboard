"""
Headless-колектор для сайту Держспецзв'язку (SSSCIP / cip.gov.ua).
cip.gov.ua віддає Access Denied через Akamai bot-захист, тому використовуємо
Playwright + playwright-stealth для обходу.

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

SSSCIP_NEWS_URL = "https://cip.gov.ua/ua/news"


def _parse_date(text: str | None) -> datetime:
    if not text:
        return datetime.utcnow()
    text = text.strip()
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
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
            from playwright_stealth import Stealth
        except ImportError:
            logger.warning(
                "Playwright/playwright-stealth не встановлено — SSSCIP пропущено. "
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
                page.goto(SSSCIP_NEWS_URL, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)

                # Точный селектор по реальной вёрстке (Angular, class="article-title")
                titles = page.locator("h3.article-title").all()
                logger.info("SSSCIP: found %d article-title elements", len(titles))

                for title_el in titles[:20]:
                    title = (title_el.text_content() or "").strip()
                    if not title:
                        continue

                    href = ""
                    try:
                        anchor = title_el.locator("xpath=ancestor::a[1]")
                        href = anchor.get_attribute("href") or ""
                    except Exception:
                        pass

                    date_text = ""
                    try:
                        row = title_el.locator("xpath=ancestor::div[contains(@class,'row')][1]")
                        date_el = row.locator(".date-tag").first
                        date_text = date_el.text_content() or ""
                    except Exception:
                        pass

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