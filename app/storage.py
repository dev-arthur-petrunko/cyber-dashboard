from sqlalchemy.orm import Session

from app.db import ThreatORM
from app.models.threat import Threat


def bulk_upsert(db: Session, threats: list[Threat]) -> dict:
    """Вставляет/обновляет пачку угроз одним запросом на чтение и одним
    коммитом на всю пачку — вместо отдельного round-trip к БД на каждую
    запись. Критично для удалённой БД (Neon/Postgres): 1600 записей по
    отдельности над сетью могут занимать 10+ минут, пачкой — секунды."""
    if not threats:
        return {"inserted": 0, "updated": 0, "total": 0}

    sources = {t.source for t in threats}
    external_ids = {t.external_id for t in threats}

    # Один запрос вместо N: тянем все потенциально существующие записи разом.
    # IN по external_id не идеально сужен по source, но это не проблема —
    # ниже мы всё равно матчим по точной паре (source, external_id).
    existing_rows = (
        db.query(ThreatORM)
        .filter(
            ThreatORM.source.in_(sources),
            ThreatORM.external_id.in_(external_ids),
        )
        .all()
    )
    existing_map = {(r.source, r.external_id): r for r in existing_rows}

    inserted, updated = 0, 0
    for t in threats:
        key = (t.source, t.external_id)
        data = t.model_dump(exclude={"fetched_at"})
        # url приходит как HttpUrl -> приводим к строке
        if data.get("url") is not None:
            data["url"] = str(data["url"])

        row = existing_map.get(key)
        if row:
            for k, v in data.items():
                setattr(row, k, v)
            updated += 1
        else:
            db.add(ThreatORM(**data))
            inserted += 1

    db.commit()  # один коммит на всю пачку
    return {"inserted": inserted, "updated": updated, "total": len(threats)}
