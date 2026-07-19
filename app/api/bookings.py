"""Роутер бронирований."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingOut
from app.services import booking as booking_service

router = APIRouter()


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создаёт бронирование слота."""
    booking = booking_service.create_booking(
        db=db,
        slot_id=data.slot_id,
        booking_date=data.booking_date,
        user=current_user,
    )
    return BookingOut(
        id=booking.id,
        user_id=booking.user_id,
        slot_id=booking.slot_id,
        booking_date=booking.booking_date,
        room_name=booking.slot.room.name,
        start_time=booking.slot.start_time.strftime("%H:%M"),
        end_time=booking.slot.end_time.strftime("%H:%M"),
    )


@router.get("/my", response_model=list[BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Возвращает список бронирований текущего пользователя."""
    return booking_service.get_my_bookings(db, current_user)


@router.delete("/{booking_id}", status_code=204)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отменяет бронирование по идентификатору."""
    booking_service.cancel_booking(db, booking_id, current_user)
