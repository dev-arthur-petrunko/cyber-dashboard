"""Тести для GenericHTMLCollector — скрапер новин із мокнутим HTTP."""
import requests

from app.collectors.generic_scraper import GenericHTMLCollector, ScraperConfig

HTML = """
<html><body>
<article class="news-item">
  <a href="/news/first"><h2 class="title">First Ukraine cyber news</h2></a>
</article>
<article class="news-item">
  <a href="/news/second"><h2 class="title">Second Ukraine cyber news</h2></a>
</article>
<div>not a news item</div>
</body></html>
"""


class _FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def _make_collector():
    config = ScraperConfig(
        source_name="Test News",
        list_url="https://example.com/news",
        item_selector="article.news-item",
        title_selector="h2.title",
        base_url="https://example.com",
    )
    return GenericHTMLCollector(config)


def test_fetch_parses_items(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(HTML))
    threats = _make_collector().fetch()
    assert len(threats) == 2


def test_normalized_fields(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(HTML))
    threat = _make_collector().fetch()[0]
    assert threat.title == "First Ukraine cyber news"
    assert threat.source == "Test News"
    assert threat.region == "UA"
    assert threat.country == ["Ukraine"]
    assert threat.url == "https://example.com/news/first"


def test_absolute_urls_kept_as_is(monkeypatch):
    html = """
    <article class="news-item">
      <a href="https://other.example.com/absolute"><h2 class="title">Abs</h2></a>
    </article>
    """
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(html))
    threat = _make_collector().fetch()[0]
    assert threat.url == "https://other.example.com/absolute"


def test_selector_found_nothing(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResponse("<html><body></body></html>")
    )
    assert _make_collector().fetch() == []


def test_request_failure_returns_empty(monkeypatch):
    def _boom(*a, **k):
        raise requests.Timeout("slow")

    monkeypatch.setattr(requests, "get", _boom)
    assert _make_collector().fetch() == []
