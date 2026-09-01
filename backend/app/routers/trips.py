from datetime import date, time, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.trip import TripDetail, TripSearchResult
from app.services.station_service import station_exists
from app.services.search_service import save_search
router = APIRouter(
    prefix="/trips",
    tags=["Trips"],
)
@router.get("/search", response_model=list[TripSearchResult],)
def search_trips(
    departure: str,
    arrival: str,
    travel_date: date,
    departure_after: time,
    db: Session = Depends(get_db),
):  
    if departure == arrival:
     raise HTTPException(
        status_code=400,
        detail="La gare de départ et la gare d'arrivée doivent être différentes.",
    )
    if not station_exists(db, departure):
     raise HTTPException(
        status_code=404,
        detail="Gare de départ introuvable.",
    )

    if not station_exists(db, arrival):
     raise HTTPException(
        status_code=404,
        detail="Gare d'arrivée introuvable.",
    )
    # Conversion de l'heure demandée en secondes depuis minuit
    departure_after_seconds = (
        departure_after.hour * 3600
        + departure_after.minute * 60
        + departure_after.second
    )

    query = text(
        """
        SELECT
            t.id AS trip_id,
            t.headsign AS train_number,

            dep_station.name AS departure_station,
            arr_station.name AS arrival_station,

            dep.departure_seconds,
            arr.arrival_seconds

        FROM gtfs_trip t

        JOIN gtfs_service_date sd
            ON sd.service_id = t.service_id

        JOIN gtfs_stop_time dep
            ON dep.trip_id = t.id

        JOIN stop_point dep_sp
            ON dep_sp.id = dep.stop_point_id

        JOIN station dep_station
            ON dep_station.id = dep_sp.station_id

        JOIN gtfs_stop_time arr
            ON arr.trip_id = t.id

        JOIN stop_point arr_sp
            ON arr_sp.id = arr.stop_point_id

        JOIN station arr_station
            ON arr_station.id = arr_sp.station_id

        WHERE
            dep_station.external_id = :departure
            AND arr_station.external_id = :arrival
            AND sd.service_date = :travel_date
            AND sd.exception_type = 1
            AND arr.stop_sequence > dep.stop_sequence
            AND dep.departure_seconds >= :departure_after_seconds

        ORDER BY dep.departure_seconds
        """
    )

    rows = db.execute(
        query,
        {
            "departure": departure,
            "arrival": arrival,
            "travel_date": travel_date,
            "departure_after_seconds": departure_after_seconds,
        },
    ).mappings().all()
    save_search(
    db=db,
    departure_external_id=departure,
    arrival_external_id=arrival,
    travel_date=travel_date,
    departure_after=departure_after,
 )

    results = []

    for row in rows:
        departure_datetime = (
            datetime.combine(
                travel_date,
                time.min,
            )
            + timedelta(seconds=row["departure_seconds"])
        )

        arrival_datetime = (
            datetime.combine(
                travel_date,
                time.min,
            )
            + timedelta(seconds=row["arrival_seconds"])
        )

        results.append(
            {
                "trip_id": row["trip_id"],
                "train_number": row["train_number"],
                "departure": row["departure_station"],
                "arrival": row["arrival_station"],
                "departure_datetime": departure_datetime,
                "arrival_datetime": arrival_datetime,
                "status": "scheduled",
            }
        )

    return results
@router.get("/{trip_id}",response_model=TripDetail,)
def get_trip_detail(
    trip_id: UUID,
    db: Session = Depends(get_db),
):
    query = text(
        """
        SELECT
            t.id AS trip_id,
            t.external_id,
            t.headsign AS train_number,
            t.service_id,

            r.short_name AS route_short_name,
            r.long_name AS route_long_name,

            st.stop_sequence,
            st.arrival_seconds,
            st.departure_seconds,

            s.name AS station_name,
            s.external_id AS station_external_id

        FROM gtfs_trip t

        JOIN route r
            ON r.id = t.route_id

        JOIN gtfs_stop_time st
            ON st.trip_id = t.id

        JOIN stop_point sp
            ON sp.id = st.stop_point_id

        JOIN station s
            ON s.id = sp.station_id

        WHERE t.id = :trip_id

        ORDER BY st.stop_sequence
        """
    )

    rows = db.execute(
        query,
        {"trip_id": trip_id},
    ).mappings().all()
    
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Trajet introuvable",
        )

    first = rows[0]
    last = rows[-1]

    def seconds_to_time(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        return f"{hours:02d}:{minutes:02d}"

    stops = []

    for row in rows:
        stops.append(
            {
                "station": row["station_name"],
                "station_external_id": row["station_external_id"],
                "stop_sequence": row["stop_sequence"],
                "arrival_time": seconds_to_time(
                    row["arrival_seconds"]
                ),
                "departure_time": seconds_to_time(
                    row["departure_seconds"]
                ),
            }
        )

    duration_minutes = (
        last["arrival_seconds"]
        - first["departure_seconds"]
    ) // 60

    return {
        "trip_id": first["trip_id"],
        "train_number": first["train_number"],
        "service_id": first["service_id"],

        "route": {
            "short_name": first["route_short_name"],
            "long_name": first["route_long_name"],
        },

        "departure_station": first["station_name"],
        "arrival_station": last["station_name"],

        "departure_time": seconds_to_time(
            first["departure_seconds"]
        ),
        "arrival_time": seconds_to_time(
            last["arrival_seconds"]
        ),

        "duration_minutes": duration_minutes,

        "stops": stops,
    }