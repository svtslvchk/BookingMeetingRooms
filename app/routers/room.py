from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.dependencies.auth import get_db
from app.models.room import Room
from app.models.booking import Booking
from app.schemas.room import RoomCreate, RoomOut
from app.schemas.booking import BookingOut

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
async def create_room(room_data: RoomCreate, db: AsyncSession = Depends(get_db)):
    """Создает новую переговорную комнату (открытый эндпоинт)."""
    new_room = Room(
        name=room_data.name,
        capacity=room_data.capacity,
        description=room_data.description
    )
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room


@router.get("", response_model=List[RoomOut])
async def get_rooms(db: AsyncSession = Depends(get_db)):
    """Возвращает список всех доступных переговорных комнат."""
    stmt = select(Room)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{room_id}/bookings", response_model=List[BookingOut])
async def get_room_bookings(room_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех будущих бронирований для конкретной комнаты.
    Бронирования, которые уже завершились, в список не попадают.
    """
    stmt = (
        select(Booking)
        .where(
            Booking.room_id == room_id,
            Booking.time_end >= datetime.now()
        )
        .order_by(Booking.time_start)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
