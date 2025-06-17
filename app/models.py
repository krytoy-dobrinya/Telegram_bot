from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum


Base = declarative_base()


# Роли пользователей
class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"


# Класс пользователя
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Добавляем новые поля для VK OAuth
    vk_code_verifier = Column(String, nullable=True)
    vk_access_token = Column(String, nullable=True)
    vk_refresh_token = Column(String, nullable=True)
    vk_user_id = Column(Integer, nullable=True)
    
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")


# Класс сообщений
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False, comment="Текст сообщения")
    
    user = relationship("User", back_populates="messages")

