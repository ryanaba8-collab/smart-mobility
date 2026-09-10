from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


# =========================================================
# STATION
# =========================================================

class Station(Base):
    __tablename__ = "station"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    external_id = Column(
        String(100),
        unique=True,
        nullable=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    city = Column(
        String(100),
        nullable=True,
    )

    latitude = Column(
        Numeric(9, 6),
        nullable=True,
    )

    longitude = Column(
        Numeric(9, 6),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
    )


# =========================================================
# TRAIN TYPE
# =========================================================

class TrainType(Base):
    __tablename__ = "train_type"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    name = Column(
        String(50),
        nullable=False,
    )

    max_speed = Column(
        Integer,
    )

    capacity = Column(
        Integer,
    )

    created_at = Column(
        DateTime,
        nullable=False,
    )


# =========================================================
# TRAIN
# =========================================================

class Train(Base):
    __tablename__ = "train"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    train_number = Column(
        String(20),
        nullable=False,
    )

    train_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("train_type.id"),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
    )


# =========================================================
# LINE
# =========================================================

class Line(Base):
    __tablename__ = "line"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

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

    distance_km = Column(
        Numeric(8, 2),
    )


# =========================================================
# TRIP
# =========================================================

class Trip(Base):
    __tablename__ = "trip"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

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

    departure_datetime = Column(
        DateTime,
        nullable=False,
    )

    arrival_datetime = Column(
        DateTime,
        nullable=False,
    )

    price = Column(
        Numeric(8, 2),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
    )


# =========================================================
# SEARCH
# =========================================================

class Search(Base):
    __tablename__ = "search"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

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

    travel_date = Column(
        Date,
        nullable=False,
    )

    departure_after = Column(
        Time,
        nullable=False,
    )

    search_datetime = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


# =========================================================
# CONVERSATION
# =========================================================

class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    session_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


# =========================================================
# CONVERSATION MESSAGE
# =========================================================

class ConversationMessage(Base):
    __tablename__ = "conversation_message"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "conversation.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role = Column(
        String(50),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )