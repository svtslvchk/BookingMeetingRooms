from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List
from app.models.booking import Booking


async def get_room_bookings_for_time(
    db: AsyncSession, 
    room_id: int, 
    time_start: datetime, 
    time_end: datetime
) -> List[Booking]:
    """
    Проверяет пересечение интервалов времени для конкретной комнаты.
    Формула пересечения: (Existing.time_start < New.time_end) AND (Existing.time_end > New.time_start)
    """
    stmt = select(Booking).where(
        Booking.room_id == room_id,
        Booking.time_start < time_end,
        Booking.time_end > time_start
    )
    result = await db.execute(stmt)
    return result.scalars().all()
