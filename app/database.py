from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import os
from config import API_TOKEN  # Импортируем для проверки инициализации конфига

class Database:
    def __init__(self):
        self.engine: AsyncEngine | None = None

    async def get_engine(self) -> AsyncEngine:
        try:
            POSTGRES_USER = os.getenv('POSTGRES_USER')
            POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
            POSTGRES_DB = os.getenv('POSTGRES_DB')
            POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
            POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

            if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
                raise ValueError("Не все переменные окружения для PostgreSQL заданы!")

            DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            
            self.engine = create_async_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                echo=True
            )
            
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                print("Успешное подключение к PostgreSQL")
                
            return self.engine
            
        except SQLAlchemyError as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    async def close(self):
        if self.engine is not None:
            await self.engine.dispose()