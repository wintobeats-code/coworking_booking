"""Роутер переговорных комнат."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.room import RoomOut, RoomWithSlotsOut
from app.services import room as room_service

router = APIRouter()


@router.get("", response_model=list[RoomOut])
def list_rooms(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Возвращает список всех переговорных комнат."""
    return room_service.get_all_rooms(db)


@router.get("/availability", response_model=list[RoomWithSlotsOut])
def rooms_availability(
    target_date: date = Query(
        ..., alias="date", description="Дата в формате YYYY-MM-DD"
    ),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Возвращает доступность слотов на указанную дату."""
    return room_service.get_rooms_availability(db, target_date)
