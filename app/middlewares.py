from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from typing import Callable, Awaitable, Any, Dict
from models import Message as MessageModel
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from collections import defaultdict
from datetime import datetime, timedelta



logger = logging.getLogger(__name__)


# Для хранения данных о запросах
request_history = defaultdict(list)


# Ограничение запросов в секунду для /auth
class RateLimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Проверяем, что это сообщение и команда /auth
        if(isinstance(event.event, Message) and event.event.text and event.event.text.startswith('/auth')):
            user_id = event.event.from_user.id
            current_time = datetime.now()
            
            # Очищаем старые записи (старше 1 секунды)
            request_history[user_id] = [
                timestamp for timestamp in request_history[user_id] 
                if current_time - timestamp < timedelta(seconds=1)
            ]
            
            # Проверяем количество запросов
            if len(request_history[user_id]) >= 3:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                await event.event.answer("⚠️ Слишком много запросов! Пожалуйста, попробуйте через секунду.")
                return
            
            # Добавляем текущий запрос в историю
            request_history[user_id].append(current_time)
        
        return await handler(event, data)


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
        
        # Важно: вызываем handler в любом случае!
        return await handler(event, data)
    
    
