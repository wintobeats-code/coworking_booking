from datetime import date
from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    slot_id: int
    booking_date: date


class BookingOut(BaseModel):
    id: int
    user_id: int
    slot_id: int
    booking_date: date
    room_name: str
    start_time: str
    end_time: str

    model_config = {"from_attributes": True}
