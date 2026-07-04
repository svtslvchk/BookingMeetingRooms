from pydantic import BaseModel, ConfigDict
from typing import Optional


class RoomCreate(BaseModel):
    name: str
    capacity: int
    description: Optional[str] = None


class RoomOut(BaseModel):
    id: int
    name: str
    capacity: int
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)