from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from database import Database
from middlewares import DbSessionMiddleware, SaveMessageMiddleware
from commands import cmd_start
import asyncio
import logging
from config import API_TOKEN, GPT_TOKEN
from commands import *
import openai


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Выполняется при запуске бота
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    db = Database()
    await db.connect()
    
    # Создать сессию
    dispatcher.update.middleware(DbSessionMiddleware(db))
    
    # Использовать сессию
    dispatcher.update.middleware(SaveMessageMiddleware())
    
    # Подключение роутера
    router = Router()
    setup_commands_router(router, db)
    
    dispatcher.include_router(router)
    
    logger.info("Бот успешно запущен")

async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    logger.info("Остановка бота...")
    await dispatcher.storage.close()
    await bot.session.close()


# Подключение бота
async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())