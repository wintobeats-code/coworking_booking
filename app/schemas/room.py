"""Pydantic-схемы для комнат и слотов."""

from datetime import time

from pydantic import BaseModel


class SlotOut(BaseModel):
    """Схема слота с информацией о доступности."""

    id: int
    start_time: time
    end_time: time
    is_booked: bool = False

    model_config = {"from_attributes": True}


class RoomOut(BaseModel):
    """Схема комнаты без слотов."""

    id: int
    name: str

    model_config = {"from_attributes": True}


class RoomWithSlotsOut(BaseModel):
    """Комната со списком слотов на конкретную дату."""

    id: int
    name: str
    slots: list[SlotOut]

    model_config = {"from_attributes": True}
