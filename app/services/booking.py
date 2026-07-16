from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Booking, User, Slot, Room, UserRole


def create_booking(db: Session, slot_id: int, booking_date: date, user: User) -> Booking:
    """Создаёт бронь. Любой авторизованный юзер может бронировать."""
    # 1. Проверяем, что слот существует
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Слот не найден")

    # 2. Создаём бронь
    booking = Booking(
        user_id=user.id,
        slot_id=slot_id,
        booking_date=booking_date,
    )
    db.add(booking)

    try:
        db.commit()
    except IntegrityError:
        # Сработал UniqueConstraint(slot_id, booking_date) — слот уже занят
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот слот на указанную дату уже забронирован",
        )

    db.refresh(booking)
    return booking


def get_my_bookings(db: Session, user: User) -> list[dict]:
    """Возвращает ТОЛЬКО мои бронирования (изоляция данных!)."""
    bookings = (
        db.query(Booking)
        .join(Slot)
        .join(Room)
        .filter(Booking.user_id == user.id)
        .all()
    )
    return [
        {
            "id": b.id,
            "user_id": b.user_id,
            "slot_id": b.slot_id,
            "booking_date": b.booking_date,
            "room_name": b.slot.room.name,
            "start_time": b.slot.start_time.strftime("%H:%M"),
            "end_time": b.slot.end_time.strftime("%H:%M"),
        }
        for b in bookings
    ]


def cancel_booking(db: Session, booking_id: int, current_user: User) -> None:
    """
    Отмена брони.
    - Сотрудник может отменить ТОЛЬКО свою бронь.
    - Админ может отменить ЛЮБУЮ бронь.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")

    is_owner = booking.user_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ к чужим бронированиям запрещён",
        )

    db.delete(booking)
    db.commit()