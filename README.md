# 🤖 СБЭУ Telegram Bot

**Бот для отправки случайных мемов ("смешнявок") и демонстрации "лута" из игры Escape from Tarkov**

## 🚀 Возможности

- Отправка случайных мемов по команде `/смешнява`
- Демонстрация "лута" из игры по команде `/лут`
- Проверка подключения к базе данных PostgreSQL по команде `/база`
- Вывод последних 10 сообщений в обратном порядке по команде `/re_chat`
- Генерирует и дает кнопку для авторизации в ВК `/auth`
- Поддержка русского языка интерфейса

## Файловая система

<pre>
.
├── .env                     # Файл с конфиденциальными переменными окружения (токены, доступы к БД)
├── .gitignore               # Список игнорируемых Git файлов (env, кэш и т.д.)
├── alembic.ini              # Конфигурация Alembic для миграций БД
├── docker-compose.yaml      # Оркестрация сервисов (PostgreSQL + бот + Alembic)
├── Dockerfile               # Сборка основного образа бота
├── Dockerfile.alembic       # Сборка образа для выполнения миграций
├── Dockerfile.server        # Сборка образа для работы сервера
├── requirements.txt         # Зависимости Python (aiogram, SQLAlchemy и др.)
└── app/
    ├── alembic/             # Папка миграций Alembic
    │   ├── versions/        # Сгенерированные файлы миграций (версионирование БД)
    │   ├── env.py           # Скрипт окружения Alembic
    │   └── script.py.mako   # Шаблон для генерации миграций
    ├── commands.py          # Обработчики команд бота (/start, /help и кастомные)
    ├── config.py            # Настройки приложения (пути, фразы, параметры БД)
    ├── database.py          # Подключение и управление PostgreSQL (асинхронное)
    ├── main.py              # Точка входа (запуск бота, настройка middleware)
    ├── middlewares.py       # Промежуточное ПО (сохранение сообщений, инжект сессий БД)
    ├── models.py            # SQLAlchemy-модели (User, Message)
    ├── server.py            # Сервер для работы авторизации в ВК
    ├── auth.html            # Окно появляющееся после успешной авторизации в ВК
    └── images/              # Локальное хранилище медиафайлов (мемы, loot-изображения)
</pre>

## 🛠 Технологии

  - aiogram - фреймворк для Telegram ботов
  - SQLAlchemy - работа с PostgreSQL
  - asyncpg - асинхронный драйвер PostgreSQL
  - python-dotenv - загрузка .env файлов
  - Alembic - миграции баз данных

## Установка

Добавить .env файл в корневую папку

Пример заполнения .env файла
```
BOT_TOKEN = Токен ТГ-бота
GPT_TOKEN = Токен ChatGPT
POSTGRES_USER = Имя пользователя в БД
POSTGRES_PASSWORD = Пароль в БД
POSTGRES_HOST = Хост в БД
POSTGRES_PORT = Порт в БД
POSTGRES_DB = Имя БД
PROXY_URL = Прокси (если требуется)
VK_CLIENT_ID = ID приложения в ВК
VK_CLIENT_SECRET = Секретный ключ от приложения ВК
VK_REDIRECT_URI = Доверенный URI от приложения ВК
```

## Запуск
```
docker-compose run alembic alembic upgrade head
docker-compose up --build
```

## Выход
```
docker-compose down -v
```
