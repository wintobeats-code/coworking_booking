from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.core.dependencies import get_current_user
from app.schemas.room import RoomOut, RoomWithSlotsOut
from app.services import room as room_service

router = APIRouter()


@router.get("", response_model=list[RoomOut])
def list_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return room_service.get_all_rooms(db)


@router.get("/availability", response_model=list[RoomWithSlotsOut])
def rooms_availability(
    date: date = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return room_service.get_rooms_availability(db, date)
