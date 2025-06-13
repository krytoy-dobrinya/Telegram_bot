from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from typing import Callable, Awaitable, Any, Dict
from models import Message as MessageModel
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

# Класс для создания мидлвейра
class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with self.db.async_session_maker() as session:
            data["session"] = session
            return await handler(event, data)

# Класс класс сохраняющий сообщения
class SaveMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Обрабатываем только текстовые сообщения
        if isinstance(event.event, Message) and event.event.text:
            session: AsyncSession = data["session"]
            
            try:
                new_msg = MessageModel(
                    user_id=event.event.from_user.id,
                    text=event.event.text
                )
                session.add(new_msg)
                await session.commit()
                logger.info(f"Сообщение сохранено: {event.event.text[:50]}...")
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
                await session.rollback()
        
        return await handler(event, data)