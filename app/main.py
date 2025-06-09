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
        await db.get_engine()  # Явная инициализация соединения
        
        # Настройка роутеров
        main_router = Router()
        commands_router = Router()
        
        # Регистрация команд с передачей db
        setup_commands_router(commands_router, db)
        
        dp.include_router(main_router)
        main_router.include_router(commands_router)
        
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())