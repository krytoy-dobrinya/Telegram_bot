# 🤖 СБЭУ Telegram Bot

**Бот для отправки случайных мемов ("смешнявок") и демонстрации "лута" из игры Escape from Tarkov**

## 🚀 Возможности

- Отправка случайных мемов по команде `/смешнява`
- Демонстрация "лута" из игры по команде `/лут`
- Проверка подключения к базе данных PostgreSQL по команде `/база`
- Поддержка русского языка интерфейса

## Файловая система

.  
├── Смешнявки           # Папка с мемами  
├── main.py             # Основной скрипт бота  
├── commands.py         # Обработчики команд  
├── database.py         # Работа с PostgreSQL  
├── config.py           # Конфигурация бота  
├── .env                # Переменные окружения  
├── requirements.txt    # Зависимости  
└── README.md           # Этот файл  

## 🛠 Технологии

  - aiogram - фреймворк для Telegram ботов
  - SQLAlchemy - работа с PostgreSQL
  - asyncpg - асинхронный драйвер PostgreSQL
  - python-dotenv - загрузка .env файлов

## Установка

Добавить .env файл в корневую папку

Пример заполнения .env файла
```
BOT_TOKEN=ваш_токен_бота
POSTGRES_USER=postgres
POSTGRES_PASSWORD=пароль
POSTGRES_DB=имя_базы
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
