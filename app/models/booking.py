from datetime import datetime
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False
    )
    time_start: Mapped[datetime] = mapped_column(nullable=False)
    time_end: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (
        Index("idx_bookings_user_id", "user_id"),
        Index("idx_bookings_room_time", "room_id", "time_start", "time_end"),
    )
