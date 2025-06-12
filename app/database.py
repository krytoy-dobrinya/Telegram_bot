from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import *
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

class Database:
    def __init__(self):
        self._engine = None
        self._async_session_maker = None

    # Устанавливает подключение к базе данных
    async def connect(self):
        try:
            self._engine = create_async_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                echo=True,
                pool_size=20,
                max_overflow=10
            )
            
            self._async_session_maker = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                autoflush=False,
                class_=AsyncSession
            )
            
            # Проверка подключения
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Успешное подключение к PostgreSQL")
                
        except SQLAlchemyError as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    @property # Превращает метод класса в атрибут
    def engine(self):
        if not self._engine:
            raise RuntimeError("База данных недоступна")
        return self._engine

    @property
    def async_session_maker(self):
        if not self._async_session_maker:
            raise RuntimeError("Сессия базы данных недоступна")
        return self._async_session_maker

    # Создает асинхронную сессию
    async def get_db_session(self) -> AsyncSession:
        return self.async_session_maker()

    # Закрывает все соединения с базой данных
    async def close(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._async_session_maker = None
            logger.info("Соединение с PostgreSQL закрыто")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()