import random
from pathlib import Path
from aiogram import types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from config import *
from sqlalchemy import text
from database import Database
from sqlalchemy.exc import SQLAlchemyError


db = Database()

async def cmd_start(message: types.Message):
    await message.answer("УЭЭЭЭ я СБЭУ бот!!!")

async def cmd_help(message: types.Message):
    await message.answer("Какой к черту help? Ты не русский что ли? Пиши по нашему '/помоги'")

async def cmd_pomogi(message: types.Message):
    help_text = """
/start - Начать работу с ботом
/help - Тут так не говорят
/помоги - А вот так тут говорят
/смешнява - Ну смешняву вкину
/лут - Покажу что вынес из рейда
/база - Проверить есть ли база
    """
    await message.answer(help_text)

async def cmd_smeshnyava(message: types.Message):
    try:
        images = [f for f in IMAGES_DIR.glob("*") 
                 if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
        
        if not images:
            await message.answer("Смешнявки сегодня не будет(")
            return
            
        random_image = random.choice(images)
        random_phrase = random.choice(RANDOM_JOKE_PHRASES)
        
        with open(random_image, "rb") as photo_file:
            await message.answer_photo(
                BufferedInputFile(
                    photo_file.read(),
                    filename=random_image.name
                ),
                caption=random_phrase
            )
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

async def cmd_loot(message: types.Message):
    try:
        if not LOOT_IMAGE.exists():
            await message.answer("Сегодня неудачный рейд был...")
            return
            
        random_phrase = random.choice(RANDOM_LOOT_PHRASES)
        
        with open(LOOT_IMAGE, "rb") as photo_file:
            await message.answer_photo(
                BufferedInputFile(
                    photo_file.read(),
                    filename="лут.jpg"
                ),
                caption=random_phrase
            )
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

async def cmd_db_check(message: types.Message, db):
    try:
        async with db.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await message.answer("База есть")
    except Exception as e:
        await message.answer(f"Сегодня без базы... : {str(e)}")




def setup_commands_router(router, db):
    router.message.register(cmd_start, Command("start"))
    router.message.register(cmd_help, Command("help"))
    router.message.register(cmd_pomogi, Command("помоги"))
    router.message.register(cmd_smeshnyava, Command("смешнява"))
    router.message.register(cmd_loot, Command("лут"))
    
    from functools import partial
    router.message.register(
        partial(cmd_db_check, db=db),
        Command("база")
    )