import os
from pathlib import Path
from dotenv import load_dotenv


# Загрузка .env
load_dotenv()


# Проверка токена бота
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("Токен бота не найден в .env файле!")

# Проверка токена ChatGPT
GPT_TOKEN = os.getenv('GPT_TOKEN')
if not GPT_TOKEN:
    raise ValueError("Токен GPT не найден в .env файле!")


# Проверка данных из бд
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("Не все переменные окружения для PostgreSQL заданы!")


# Пути
IMAGES_DIR = Path("images")
LOOT_IMAGE = IMAGES_DIR / "loot.jpg"


# Подключение прокси
PROXY_URL = os.getenv("PROXY_URL")
os.environ["http_proxy"] = PROXY_URL
os.environ["https_proxy"] = PROXY_URL


# Рандомные фразы
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

# Предустановка ChatGPT
GPT_LORE = """
Ты СБЭУ(Симуляция Боя в Экстремальных Условиях) Помощник.
Ты должен отвечать в соответствии с лором Escape from Tarkov.
Пиши небольшие ответы (не больше 3-4 предложений). 
Используй фразы, который используют Дикие, ЧВК BEAR и боссы игры.
"""
