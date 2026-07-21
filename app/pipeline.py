"""
Точка входа для сбора данных. Запускается по расписанию
(GitHub Actions cron, см. .github/workflows/collect.yml) или вручную:

    python -m app.pipeline
"""
import logging

from dotenv import load_dotenv

load_dotenv()

from app.collectors.alienvault_otx import AlienVaultOTXCollector
from app.collectors.cert_ua import CertUACollector
from app.collectors.curated import CuratedCollector
from app.collectors.cisa_kev import CISAKEVCollector
from app.collectors.exploitdb import ExploitDBCollector
from app.collectors.generic_scraper import GenericHTMLCollector
from app.collectors.github_poc import GitHubPoCCollector
from app.collectors.malwarebazaar import MalwareBazaarCollector
from app.collectors.ncsc_uk import NCSCCollector
from app.collectors.news import NewsCollector
from app.collectors.nvd import NVDCollector
from app.collectors.registry import ALL_SCRAPER_CONFIGS
from app.collectors.rnbo_ua import RNBOCollector
from app.collectors.ssscip_ua import SSSCIPCollector
from app.collectors.ssu_ua import SSUCollector
from app.collectors.threatfox import ThreatFoxCollector
from app.collectors.vendor_rss import VendorRSSCollector
from app.db import SessionLocal, init_db
from app.enrichment import enrich_epss
from app.storage import bulk_upsert

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("pipeline")

COLLECTORS = [
    # Кураторські записи (ручні посилання)
    CuratedCollector(),
    # Украина
    CertUACollector(),
    *(GenericHTMLCollector(cfg) for cfg in ALL_SCRAPER_CONFIGS),
    RNBOCollector(),
    SSUCollector(),
    SSSCIPCollector(),
    VendorRSSCollector(),
    MalwareBazaarCollector(),
    AlienVaultOTXCollector(),
    # Мир — уязвимости и эксплойты
    NVDCollector(lookback_hours=48),
    CISAKEVCollector(),
    GitHubPoCCollector(lookback_days=7),
    ExploitDBCollector(lookback_days=7),
    # Мир — новости и IOC
    NewsCollector(),
    NCSCCollector(),
    ThreatFoxCollector(),
]


def run():
    init_db()
    db = SessionLocal()
    summary = {}
    try:
        for collector in COLLECTORS:
            logger.info("Running collector: %s", collector.source_name)
            try:
                threats = collector.fetch()
            except Exception as e:
                logger.exception("Collector %s crashed: %s", collector.source_name, e)
                summary[collector.source_name] = {"error": str(e)}
                continue

            result = bulk_upsert(db, threats)
            summary[collector.source_name] = result
            logger.info("%s: %s", collector.source_name, result)

        logger.info("Enriching with EPSS scores...")
        try:
            epss_updated = enrich_epss(db)
            summary["epss_enrichment"] = {"updated": epss_updated}
        except Exception as e:
            logger.exception("EPSS enrichment crashed: %s", e)
            summary["epss_enrichment"] = {"error": str(e)}
    finally:
        db.close()

    logger.info("Pipeline finished: %s", summary)
    return summary


if __name__ == "__main__":
    run()
