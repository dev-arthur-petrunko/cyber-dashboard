"""
Единая модель данных для всех источников угроз.
Любой коллектор (NVD, CISA KEV, CERT-UA, ...) обязан превращать
сырые данные источника в объект Threat перед сохранением в БД.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Severity(str, Enum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"
    unknown = "Unknown"


class ThreatType(str, Enum):
    cve = "CVE"
    advisory = "Advisory"
    news = "News"
    exploit = "Exploit"
    ioc = "IOC"


class Region(str, Enum):
    ua = "UA"
    world = "World"


class ExploitMaturity(str, Enum):
    poc = "PoC"          # есть публичный proof-of-concept
    weaponized = "Weaponized"   # есть готовый рабочий эксплойт
    in_the_wild = "In the wild"  # зафиксирована реальная эксплуатация (KEV)
    unknown = "Unknown"


class Threat(BaseModel):
    # Стабильный ключ для дедупликации (например "CVE-2024-12345" или hash(url))
    external_id: str = Field(..., description="Уникальный ID во внешнем источнике")

    title: str
    source: str  # "NVD" | "CISA KEV" | "CERT-UA" | "GitHub" | "BleepingComputer" ...
    type: ThreatType
    severity: Severity = Severity.unknown

    country: list[str] = Field(default_factory=list)
    region: Region = Region.world  # для переключателя "Украина / Мир" на дашборде
    vendor: Optional[str] = None
    products: list[str] = Field(default_factory=list)

    # Глубина риска (Этап 5+): числовые метрики вместо только Severity-ярлыка
    cvss_score: Optional[float] = None
    epss_score: Optional[float] = None  # вероятность эксплуатации в след. 30 дней (0-1)
    exploit_maturity: ExploitMaturity = ExploitMaturity.unknown

    published: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    tags: list[str] = Field(default_factory=list)
    summary: str = ""
    url: Optional[str] = None

    # Поля для будущего "Cyber Timeline" (Этап далее по плану)
    cve_id: Optional[str] = None
    poc_published: Optional[datetime] = None
    added_to_kev: Optional[datetime] = None

    class Config:
        use_enum_values = True
