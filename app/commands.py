import random
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from config import *
from sqlalchemy import text, select
from database import Database
from sqlalchemy.ext.asyncio import AsyncSession
from models import Message, User
from sqlalchemy import desc
from functools import partial

# Открыть картинку
async def open_image(image_path, message, phrase):
    try:
        with open(image_path, "rb") as photo_file:
            await message.answer_photo(
                BufferedInputFile(
                    photo_file.read(),
                    filename=image_path.name
                ),
                caption=phrase
            )
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


# /start      
async def cmd_start(message: Message, session: AsyncSession):
    try:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(id=message.from_user.id)
            session.add(user)
            await session.commit()
            await message.answer("Добро пожаловать!")
        else:
            await message.answer("С возвращением!")
    except Exception as e:
        await session.rollback()
        await message.answer("Произошла ошибка")
        raise e


# /help
async def cmd_help(message: types.Message):
    await message.answer("Какой к черту help? Ты не русский что ли? Пиши по нашему '/помоги'")


# /помоги
async def cmd_pomogi(message: types.Message):
    help_text = """
/start - Начать работу с ботом
/help - Тут так не говорят
/помоги - А вот так тут говорят
/смешнява - Ну смешняву вкину
/лут - Покажу что вынес из рейда
/база - Проверить есть ли база
/re_chat - Кто знает что это такое...
    """
    await message.answer(help_text)


# /смешнява
async def cmd_smeshnyava(message: types.Message):
    images = [f for f in IMAGES_DIR.glob("*") 
                if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
    
    if not images:
        await message.answer("Смешнявки сегодня не будет(")
        return
        
    random_image = random.choice(images)
    random_phrase = random.choice(RANDOM_JOKE_PHRASES)
    
    await open_image(random_image, message, random_phrase)


# /лут
async def cmd_loot(message: types.Message):
    if not LOOT_IMAGE.exists():
        await message.answer("Сегодня неудачный рейд был...")
        return
    
    random_phrase = random.choice(RANDOM_LOOT_PHRASES)
    
    await open_image(LOOT_IMAGE, message, random_phrase)


# /база
async def cmd_db_check(message: types.Message, db):
    try:
        async with db.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await message.answer("База есть")
    except Exception as e:
        await message.answer(f"Сегодня без базы... : {str(e)}")


# /re_chat
async def cmd_re_chat(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Получаем последние 10 сообщений пользователя из чата с ботом
    try:
        # Получаем или создаем пользователя в БД
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, username=username)
            session.add(user)
            await session.commit()
        
        # Получаем историю сообщений (последние 10)
        messages = await session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.id))
            .limit(10)
        )
        messages = messages.scalars().all()
        
        if not messages:
            await message.answer("У вас нет сообщений в базе!")
            return
        
        
        # Формируем список сообщений в прямом порядке (от старых к новым)
        message_history = [msg.text for msg in messages]
        
        # Отправляем пользователю
        response = "Последние 10 сообщений:\n\n"
        response += "\n\n".join(f"➡ {text}" for text in message_history)
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        await session.rollback()

# Объявление команд
def setup_commands_router(router: Router, db_pool) -> None:
    router.message.register(
        partial(cmd_start, session=db_pool),
        Command("start")
    )
    
    router.message.register(cmd_help, Command("help"))
    router.message.register(cmd_pomogi, Command("помоги"))
    router.message.register(cmd_smeshnyava, Command("смешнява"))
    router.message.register(cmd_loot, Command("лут"))
    
    router.message.register(
        partial(cmd_re_chat, session=db_pool),  # Теперь передаём session
        Command("re_chat")
    )
    
    # Требуется дополнительный аргумент db_pool, поэтому используем partial
    router.message.register(
        partial(cmd_db_check, db=db_pool),
        Command("база")
    )


