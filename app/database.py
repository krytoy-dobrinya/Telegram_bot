from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from config import *


class Database:
    def __init__(self):
        self.engine: AsyncEngine | None = None

    # Асинхронное подключение к бд
    async def get_engine(self) -> AsyncEngine:
        try:
            # Задаем URL для подключения
            DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            
            # Создание асинхронного движка
            self.engine = create_async_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                echo=True
            )
            
            # Тестовое подключение к базе для проверки
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                print("Успешное подключение к PostgreSQL")
            return self.engine
            
        except SQLAlchemyError as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    # Закрываем подключение к бд
    async def close(self):
        if self.engine is not None:
            await self.engine.dispose()