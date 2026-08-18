from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Station(Base):
    __tablename__ = "station"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class TrainType(Base):
    __tablename__ = "train_type"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(50), nullable=False)
    max_speed = Column(Integer)
    capacity = Column(Integer)
    created_at = Column(DateTime, nullable=False)


class Train(Base):
    __tablename__ = "train"

    id = Column(UUID(as_uuid=True), primary_key=True)
    train_number = Column(String(20), nullable=False)
    train_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("train_type.id"),
        nullable=False,
    )
    status = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False)


class Line(Base):
    __tablename__ = "line"

    id = Column(UUID(as_uuid=True), primary_key=True)
    departure_station_id = Column(
        UUID(as_uuid=True),
        ForeignKey("station.id"),
        nullable=False,
    )
    arrival_station_id = Column(
        UUID(as_uuid=True),
        ForeignKey("station.id"),
        nullable=False,
    )
    distance_km = Column(Numeric(8, 2))


class Trip(Base):
    __tablename__ = "trip"

    id = Column(UUID(as_uuid=True), primary_key=True)
    line_id = Column(
        UUID(as_uuid=True),
        ForeignKey("line.id"),
        nullable=False,
    )
    train_id = Column(
        UUID(as_uuid=True),
        ForeignKey("train.id"),
        nullable=False,
    )
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)
    price = Column(Numeric(8, 2), nullable=False)
    status = Column(String(30), nullable=False)