# tests/conftest.py

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1. Конфигурируем чистый тестовый движок
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres_pass@localhost:5433/booking_db_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


# 2. ПОДМЕНА: Импортируем модуль базы данных ДО загрузки приложения
from app import database

# Перебиваем оригинальные движок и фабрику сессий прямо в модуле app/database.py
database.engine = test_engine
database.AsyncSessionLocal = test_session_maker


# 3. Теперь импортируем само приложение и Base. 
# Твоя функция get_db теперь автоматически завязана на тестовую сессию.
from app.main import app
from app.database import Base


@pytest.fixture(scope="session", autouse=True)
async def init_test_db():
    """Дропаем и создаем таблицы в ТЕСТОВОЙ базе перед началом прогона."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clean_database():
    """Очищаем данные из таблиц тестовой БД после каждого отдельного теста."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для отправки запросов в тестах."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac