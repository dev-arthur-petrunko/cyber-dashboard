"""
Конфиги для GenericHTMLCollector. ВАЖНО: селекторы ниже — черновик,
я не смог открыть эти сайты из песочницы (нет доступа к домену),
поэтому проверь их в браузере (DevTools → Inspect на карточке новости)
перед тем как полагаться на данные с них.

Как проверить/поправить:
1. Открой list_url в браузере
2. DevTools → выдели одну карточку новости → посмотри её CSS-класс → item_selector
3. Внутри неё найди заголовок → title_selector
4. Найди ссылку (обычно сама карточка — <a>, либо есть <a> внутри) → link_selector
"""
from app.collectors.generic_scraper import ScraperConfig

# Рабочий URL найден: /articles/ (не /news/ — там 404)
CYBERPOLICE_UA = ScraperConfig(
    source_name="Кіберполіція України",
    list_url="https://cyberpolice.gov.ua/articles/",
    item_selector="article, .news-item, .post, a[href*='/news/'], a[href*='/article/']",
    title_selector="h2, h3, .title",
    link_selector="a",
    base_url="https://cyberpolice.gov.ua",
)

# cip.gov.ua теперь собирается отдельным Playwright-коллектором в
# app/collectors/ssscip_ua.py (обычный requests не обходит защиту).

# НКЦК при РНБО и СБУ теперь собираются отдельными скраперами:
#   app/collectors/rnbo_ua.py
#   app/collectors/ssu_ua.py

ALL_SCRAPER_CONFIGS = [CYBERPOLICE_UA]
