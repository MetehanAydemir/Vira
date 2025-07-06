import json
from typing import Dict, List, Tuple
import numpy as np
from sqlalchemy import select, desc
from contextlib import contextmanager
from datetime import datetime

from vira.db.engine import db_session
from vira.db.models import (
    LongTermMemory,
    Interaction,
    ShortTermMemory,
    PersonalityVector,
    PersonalityJournal
)
from vira.utils.logger import get_logger

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
                    metadatas=metadatas,
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


class PersonalityRepository:
    """Kişilik vektörlerini yönetmek için SQLAlchemy repository sınıfı."""

    def get_personality_vector(self, user_id: str) -> Dict[str, float]:
        """
        Kullanıcının en güncel kişilik vektörünü alır.

        Args:
            user_id: Kullanıcı kimliği

        Returns:
            Kişilik vektörü (boyut-değer çiftleri)
        """
        try:
            with db_session() as session:
                # En son eklenen kişilik vektörünü al
                personality = session.scalars(
                    select(PersonalityVector)
                    .filter(PersonalityVector.user_id == user_id)
                    .order_by(desc(PersonalityVector.created_at))
                    .limit(1)
                ).first()

                if personality:
                    return personality.vector

                # Kullanıcı için kayıt yoksa varsayılan vektörü döndür
                return {
                    "empathy": 0.5,
                    "curiosity": 0.5,
                    "assertiveness": 0.5,
                    "humour": 0.5,
                    "scepticism": 0.5
                }

        except Exception as e:
            logger.error(f"Kişilik vektörü alınırken hata: {e}")
            return {}

    def save_personality_vector(self, user_id: str, vector: Dict[str, float],
                                old_vector: Dict[str, float] = None,
                                delta: Dict[str, float] = None,
                                reason: str = None) -> bool:
        """
        Kullanıcının kişilik vektörünü kaydeder ve değişim günlüğü oluşturur.

        Args:
            user_id: Kullanıcı kimliği
            vector: Yeni kişilik vektörü
            old_vector: Önceki kişilik vektörü (isteğe bağlı)
            delta: Değişim değerleri (isteğe bağlı)
            reason: Değişim nedeni (isteğe bağlı)

        Returns:
            İşlemin başarılı olup olmadığı
        """
        try:
            with db_session() as session:
                # Yeni kişilik vektörünü oluştur
                new_vector = PersonalityVector(
                    user_id=user_id,
                    vector=vector
                )
                session.add(new_vector)
                session.flush()  # ID'yi almak için flush et

                # Değişim günlüğü oluştur (eğer eski vektör ve delta belirtilmişse)
                if old_vector and delta:
                    journal_entry = PersonalityJournal(
                        user_id=user_id,
                        vector_id=new_vector.id,
                        old_vector=old_vector,
                        new_vector=vector,
                        delta=delta,
                        reason=reason or "Scheduled update"
                    )
                    session.add(journal_entry)

                # Session context manager commit işlemini yapacak
                logger.info(f"Kişilik vektörü kaydedildi: {user_id}")
                return True

        except Exception as e:
            logger.error(f"Kişilik vektörü kaydedilirken hata: {e}")
            return False

    def get_personality_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Kullanıcının kişilik vektörü değişim geçmişini alır.

        Args:
            user_id: Kullanıcı kimliği
            limit: Getirilecek maksimum kayıt sayısı

        Returns:
            Kişilik değişim kayıtları listesi
        """
        try:
            with db_session() as session:
                journals = session.scalars(
                    select(PersonalityJournal)
                    .filter(PersonalityJournal.user_id == user_id)
                    .order_by(desc(PersonalityJournal.created_at))
                    .limit(limit)
                ).all()

                history = []
                for journal in journals:
                    history.append({
                        "timestamp": journal.created_at,
                        "old_vector": journal.old_vector,
                        "new_vector": journal.new_vector,
                        "delta": journal.delta,
                        "reason": journal.reason
                    })

                logger.info(f"Retrieved {len(history)} personality history entries for user {user_id}")
                return history

        except Exception as e:
            logger.error(f"Failed to retrieve personality history: {e}")
            return []