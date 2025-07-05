import numpy as np
from sqlalchemy import text
from contextlib import contextmanager
from vira.db.engine import db_session
from vira.db.models import LongTermMemory, Interaction, ShortTermMemory
from vira.utils.logger import get_logger
from sqlalchemy import text, select, and_, desc
from typing import List, Tuple
from datetime import datetime

logger = get_logger(__name__)


class MemoryRepository:
    """Repository for memory operations using SQLAlchemy."""

    def store_memory(self, user_id: str, content: str, embedding: np.ndarray):
        """Store a memory entry with its embedding in the database."""
        try:
            # Use the context manager for session management
            with db_session() as session:
                # Store user_id in meta_data field
                metadatas = {'user_id': user_id}

                memory = LongTermMemory(
                    content=content,
                    metadatas=metadatas,  # Changed from metadata to meta_data
                    embedding=embedding.tolist()
                )
                session.add(memory)
                # No need to commit here, the context manager will do it

                # Refresh to get the ID (still within the transaction)
                session.flush()
                memory_id = memory.id

            # Session is now committed and closed
            logger.info(f"Memory stored with ID: {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    def retrieve_similar_memories(self, user_id: str, embedding: np.ndarray, top_k: int = 3):
        """Retrieve the most similar memories based on embedding similarity."""
        try:
            with db_session() as session:
                # Using raw SQL with SQLAlchemy for vector similarity search
                # Filter by user_id in meta_data field
                memories = session.scalars(
                    select(LongTermMemory)
                    .filter(LongTermMemory.metadatas['user_id'].astext == user_id)
                    .order_by(LongTermMemory.embedding.cosine_distance(embedding.tolist()))
                    .limit(top_k)
                ).all()
                result = []
                for memory in memories:
                    # Cosine similarity = 1 - cosine distance
                    distance = session.scalar(
                        select(LongTermMemory.embedding.cosine_distance(embedding.tolist()))
                        .where(LongTermMemory.id == memory.id)
                    )
                    similarity = 1 - distance
                    result.append((memory.content, float(similarity), memory.created_at))

            logger.info(f"Retrieved {len(result)} similar memories for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve similar memories: {e}")
            return []

    def get_recent_conversations(self, user_id: str, session_id: str = None, limit: int = 5) -> List[
        Tuple[str, str, datetime]]:
        """
        Kullanıcının son konuşmalarını kronolojik sırayla getirir.

        Öncelikle ShortTermMemory tablosundan session_id ile ilişkili kayıtları arar.
        Eğer yoksa veya session_id belirtilmemişse, Interaction tablosundan user_id'ye göre arama yapar.

        Args:
            user_id: Kullanıcı kimliği
            session_id: Oturum kimliği (opsiyonel)
            limit: Getirilecek maksimum konuşma sayısı

        Returns:
            List[Tuple[str, str, datetime]]: (kullanıcı_mesajı, sistem_yanıtı, tarih) üçlülerinden oluşan liste
        """
        try:
            with db_session() as session:
                # Önce ShortTermMemory tablosunda ara (eğer session_id belirtilmişse)
                if session_id:
                    short_term_memories = session.scalars(
                        select(ShortTermMemory)
                        .filter(ShortTermMemory.session_id == session_id)
                        .order_by(desc(ShortTermMemory.created_at))
                        .limit(limit * 2)  # Kullanıcı ve sistem mesajları için 2 katı kayıt gerekebilir
                    ).all()

                    if short_term_memories:
                        # ShortTermMemory'den konuşma çiftleri oluştur
                        conversations = []
                        for i in range(0, len(short_term_memories) - 1, 2):
                            if i + 1 < len(short_term_memories):
                                # Kullanıcı mesajı ve sistem yanıtı olarak varsayalım
                                # Not: Gerçek uygulamada mesaj türünü belirten bir alan olmalı
                                user_message = short_term_memories[i].content
                                system_response = short_term_memories[i + 1].content
                                created_at = short_term_memories[i].created_at
                                conversations.append((user_message, system_response, created_at))

                        # En fazla limit kadar konuşma döndür
                        return conversations[:limit]

                # ShortTermMemory'de bulunamazsa veya session_id belirtilmemişse, Interaction tablosunda ara
                interactions = session.scalars(
                    select(Interaction)
                    .filter(Interaction.user_id == user_id)
                    .order_by(desc(Interaction.created_at))
                    .limit(limit)
                ).all()

                conversations = [(interaction.message, interaction.response, interaction.created_at)
                                 for interaction in interactions]

                logger.info(f"Retrieved {len(conversations)} recent conversations for user {user_id}")
                return conversations

        except Exception as e:
            logger.error(f"Failed to retrieve recent conversations: {e}")
            return []