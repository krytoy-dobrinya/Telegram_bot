import random
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BufferedInputFile
from config import *
from sqlalchemy import text, select
from database import Database
from sqlalchemy.ext.asyncio import AsyncSession
from models import Message, User
from sqlalchemy import desc
from functools import partial
import logging
from openai import AsyncOpenAI
from config import VK_CLIENT_ID, VK_REDIRECT_URI




logger = logging.getLogger(__name__)

# Инициализация клиента
client = AsyncOpenAI(api_key=GPT_TOKEN)

# Функция отправки картинки
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
async def cmd_start(message: types.Message, session: AsyncSession):
    try:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(id=message.from_user.id, username=message.from_user.username)
            session.add(user)
            await session.commit()  # Явный commit для гарантии
            await message.answer("Добро пожаловать!")
        else:
            await message.answer("С возвращением!")
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка в /start: {e}")
        await message.answer("Произошла ошибка при регистрации")


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
/auth - авторизация в ВК
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
    
    try:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, username=username)
            session.add(user)
            await session.commit()
        
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
        
        message_history = [msg.text for msg in messages]
        response = "Последние 10 сообщений:\n\n"
        response += "\n\n".join(f"➡ {text}" for text in message_history)
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        await session.rollback()


# /Взаимодействие с ChatGPT
async def get_chatgpt_response(text: str, user_id: int, session: AsyncSession) -> str:
    try:
        # Получаем историю сообщений
        messages = await session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.id))
            .limit(5)
        )
        
        # Формируем chat_history
        chat_history = [
            {"role": "system", "content": GPT_LORE}
        ] + [
            {"role": "user", "content": msg.text.strip()}
            for msg in messages.scalars().all()
            if msg.text and msg.text.strip()
        ]
        
        # Добавляем текущее сообщение
        chat_history.append({"role": "user", "content": text.strip()})
        
        # Отправка запроса (с await!)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Ошибка ChatGPT: {e}")
        return "Извините, не могу ответить сейчас."


# /auth - отправляет ссылку для авторизации через VK
async def cmd_auth(message: types.Message):
    try:
        client_id = VK_CLIENT_ID
        redirect_uri = VK_REDIRECT_URI
        scope = "offline"  # offline для получения refresh_token
        
        # Формируем URL для авторизации в точном требуемом формате
        auth_url = f'https://oauth.vk.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&state={message.from_user.id}'
        
        # Создаем кнопку для авторизации
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="🔑 Авторизоваться через VK",
            url=auth_url
        ))
        
        await message.answer(
            "Для авторизации через VK нажмите кнопку ниже:",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Ошибка в /auth: {e}")
        await message.answer("Произошла ошибка при создании ссылки авторизации")
    


# /Обычное сообщение без команды
async def handle_regular_message(message: types.Message, session: AsyncSession):
    if message.text.startswith('/'):
        return  # Игнорируем команды
    
    try:
        response = await get_chatgpt_response(
            message.text, 
            message.from_user.id, 
            session
        )
        await message.answer(response)
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer("Произошла ошибка при обработке сообщения")





# Настройка роутера команд
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
        partial(cmd_re_chat, session=db_pool),
        Command("re_chat")
    )
    router.message.register(
        partial(cmd_db_check, db=db_pool),
        Command("база")
    )
    
    router.message.register(cmd_auth, Command("auth"))
    
    # Регистрируем обработчик обычных сообщений
    router.message.register(
        partial(handle_regular_message, session=db_pool)
    )
    
