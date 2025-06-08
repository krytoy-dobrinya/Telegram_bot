import os
import asyncio
import random
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError



# Загрузка переменных окруженияw
load_dotenv()

# Токен моего СБЭУ Бота
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("Токен бота не найден в .env файле!")

# Данные для PostgreSQL
def get_database_engine():
    try:
        # Получаем переменные окружения с проверкой
        POSTGRES_USER = os.getenv('POSTGRES_USER')
        POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
        POSTGRES_DB = os.getenv('POSTGRES_DB')
        POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
        POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

        if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
            raise ValueError("Не все обязательные переменные окружения для PostgreSQL заданы!")

        # Формируем строку подключения
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # Создаём движок с настройками
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            echo=True 
        )
        
        # Проверяем подключение (используем text() для SQL-запросов)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Успешное подключение к PostgreSQL")
            
        return engine
        
    except SQLAlchemyError as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        raise

# Инициализация подключения
engine = get_database_engine()

# Инициализация бота
bot = Bot(token=API_TOKEN) 
dp = Dispatcher()

# --------------------------------------------------------------------------------------------------------------------------------
# Инициализации

# Путь к папке со смешнявками
IMAGES_DIR = Path("Смешнявки")

# Список рандомных фраз для смешнявок
RANDOM_JOKE_PHRASES = [
    "Лови подарочек",
    "Держи, служивый",
    "Держи",
    "Есть такое",
    "Лови",
    "Этот ваще крутой",
    "Лучше не найдешь",
    "Вот этот смешной"
]

# Список рандомных фраз лутания
RANDOM_LOOT_PHRASES = [
    "Смотрите что с лабы вынес",
    "Смотрите что с таможни вынес",
    "Смотрите что с развязки вынес",
    "Смотрите что с улиц таркова вынес",
    "Смотрите что из леса вынес",
    "Смотрите что с берега вынес",
    "Смотрите что с резерва вынес",
    "Смотрите что с эпицентра вынес",
    "Смотрите что с маяка вынес"
]

# --------------------------------------------------------------------------------------------------------------------------------
# Команды бота

# /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("УЭЭЭЭ я СБЭУ бот!!!")

# /help
@dp.message(Command("help"))
async def send_welcome(message: types.Message):
    await message.answer("Какой к черту help? Ты не русский что ли? Пиши по нашему '/помоги'")

# /помоги
@dp.message(Command("помоги"))
async def send_welcome(message: types.Message):
    help_text = """
/start - Начать работу с ботом
/help - Тут так не говорят
/помоги - А вот так тут говорят
/смешнява - Ну смешняву вкину
/лут - Покажу что вынес из рейда
/база - Проверить есть ли база
    """
    await message.answer(help_text)


# /смешнява
@dp.message(Command("смешнява"))
async def send_smeshnyava(message: types.Message):
    try:
        # Получаем список картинок
        images = [
            f for f in IMAGES_DIR.glob("*")
            if f.suffix.lower() in (".jpg", ".jpeg", ".png")
        ]
        if not images:
            await message.answer("Смешнявки сегодня не будет(")
            return
            
        # Выбираем случайное фото и случайную фразу
        random_image = random.choice(images)
        random_phrase = random.choice(RANDOM_JOKE_PHRASES)
        
        # Отправляем фото
        with open(random_image, "rb") as photo_file:
            await message.answer_photo(
                types.BufferedInputFile(photo_file.read(), filename=random_image.name),
                caption=random_phrase
            )
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


# /лут
@dp.message(Command("лут"))
async def send_loot(message: types.Message):
    try:
        # Указываем полный путь к файлу
        loot_image = Path("лут.jpg")
        
        # Проверяем существование файла
        if not loot_image.exists():
            await message.answer("Сегодня неудачный рейд был...")
            return
            
        # Выбираем случайную фразу
        random_phrase = random.choice(RANDOM_LOOT_PHRASES)
        
        # Отправляем фото (правильный способ)
        with open(loot_image, "rb") as photo_file:
            await message.answer_photo(
                types.BufferedInputFile(
                    photo_file.read(),
                    filename="лут.jpg" 
                ),
                caption=random_phrase
            )
            
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        
# /база
@dp.message(Command("база"))
async def check_db(message: types.Message):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            await message.answer("База есть.")
    except SQLAlchemyError as e:
        await message.answer(f"Сегодня без базы: {e}")


# --------------------------------------------------------------------------------------------------------------------------------
# Запуск бота
async def main():
    # Инициализация подключения к БД
    try:
        engine = get_database_engine()
        
        # Ваш код запуска бота
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
