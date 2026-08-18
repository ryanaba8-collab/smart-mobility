from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Station
from fastapi.middleware.cors import CORSMiddleware

from datetime import date, time

from app.models import Line, Station, Train, Trip
app = FastAPI(
    title="Smart Mobility API",
    description="Backend API for the Smart Mobility Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "application": "Smart Mobility",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health/database")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )

        database_name = result.scalar()

    return {
        "database": database_name,
        "status": "connected",
    }


@app.get("/stations")
def get_stations(db: Session = Depends(get_db)):
    stations = db.query(Station).all()

    return stations
@app.get("/trips/search")
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