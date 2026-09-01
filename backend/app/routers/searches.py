from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased

from app.database import get_db
from app.models import Search, Station


router = APIRouter(
    prefix="/searches",
    tags=["Searches"],
)


@router.get("/history")
def get_search_history(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    departure_station = aliased(Station)
    arrival_station = aliased(Station)

    rows = (
        db.query(
            Search.id,
            Search.travel_date,
            Search.departure_after,
            Search.search_datetime,

            departure_station.name.label("departure"),
            departure_station.external_id.label(
                "departure_external_id"
            ),

            arrival_station.name.label("arrival"),
            arrival_station.external_id.label(
                "arrival_external_id"
            ),
        )
        .join(
            departure_station,
            departure_station.id == Search.departure_station_id,
        )
        .join(
            arrival_station,
            arrival_station.id == Search.arrival_station_id,
        )
        .order_by(Search.search_datetime.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": row.id,
            "departure": row.departure,
            "departure_external_id": row.departure_external_id,
            "arrival": row.arrival,
            "arrival_external_id": row.arrival_external_id,
            "travel_date": row.travel_date,
            "departure_after": row.departure_after,
            "search_datetime": row.search_datetime,
        }
        for row in rows
    ]