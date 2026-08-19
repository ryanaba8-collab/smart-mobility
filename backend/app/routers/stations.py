from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Station


router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
)


@router.get("")
def get_stations(db: Session = Depends(get_db)):
    stations = db.query(Station).all()

    return stations