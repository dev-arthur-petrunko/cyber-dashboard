"""
Слой БД. По умолчанию — SQLite (data/threats.db), без внешних зависимостей.
Для продакшена достаточно поменять DATABASE_URL в .env на postgresql://...
"""
import os
from datetime import datetime

from sqlalchemy import (Column, DateTime, Float, Integer, String, Text, JSON,
                         UniqueConstraint, create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./data/threats.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class ThreatORM(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True)
    external_id = Column(String, index=True)
    source = Column(String, index=True)

    title = Column(String, nullable=False)
    type = Column(String, index=True)
    severity = Column(String, index=True)

    country = Column(JSON, default=list)
    region = Column(String, default="World", index=True)
    vendor = Column(String, nullable=True)
    products = Column(JSON, default=list)

    cvss_score = Column(Float, nullable=True)
    epss_score = Column(Float, nullable=True)
    exploit_maturity = Column(String, default="Unknown", index=True)

    published = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    tags = Column(JSON, default=list)
    summary = Column(Text, default="")
    url = Column(String, nullable=True)

    cve_id = Column(String, nullable=True, index=True)
    poc_published = Column(DateTime, nullable=True)
    added_to_kev = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )


def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
