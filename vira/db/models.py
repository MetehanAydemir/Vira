from sqlalchemy import Column, String, DateTime, Text, UUID, JSON, Integer, ForeignKey, Float, Boolean
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
    importance_score = Column(Float, default=0.5)
    reflection_count = Column(Integer, default=0)
    insight_generated = Column(Boolean, default=False)
    autonomy_tags = Column(JSONB, server_default='[]')  # lambda yerine server_default kullanıldı

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

    id = Column(UUID, primary_key=True, default=uuid.uuid4)  # user_id'yi id olarak değiştirdik
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)  # Opsiyonel e-posta alanı
    hashed_password = Column(String, nullable=False)  # Şifre hash'i
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class Interaction(Base):
    """SQLAlchemy model for conversation history (konuşma kayıtları)."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    intent_type = Column(String, nullable=True)
    metadata_v = Column(JSONB, server_default='{}')

    def __repr__(self):
        return f"<Interaction(id={self.id}, user_id={self.user_id})>"

# --- Self-Reflection için yeni modeller ---

class AutonomousInsight(Base):
    """SQLAlchemy model for autonomous insights (otonom içgörüler)."""
    __tablename__ = "autonomous_insights"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    insight_text = Column(Text, nullable=False)
    insight_type = Column(String(50))  # 'pattern_recognition', 'emotional_evolution', 'behavioral_change'
    confidence_score = Column(Float, default=0.5)
    source_memory_ids = Column(JSONB, server_default='[]')  # lambda yerine server_default kullanıldı
    created_at = Column(DateTime, server_default=func.now())
    acted_upon = Column(Boolean, default=False)
    action_results = Column(JSONB, server_default='{}')

    def __repr__(self):
        return f"<AutonomousInsight(id={self.id}, user_id={self.user_id}, type={self.insight_type})>"

class EmergentGoal(Base):
    """SQLAlchemy model for emergent goals (belirlenen hedefler)."""
    __tablename__ = "emergent_goals"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    goal_text = Column(Text, nullable=False)
    goal_type = Column(String(50))  # 'relationship_building', 'emotional_support', 'proactive_assistance'
    priority = Column(Integer, default=5)  # 1-10 arası
    status = Column(String(20), default='active')  # 'active', 'completed', 'paused'
    source_insight_id = Column(UUID, ForeignKey("autonomous_insights.id"), nullable=True)
    progress_metrics = Column(JSONB, server_default='{}')
    created_at = Column(DateTime, server_default=func.now())
    target_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<EmergentGoal(id={self.id}, user_id={self.user_id}, type={self.goal_type})>"

class ReflectionSession(Base):
    """SQLAlchemy model for reflection sessions (yansıtma oturumları)."""
    __tablename__ = "reflection_sessions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    reflection_type = Column(String(50))  # 'daily', 'weekly', 'event_triggered'
    trigger_reasons = Column(JSONB, server_default='[]')  # lambda yerine server_default kullanıldı
    analysis_results = Column(JSONB, server_default='{}')
    insights_generated = Column(Integer, default=0)
    goals_created = Column(Integer, default=0)
    reflection_depth = Column(Float, default=0.5)
    created_at = Column(DateTime, server_default=func.now())
    duration_seconds = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<ReflectionSession(id={self.id}, user_id={self.user_id}, type={self.reflection_type})>"

class PersonalityVector(Base):
    """SQLAlchemy model for personality vectors (kişilik vektörleri)."""
    __tablename__ = "personality_vectors"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    vector = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<PersonalityVector(id={self.id}, user_id={self.user_id})>"

class PersonalityJournal(Base):
    """SQLAlchemy model for personality change journal (kişilik değişim günlüğü)."""
    __tablename__ = "personality_journal"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    vector_id = Column(UUID, ForeignKey("personality_vectors.id"))
    old_vector = Column(JSONB, nullable=False)
    new_vector = Column(JSONB, nullable=False)
    delta = Column(JSONB, nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<PersonalityJournal(id={self.id}, user_id={self.user_id})>"