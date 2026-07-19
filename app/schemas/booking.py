"""Pydantic-схемы для бронирования."""

from datetime import date

from pydantic import BaseModel


class BookingCreate(BaseModel):
    """Схема создания бронирования."""

    slot_id: int
    booking_date: date


class BookingOut(BaseModel):
    """Схема ответа с информацией о бронировании."""

    id: int
    user_id: int
    slot_id: int
    booking_date: date
    room_name: str
    start_time: str
    end_time: str

    model_config = {"from_attributes": True}
