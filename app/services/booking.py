from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.booking import get_room_bookings_for_time
from app.models.booking import Booking


class RoomAlreadyBookedError(Exception):
    """Исключение выбрасывается, если выбранный интервал времени уже занят."""
    pass


class BookingService:
    @staticmethod
    async def create_booking(
        db: AsyncSession,
        user_id: int,
        room_id: int,
        time_start: datetime,
        time_end: datetime
    ) -> Booking:
        # Убираем информацию о таймзоне (делаем datetime naive), чтобы asyncpg не ругался
        if time_start.tzinfo is not None:
            time_start = time_start.replace(tzinfo=None)
        if time_end.tzinfo is not None:
            time_end = time_end.replace(tzinfo=None)

        # 1. Валидация: время начала должно быть строго раньше времени окончания
        if time_start >= time_end:
            raise ValueError("Время начала бронирования должно быть меньше времени окончания.")

        # 2. Валидация: бронь не должна быть в прошлом времени
        if time_start < datetime.now():
            raise ValueError("Нельзя оформить бронирование на прошедшее время.")

        # 3. Валидация: проверка пересечения интервалов в репозитории
        existing_bookings = await get_room_bookings_for_time(db, room_id, time_start, time_end)
        if existing_bookings:
            raise RoomAlreadyBookedError("Выбранная комната уже занята на указанный интервал времени.")

        # 4. Создание записи
        new_booking = Booking(
            user_id=user_id,
            room_id=room_id,
            time_start=time_start,
            time_end=time_end
        )
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)
        return new_booking