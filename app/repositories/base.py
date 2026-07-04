from abc import ABC, abstractmethod
from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    """Абстрактный базовый класс репозитория, задающий интерфейс работы с БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def add(self, entity: Any) -> Any:
        """Добавить новую сущность в сессию."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Any | None:
        """Получить сущность по её уникальному ID."""
        pass
