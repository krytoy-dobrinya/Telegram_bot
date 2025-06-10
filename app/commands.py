import random
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from config import *
from sqlalchemy import text
from database import Database


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
async def cmd_start(message: types.Message):
    await message.answer("УЭЭЭЭ я СБЭУ бот!!! Как попросить помощи с командами сам догадаешься.")


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


# Объявление команд
def setup_commands_router(router: Router, db: Database) -> None:
    router.message.register(cmd_start, Command("start"))
    router.message.register(cmd_help, Command("help"))
    router.message.register(cmd_pomogi, Command("помоги"))
    router.message.register(cmd_smeshnyava, Command("смешнява"))
    router.message.register(cmd_loot, Command("лут"))
    
    # Требуется дополнительный аргумент db, поэтому используем partial
    from functools import partial
    router.message.register(
        partial(cmd_db_check, db=db),
        Command("база")
    )