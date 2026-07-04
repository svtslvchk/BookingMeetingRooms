from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:postgres_pass@localhost:5433/booking_db"

# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Логирование всех SQL-запросов в консоль
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Базовый класс для ORM-моделей
Base = declarative_base()
