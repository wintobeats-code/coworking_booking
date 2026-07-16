from datetime import time, date
from pydantic import BaseModel


class SlotOut(BaseModel):
    id: int
    start_time: time
    end_time: time
    is_booked: bool = False  # для отображения доступности на дату

    model_config = {"from_attributes": True}


class RoomOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class RoomWithSlotsOut(BaseModel):
    """Комната со списком слотов на конкретную дату."""
    id: int
    name: str
    slots: list[SlotOut]

    model_config = {"from_attributes": True}
