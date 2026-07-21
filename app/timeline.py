"""
Cyber Timeline: для одного CVE собирает все записи из разных источников
(NVD, GitHub PoC, Exploit-DB, CISA KEV, CERT-UA/новости-упоминания) в единую
хронологию и считает, насколько быстро угроза "созрела" — от публикации до
появления рабочего эксплойта и до подтверждённой эксплуатации "в дикой природе".
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db import ThreatORM

EVENT_LABELS = {
    "published": "Уязвимість опублікована",
    "poc": "З'явився публічний PoC",
    "weaponized": "З'явився готовий експлойт",
    "kev": "Додано в CISA KEV (активна експлуатація)",
    "advisory": "Попередження CERT-UA / офіційне повідомлення",
    "mention": "Згадка в новинах",
}

SOURCE_TO_EVENT_TYPE = {
    "NVD": "published",
    "GitHub": "poc",
    "Exploit-DB": "weaponized",
    "CISA KEV": "kev",
    "CERT-UA": "advisory",
    "Кіберполіція України": "advisory",
    "Держспецзв'язку (SSSCIP)": "advisory",
    "NCSC UK": "advisory",
}


def _event_type(row: ThreatORM) -> str:
    return SOURCE_TO_EVENT_TYPE.get(row.source, "mention")


def _event_date(row: ThreatORM) -> Optional[datetime]:
    # для KEV приоритет — дата попадания в каталог, а не published
    if row.source == "CISA KEV" and row.added_to_kev:
        return row.added_to_kev
    return row.published


def build_timeline(db: Session, cve_id: str) -> dict:
    rows = (
        db.query(ThreatORM)
        .filter(ThreatORM.cve_id == cve_id.upper())
        .order_by(ThreatORM.published.asc())
        .all()
    )

    if not rows:
        return {"cve_id": cve_id.upper(), "found": False, "events": []}

    events = []
    for row in rows:
        date = _event_date(row)
        if not date:
            continue
        etype = _event_type(row)
        events.append(
            {
                "type": etype,
                "label": EVENT_LABELS.get(etype, row.source),
                "date": date,
                "source": row.source,
                "title": row.title,
                "url": row.url,
                "severity": row.severity,
            }
        )
    events.sort(key=lambda e: e["date"])

    published_event = next((e for e in events if e["type"] == "published"), None)
    poc_event = next((e for e in events if e["type"] == "poc"), None)
    kev_event = next((e for e in events if e["type"] == "kev"), None)

    days_to_poc = (
        (poc_event["date"] - published_event["date"]).days
        if published_event and poc_event
        else None
    )
    days_to_kev = (
        (kev_event["date"] - published_event["date"]).days
        if published_event and kev_event
        else None
    )

    # Rule-based вердикт (без AI — эвристика на основе скорости появления эксплойта).
    # На Этапе 5 это место естественно заменяется на LLM-суммаризацию.
    if days_to_kev is not None and days_to_kev <= 2:
        verdict = "Критична швидкість: почали атакувати практично одразу після публікації — патчити невідкладно."
    elif days_to_poc is not None and days_to_poc <= 1:
        verdict = "PoC з'явився миттєво — високий ризик швидкої експлуатації, пріоритет патчингу високий."
    elif days_to_poc is not None and days_to_poc <= 7:
        verdict = "PoC з'явився протягом першого тижня — типовий темп для активно досліджуваних вразливостей."
    elif poc_event or kev_event:
        verdict = "Експлуатація зафіксована, але не миттєво — є час на плановий патчинг."
    else:
        verdict = "Поки що немає підтверджених PoC або фактів експлуатації в дикій природі."

    best_cvss = next((r.cvss_score for r in rows if r.cvss_score is not None), None)
    best_epss = next((r.epss_score for r in rows if r.epss_score is not None), None)

    return {
        "cve_id": cve_id.upper(),
        "found": True,
        "events": events,
        "days_to_poc": days_to_poc,
        "days_to_kev": days_to_kev,
        "cvss_score": best_cvss,
        "epss_score": best_epss,
        "verdict": verdict,
    }
