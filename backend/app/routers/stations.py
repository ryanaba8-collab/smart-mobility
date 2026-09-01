from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Station


router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
)


@router.get("/search")
def search_stations(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    stations = (
        db.query(Station)
        .filter(
            Station.external_id.isnot(None),
            Station.name.ilike(f"%{q}%"),
        )
        .order_by(Station.name)
        .limit(limit)
        .all()
    )

    return stations


@router.get("")
def get_stations(db: Session = Depends(get_db)):
    stations = (
        db.query(Station)
        .filter(Station.external_id.isnot(None))
        .order_by(Station.name)
        .all()
    )

    return stations