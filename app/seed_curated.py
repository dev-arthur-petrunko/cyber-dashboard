"""
Швидке завантаження кураторських записів у БД:

    python -m app.seed_curated
"""
import logging

from dotenv import load_dotenv

load_dotenv()

from app.collectors.curated import CuratedCollector
from app.db import SessionLocal, init_db
from app.storage import bulk_upsert

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("seed_curated")


def run():
    init_db()
    db = SessionLocal()
    try:
        collector = CuratedCollector()
        threats = collector.fetch()
        result = bulk_upsert(db, threats)
        logger.info("Seeded %s curated threats: %s", len(threats), result)
        return result
    finally:
        db.close()


if __name__ == "__main__":
    run()
