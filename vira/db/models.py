from sqlalchemy import Column, String, DateTime, Text, UUID, JSON, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class LongTermMemory(Base):
    """SQLAlchemy model for long-term memory storage (uzun süreli hafıza)."""
    __tablename__ = "long_term_memory"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    metadatas = Column(JSONB, server_default='{}')
    embedding = Column(Vector(1536), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<LongTermMemory(id={self.id}, content={self.content[:30]}...)>"

class ShortTermMemory(Base):
    """SQLAlchemy model for short-term memory storage (kısa süreli hafıza)."""
    __tablename__ = "short_term_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ShortTermMemory(id={self.id}, session_id={self.session_id})>"

class User(Base):
    """SQLAlchemy model for user information (kullanıcı bilgileri)."""
    __tablename__ = "users"

    user_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"

class Interaction(Base):
    """SQLAlchemy model for conversation history (konuşma kayıtları)."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey("users.user_id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Interaction(id={self.id}, user_id={self.user_id})>"