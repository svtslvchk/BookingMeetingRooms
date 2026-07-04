from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BookingCreate(BaseModel):
    room_id: int
    time_start: datetime
    time_end: datetime


class BookingOut(BaseModel):
    id: int
    room_id: int
    user_id: int
    time_start: datetime
    time_end: datetime

    model_config = ConfigDict(from_attributes=True)