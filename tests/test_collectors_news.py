"""Тести для новинного колектора з мокнутим feedparser."""
from types import SimpleNamespace

import app.collectors.news as news_module
from app.collectors.news import NewsCollector


def _entry(title, link="", published="", tags=None):
    return {
        "title": title,
        "link": link,
        "published": published,
        "tags": [{"term": t} for t in (tags or [])],
    }


def _feed(entries):
    return SimpleNamespace(bozo=False, entries=entries)


def _mock_parse(first_entries, other_entries=None):
    """parse() returns first_entries for the first feed, other_entries for the rest."""
    calls = {"n": 0}

    def parse(url):
        entries = first_entries if calls["n"] == 0 else (other_entries or [])
        calls["n"] += 1
        return _feed(entries)

    return parse


def test_fetch_parses_entries(monkeypatch):
    monkeypatch.setattr(
        news_module,
        "feedparser",
        SimpleNamespace(
            parse=_mock_parse(
                [
                    _entry("New ransomware hits", "https://x/1", "Tue, 05 May 2026 10:00:00 GMT"),
                    _entry("Patch Tuesday", "https://x/2", "Wed, 06 May 2026 11:00:00 GMT"),
                ]
            )
        ),
    )
    threats = NewsCollector().fetch()
    assert len(threats) == 2
    assert all(t.source in ("The Hacker News", "BleepingComputer") for t in threats)


def test_excludes_ctf_and_hackathon_titles(monkeypatch):
    monkeypatch.setattr(
        news_module,
        "feedparser",
        SimpleNamespace(
            parse=_mock_parse(
                [
                    _entry("Hackathon winners announced"),
                    _entry("Real cyberattack details"),
                    _entry("CTF writeup"),
                ]
            )
        ),
    )
    threats = NewsCollector().fetch()
    assert len(threats) == 1
    assert threats[0].title == "Real cyberattack details"


def test_bozo_feed_without_entries_is_skipped(monkeypatch):
    monkeypatch.setattr(
        news_module,
        "feedparser",
        SimpleNamespace(
            parse=lambda url: SimpleNamespace(bozo=True, bozo_exception=Exception("bad xml"), entries=[])
        ),
    )
    assert NewsCollector().fetch() == []


def test_external_id_falls_back_to_title_hash(monkeypatch):
    monkeypatch.setattr(
        news_module,
        "feedparser",
        SimpleNamespace(
            parse=lambda url: _feed([_entry("No link in this entry")])
        ),
    )
    threats = NewsCollector().fetch()
    assert threats[0].external_id  # не пустий рядок
    assert threats[0].url is None
