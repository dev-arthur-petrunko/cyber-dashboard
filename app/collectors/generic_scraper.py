"""
У СБУ, НКЦК, кіберполіції і Держспецзв'язку (cip.gov.ua) нет стабильного
публичного RSS или API — только HTML-страницы с новостями. Это единственный
рабочий вариант их подключить, но он ХРУПКИЙ: если сайт поменяет вёрстку,
селекторы перестанут работать и коллектор нужно будет поправить.

Использование: создать экземпляр с конфигом (см. registry.py ниже) и
проверить/поправить CSS-селекторы под актуальную вёрстку сайта — я не смог
протестировать их вживую (эти домены недоступны из песочницы), так что
считай их черновиком, а не готовым решением.
"""
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.models.threat import Region, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    source_name: str
    list_url: str
    item_selector: str       # CSS-селектор одной новости в списке
    title_selector: str      # CSS-селектор заголовка внутри item_selector
    link_selector: str = ""  # если пусто — берём href с самого item_selector или title
    link_attr: str = "href"
    base_url: str = ""       # для относительных ссылок


class GenericHTMLCollector(BaseCollector):
    """Дженерик-коллектор: один класс, много конфигов (см. registry.py)."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.source_name = config.source_name

    def fetch(self) -> list[Threat]:
        try:
            resp = requests.get(
                self.config.list_url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0 (compatible; UA-Cyber-Dashboard/0.1)"},
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("%s scrape failed: %s", self.source_name, e)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(self.config.item_selector)
        if not items:
            logger.warning(
                "%s: селектор '%s' не нашёл ни одной новости — вёрстка изменилась, "
                "проверь конфиг в registry.py",
                self.source_name,
                self.config.item_selector,
            )

        threats = []
        for item in items[:30]:
            title_el = item.select_one(self.config.title_selector)
            if not title_el and item.name == "a" and item.get_text(strip=True):
                title_el = item  # заголовок = текст самой ссылки
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title:
                continue

            link_el = (
                item.select_one(self.config.link_selector)
                if self.config.link_selector
                else (item if item.name == "a" else title_el)
            )
            href = link_el.get(self.config.link_attr, "") if link_el else ""
            if href and self.config.base_url and not href.startswith("http"):
                href = self.config.base_url.rstrip("/") + "/" + href.lstrip("/")

            external_id = href or hashlib.sha1(title.encode()).hexdigest()

            threats.append(
                Threat(
                    external_id=external_id,
                    title=title,
                    source=self.source_name,
                    type=ThreatType.advisory,
                    severity=Severity.unknown,
                    country=["Ukraine"],
                    region=Region.ua,
                    published=datetime.utcnow(),  # список не даёт точную дату — уточняется по ссылке
                    summary="",
                    url=href or None,
                )
            )
        return threats
