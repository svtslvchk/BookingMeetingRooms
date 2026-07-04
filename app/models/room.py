from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)