import asyncio
from aiogram import Bot, Dispatcher, Router
from config import API_TOKEN
from database import Database
from commands import setup_commands_router


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    # Инициализация БД
    db = Database()
    try:
        # Явная инициализация соединения
        await db.get_engine()  
        
        # Настройка роутеров
        commands_router = Router()
        
        # Регистрация команд с передачей db
        setup_commands_router(commands_router, db)
        dp.include_router(commands_router)
        
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())