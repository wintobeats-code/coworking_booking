"""Сервис комнат: получение списка и доступности слотов."""

from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.db.models import Booking, Room


def get_all_rooms(db: Session) -> list[Room]:
    """Возвращает все комнаты без информации о слотах."""
    return db.query(Room).all()


def get_rooms_availability(db: Session, target_date: date) -> list[dict]:
    """Возвращает список комнат со слотами на указанную дату."""
    booked_slots = (
        db.query(Booking.slot_id).filter(Booking.booking_date == target_date).all()
    )
    booked_slot_ids = {b.slot_id for b in booked_slots}

    rooms = db.query(Room).options(joinedload(Room.slots)).all()

    result = []
    for room in rooms:
        slots_data = []
        for slot in room.slots:
            slots_data.append(
                {
                    "id": slot.id,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                    "is_booked": slot.id in booked_slot_ids,
                }
            )
        result.append(
            {
                "id": room.id,
                "name": room.name,
                "slots": slots_data,
            }
        )
    return result
