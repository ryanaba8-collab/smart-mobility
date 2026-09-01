from datetime import date, time

from sqlalchemy.orm import Session

from app.models import Search, Station


def save_search(
    db: Session,
    departure_external_id: str,
    arrival_external_id: str,
    travel_date: date,
    departure_after: time,
):
    departure_station = (
        db.query(Station)
        .filter(Station.external_id == departure_external_id)
        .first()
    )

    arrival_station = (
        db.query(Station)
        .filter(Station.external_id == arrival_external_id)
        .first()
    )

    if not departure_station or not arrival_station:
        return

    search = Search(
        departure_station_id=departure_station.id,
        arrival_station_id=arrival_station.id,
        travel_date=travel_date,
        departure_after=departure_after,
    )

    db.add(search)
    db.commit()