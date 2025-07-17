import json
from typing import Dict, List, Tuple, Any, Optional
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
    PersonalityJournal,
    User
)
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class UserRepository:
    """Kullanıcı veritabanı işlemlerini yönetmek için repository sınıfı."""

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Kullanıcıyı ID'ye göre getirir."""
        with db_session() as session:
            return session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        Kullanıcıyı kullanıcı adına göre getirir.

        Kullanıcı nesnesini değil, gerekli bilgileri içeren bir sözlük döndürür.
        """
        with db_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "hashed_password": user.hashed_password,
                "email": user.email,
                "created_at": user.created_at
            }

    def create_user(self, username: str, hashed_password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Yeni bir kullanıcı oluşturur ve veritabanına kaydeder.

        Kullanıcı nesnesini değil, gerekli bilgileri içeren bir sözlük döndürür.
        Bu, session kapandıktan sonra detached instance hatalarını önler.
        """
        with db_session() as session:
            # Kullanıcının zaten var olup olmadığını kontrol et (aynı session içinde)
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                raise ValueError("Bu kullanıcı adı zaten kullanımda")

            # Yeni kullanıcı oluştur
            new_user = User(
                username=username,
                hashed_password=hashed_password,
                email=email
            )
            session.add(new_user)
            session.commit()  # Değişiklikleri kaydet

            # Session kapanmadan önce gerekli değerleri al ve bir sözlük olarak döndür
            user_data = {
                "id": new_user.id,
                "username": new_user.username,
                "created_at": new_user.created_at
            }

            return user_data

class MemoryRepository:
    """Repository for memory operations using SQLAlchemy."""

    def get_personality_data(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcının kişilik verilerini getirir.

        Args:
            user_id: Kullanıcı kimliği

        Returns:
            Dict[str, Any]: Kişilik verileri
        """
        try:
            # PersonalityRepository kullanarak kişilik verilerini al
            personality_repo = PersonalityRepository()
            personality_vector = personality_repo.get_personality_vector(user_id)

            logger.info(f"Retrieved personality data for user {user_id}")
            return personality_vector
        except Exception as e:
            logger.error(f"Failed to retrieve personality data: {e}")
            return {}

    def get_conversation_history(self, user_id: str, limit: int = 10, days: int = 7) -> List[Tuple[str, str, datetime]]:
        """
        Kullanıcının konuşma geçmişini getirir.

        Args:
            user_id: Kullanıcı kimliği
            limit: Getirilecek maksimum konuşma sayısı
            days: Kaç günlük konuşmaların getirileceği

        Returns:
            List[Tuple[str, str, datetime]]: (kullanıcı_mesajı, sistem_yanıtı, tarih) üçlülerinden oluşan liste
        """
        # Mevcut get_recent_conversations metodunu kullan
        return self.get_recent_conversations(user_id, session_id=None, limit=limit)

    def get_long_term_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Kullanıcının uzun süreli hafıza verilerini getirir.

        Args:
            user_id: Kullanıcı kimliği

        Returns:
            List[Dict[str, Any]]: Uzun süreli hafıza verileri
        """
        try:
            with db_session() as session:
                memories = session.scalars(
                    select(LongTermMemory)
                    .filter(LongTermMemory.metadatas['user_id'].astext == user_id)
                    .order_by(desc(LongTermMemory.created_at))
                    .limit(100)  # Makul bir limit
                ).all()

                result = []
                for memory in memories:
                    result.append({
                        "content": memory.content,
                        "created_at": memory.created_at,
                        "metadata": memory.metadatas
                    })

                logger.info(f"Retrieved {len(result)} long term memories for user {user_id}")
                return result
        except Exception as e:
            logger.error(f"Failed to retrieve long term memories: {e}")
            return []

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

    def store_interaction(self, user_id: str, message: str, response: str, intent_type: str = None) -> int:
        """
        Kullanıcı etkileşimini Interaction tablosuna kaydeder.

        Args:
            user_id: Kullanıcı kimliği
            message: Kullanıcı mesajı
            response: Sistem yanıtı
            intent_type: Niyet türü (opsiyonel)

        Returns:
            int: Kaydedilen etkileşimin ID'si
        """
        try:
            with db_session() as session:
                interaction = Interaction(
                    user_id=user_id,
                    message=message,
                    response=response,
                    intent_type=intent_type
                )
                session.add(interaction)
                session.flush()
                interaction_id = interaction.id

                logger.info(f"Interaction kaydedildi: {interaction_id}")
                return interaction_id
        except Exception as e:
            logger.error(f"Interaction kaydedilirken hata: {e}")
            raise

    def store_short_term_memory(self, session_id: str, content: str) -> int:
        """
        Kısa süreli hafızaya kayıt yapar.

        Args:
            session_id: Oturum kimliği
            content: Kaydedilecek içerik

        Returns:
            int: Kaydedilen hafıza girdisinin ID'si
        """
        try:
            with db_session() as session:
                memory = ShortTermMemory(
                    session_id=session_id,
                    content=content
                )
                session.add(memory)
                session.flush()
                memory_id = memory.id

                logger.info(f"Short-term memory kaydedildi: {memory_id}")
                return memory_id
        except Exception as e:
            logger.error(f"Short-term memory kaydedilirken hata: {e}")
            raise

    def store_long_term_memory(self, user_id: str, content: str, embedding: np.ndarray,
                               metadatas: Dict[str, Any] = None) -> str:
        """
        Uzun süreli hafızaya kayıt yapar.

        Args:
            user_id: Kullanıcı kimliği
            content: Kaydedilecek içerik
            embedding: İçerik için vektör gömme
            metadatas: Ek metadata bilgileri (opsiyonel)

        Returns:
            str: Kaydedilen hafıza girdisinin ID'si
        """
        try:
            with db_session() as session:
                # Metadata'ya user_id ekle
                if metadatas is None:
                    metadatas = {}

                if 'user_id' not in metadatas:
                    metadatas['user_id'] = user_id

                memory = LongTermMemory(
                    content=content,
                    embedding=embedding.tolist(),
                    metadatas=metadatas
                )
                session.add(memory)
                session.flush()
                memory_id = memory.id

                logger.info(f"Long-term memory kaydedildi: {memory_id}")
                return str(memory_id)
        except Exception as e:
            logger.error(f"Long-term memory kaydedilirken hata: {e}")
            raise

    def retrieve_similar_memories_with_metadata(self, user_id: str, embedding: np.ndarray, top_k: int = 3):
        """
        Embedding benzerliğine göre en benzer hafızaları metadata ile birlikte getirir.

        Args:
            user_id: Kullanıcı kimliği
            embedding: Sorgu vektörü
            top_k: Getirilecek maksimum kayıt sayısı

        Returns:
            List[Tuple[str, float, datetime, Dict]]: (içerik, benzerlik, tarih, metadata) dörtlülerinden oluşan liste
        """
        try:
            with db_session() as session:
                # Vektör benzerlik araması
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

                    # İçerik, benzerlik, tarih ve metadata'yı döndür
                    result.append((
                        memory.content,
                        float(similarity),
                        memory.created_at,
                        memory.metadatas
                    ))

                logger.info(f"Retrieved {len(result)} similar memories with metadata for user {user_id}")
                return result
        except Exception as e:
            logger.error(f"Failed to retrieve similar memories with metadata: {e}")
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