from datetime import date, time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Line, Station, Train, Trip


router = APIRouter(
    prefix="/trips",
    tags=["Trips"],
)
@router.get("/search")
def search_trips(
    departure: str,
    arrival: str,
    travel_date: date,
    departure_after: time,
    db: Session = Depends(get_db),
):
    departure_station = db.query(Station).filter(
        Station.name == departure
    ).first()

    arrival_station = db.query(Station).filter(
        Station.name == arrival
    ).first()

    if not departure_station or not arrival_station:
        return []

    trips = (
        db.query(Trip, Train)
        .join(Train, Trip.train_id == Train.id)
        .join(Line, Trip.line_id == Line.id)
        .filter(
            Line.departure_station_id == departure_station.id,
            Line.arrival_station_id == arrival_station.id,
        )
        .all()
    )

    results = []

    for trip, train in trips:
        if (
            trip.departure_datetime.date() == travel_date
            and trip.departure_datetime.time() >= departure_after
        ):
            results.append(
                {
                    "trip_id": trip.id,
                    "train_number": train.train_number,
                    "departure": departure,
                    "arrival": arrival,
                    "departure_datetime": trip.departure_datetime,
                    "arrival_datetime": trip.arrival_datetime,
                    "price": float(trip.price),
                    "status": trip.status,
                }
            )

    return results
@router.get("/{trip_id}")
def get_trip_detail(
    trip_id: UUID,
    db: Session = Depends(get_db),
):
    result = (
        db.query(Trip, Train, Line)
        .join(Train, Trip.train_id == Train.id)
        .join(Line, Trip.line_id == Line.id)
        .filter(Trip.id == trip_id)
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Trajet introuvable",
        )

    trip, train, line = result

    departure_station = (
        db.query(Station)
        .filter(Station.id == line.departure_station_id)
        .first()
    )

    arrival_station = (
        db.query(Station)
        .filter(Station.id == line.arrival_station_id)
        .first()
    )

    duration_minutes = int(
        (
            trip.arrival_datetime - trip.departure_datetime
        ).total_seconds()
        / 60
    )

    return {
        "trip_id": trip.id,
        "train_number": train.train_number,
        "departure_station": departure_station.name,
        "arrival_station": arrival_station.name,
        "departure_datetime": trip.departure_datetime,
        "arrival_datetime": trip.arrival_datetime,
        "duration_minutes": duration_minutes,
        "distance_km": float(line.distance_km),
        "price": float(trip.price),
        "status": trip.status,
    }
