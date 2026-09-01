from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TripSearchResult(BaseModel):
    trip_id: UUID
    train_number: str | None
    departure: str
    arrival: str
    departure_datetime: datetime
    arrival_datetime: datetime
    status: str

from typing import List


class TripStop(BaseModel):
    station: str
    station_external_id: str | None
    stop_sequence: int
    arrival_time: str
    departure_time: str


class TripRoute(BaseModel):
    short_name: str | None
    long_name: str | None


class TripDetail(BaseModel):
    trip_id: UUID
    train_number: str | None
    service_id: str

    route: TripRoute

    departure_station: str
    arrival_station: str

    departure_time: str
    arrival_time: str

    duration_minutes: int

    stops: List[TripStop]    