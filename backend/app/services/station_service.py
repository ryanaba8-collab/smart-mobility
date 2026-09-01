from sqlalchemy.orm import Session

from app.models import Station


def station_exists(
    db: Session,
    external_id: str,
) -> bool:
    return (
        db.query(Station.id)
        .filter(Station.external_id == external_id)
        .first()
        is not None
    )