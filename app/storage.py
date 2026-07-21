from sqlalchemy.orm import Session

from app.db import ThreatORM
from app.models.threat import Threat


def upsert_threat(db: Session, threat: Threat) -> ThreatORM:
    """Вставляет новую угрозу или обновляет существующую (по source+external_id)."""
    existing = (
        db.query(ThreatORM)
        .filter_by(source=threat.source, external_id=threat.external_id)
        .first()
    )

    data = threat.model_dump(exclude={"fetched_at"})
    # url приходит как HttpUrl -> приводим к строке
    if data.get("url") is not None:
        data["url"] = str(data["url"])

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        row = existing
    else:
        row = ThreatORM(**data)
        db.add(row)

    db.commit()
    db.refresh(row)
    return row


def bulk_upsert(db: Session, threats: list[Threat]) -> dict:
    inserted, updated = 0, 0
    for t in threats:
        existing = (
            db.query(ThreatORM)
            .filter_by(source=t.source, external_id=t.external_id)
            .first()
        )
        upsert_threat(db, t)
        if existing:
            updated += 1
        else:
            inserted += 1
    return {"inserted": inserted, "updated": updated, "total": len(threats)}
