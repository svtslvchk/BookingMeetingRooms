from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.dependencies.auth import get_current_user, get_db
from app.models.user import User
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking import BookingService, RoomAlreadyBookedError

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создает бронирование для авторизованного пользователя с валидацией пересечений."""
    try:
        booking = await BookingService.create_booking(
            db=db,
            user_id=current_user.id,
            room_id=booking_data.room_id,
            time_start=booking_data.time_start,
            time_end=booking_data.time_end
        )
        return booking
    except ValueError as e:
        # Ошибки валидации времени (в прошлом, старт >= конец)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RoomAlreadyBookedError as e:
        # Ошибка пересечения интервалов
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/my", response_model=List[BookingOut])
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает список всех бронирований текущего авторизованного пользователя."""
    stmt = (
        select(Booking)
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.time_start)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
