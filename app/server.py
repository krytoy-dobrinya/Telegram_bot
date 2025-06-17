# server.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import logging
from fastapi.responses import FileResponse
from config import VK_CLIENT_ID, VK_CLIENT_SECRET, VK_REDIRECT_URI
from database import Database
from models import User



app = FastAPI()
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()


# Обработка запуска бд
@app.on_event("startup")
async def startup():
    await db.connect()


# Обработка завершения бд
@app.on_event("shutdown")
async def shutdown():
    await db.close()


# Обрабатывает callback от VK OAuth.
@app.get("/vk/callback")
async def vk_callback(request: Request, code: str, state: str):
    try:
        # Получаем user_id из state
        user_id = int(state)
        
        # Обмениваем код на токен
        token_url = "https://oauth.vk.com/access_token"
        params = {
            "client_id": VK_CLIENT_ID,
            "client_secret": VK_CLIENT_SECRET,
            "redirect_uri": VK_REDIRECT_URI,
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(token_url, params=params)
            response.raise_for_status()
            token_data = response.json()
            
            # Сохраняем токены в базу
            async with db.async_session_maker() as session:
                user = await session.get(User, user_id)
                if not user:
                    user = User(id=user_id, username=None)
                    session.add(user)
                
                user.vk_access_token = token_data.get("access_token")
                user.vk_refresh_token = token_data.get("refresh_token")
                user.vk_user_id = token_data.get("user_id")
                
                await session.commit()
        
        # Выводим окно успеха
        return FileResponse("auth.html")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))