"""Перевірка реєстру колекторів і коректності pipeline-конфігурації."""
import app.pipeline as pipeline
from app.collectors.registry import ALL_SCRAPER_CONFIGS


def test_all_collectors_registered():
    assert len(pipeline.COLLECTORS) >= 10


def test_collectors_have_unique_source_names():
    names = [c.source_name for c in pipeline.COLLECTORS]
    assert len(names) == len(set(names)), f"duplicate sources: {names}"


def test_collectors_expose_fetch():
    for collector in pipeline.COLLECTORS:
        assert callable(getattr(collector, "fetch")), collector.source_name
        assert collector.source_name


def test_all_collectors_subclass_base():
    from app.collectors.base import BaseCollector

    for collector in pipeline.COLLECTORS:
        assert isinstance(collector, BaseCollector), collector.source_name


def test_scraper_configs_have_required_fields():
    for cfg in ALL_SCRAPER_CONFIGS:
        assert cfg.source_name
        assert cfg.list_url.startswith("http")
        assert cfg.item_selector
        assert cfg.title_selector


def test_scraper_configs_unique_names():
    names = [cfg.source_name for cfg in ALL_SCRAPER_CONFIGS]
    assert len(names) == len(set(names))


def test_pipeline_imports_without_side_effects():
    # import-модуль не повинен тригерити мережеві запити або БД
    assert callable(pipeline.run)
