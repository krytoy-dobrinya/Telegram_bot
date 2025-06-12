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
    username = Column(String, nullable=True, comment="Username в Telegram")
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")


# Класс сообщений
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False, comment="Текст сообщения")
    
    user = relationship("User", back_populates="messages")

