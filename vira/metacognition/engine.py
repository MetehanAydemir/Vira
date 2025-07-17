"""
MetaCognitive Engine - Tüm hafıza sistemlerini entegre eden ve birleştiren motor.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import logging

from vira.metacognition.models import UserMentalModel
from vira.db.repository import MemoryRepository, PersonalityRepository, UserRepository

logger = logging.getLogger(__name__)

class MetaCognitiveEngine:
    """
    Tüm hafıza sistemlerini entegre eden ve birleştiren MetaCognitive Engine.

    Bu motor, farklı hafıza sistemlerindeki (LongTerm, ShortTerm, Personality, Interaction)
    bilgileri birleştirerek bütünsel bir kullanıcı anlayışı oluşturur.
    """

    def __init__(self, db_repos_or_repo=None):
        """
        MetaCognitiveEngine'i başlatır.

        Args:
            db_repos_or_repo: Veritabanı repository'si veya repository'leri içeren sözlük
                             {"memory_repo": MemoryRepository, "personality_repo": PersonalityRepository, ...}
        """
        # Repositoryleri sözlük olarak tutacağız
        self.db_repos = {}

        if db_repos_or_repo is not None:
            # Eğer bir sözlük ise direkt kullan
            if isinstance(db_repos_or_repo, dict):
                self.db_repos = db_repos_or_repo
                # Geriye dönük uyumluluk için memory_repo'yu db_repo'ya ata
                self.db_repo = self.db_repos.get("memory_repo")
            else:
                # Tek bir repository ise, memory_repo olarak kaydet
                self.db_repo = db_repos_or_repo
                if self.db_repo is not None:
                    self.db_repos["memory_repo"] = self.db_repo
        else:
            # Hiçbir şey verilmediyse, None olarak ayarla
            self.db_repo = None

    def build_unified_user_model(self, user_id_or_state: Union[str, Dict[str, Any]],
                                 time_window: Dict[str, int] = None) -> UserMentalModel:
        """
        Kullanıcı için birleştirilmiş zihinsel model oluşturur.

        Args:
            user_id_or_state: Kullanıcı kimliği veya ViraState içeriği
            time_window: Zaman penceresi (örn: {"days": 7, "trend_days": 90})

        Returns:
            Birleştirilmiş kullanıcı modeli
        """
        # user_id_or_state'in Dict mi str mi olduğunu kontrol et
        if isinstance(user_id_or_state, dict):
            state = user_id_or_state
            user_id = state.get("user_id")
        else:
            user_id = user_id_or_state
            state = {"user_id": user_id}

        if not user_id:
            logger.warning("User ID bulunamadı, default model oluşturuluyor")
            user_id = "unknown"

        logger.debug(f"Building unified user model for user {user_id}")

        # Zaman penceresini ayarla
        if time_window is None:
            time_window = {
                "days": 7,  # Son durum için
                "trend_days": 90  # Eğilimler için
            }

        # Yeni model oluştur
        model = UserMentalModel(user_id)

        # Repolarımızı almak için helper
        memory_repo = self.db_repos.get("memory_repo") if hasattr(self, "db_repos") else self.db_repo
        personality_repo = self.db_repos.get("personality_repo") if hasattr(self, "db_repos") else None

        try:
            # Personality verilerini getir
            if personality_repo and hasattr(personality_repo, "get_personality_vector"):
                personality_data = personality_repo.get_personality_vector(user_id)
                if personality_data:
                    model.personality_trends = self._extract_personality_trends(personality_data)
            elif memory_repo and hasattr(memory_repo, "get_personality_data"):
                # Geriye dönük uyumluluk için
                personality_data = memory_repo.get_personality_data(user_id)
                if personality_data:
                    model.personality_trends = self._extract_personality_trends(personality_data)

            # Konuşma geçmişini getir
            if memory_repo and hasattr(memory_repo, "get_conversation_history"):
                recent_conversations = memory_repo.get_conversation_history(
                    user_id,
                    limit=10,
                    days=time_window.get("days", 7)
                )
                model.current_state = self._analyze_recent_interactions(recent_conversations)
                model.conversation_patterns = self._extract_conversation_patterns(recent_conversations)

            # Uzun süreli hafıza verilerini getir
            if memory_repo and hasattr(memory_repo, "get_long_term_memories"):
                long_term_memories = memory_repo.get_long_term_memories(user_id)
                model.memory_themes = self._extract_memory_themes(long_term_memories)

            # Çapraz korelasyonlar
            self._perform_cross_correlations(model)

        except Exception as e:
            logger.error(f"Unified user model oluştururken hata: {str(e)}")

        # Mevcut dynamic_personality verilerini entegre et
        if "dynamic_personality" in state and state["dynamic_personality"]:
            self._integrate_dynamic_personality(model, state["dynamic_personality"])

        return model

    def _extract_personality_trends(self, personality_data):
        """Personality verilerinden eğilimleri çıkarır."""
        # Mevcut implementasyonda basit bir şekilde personality verilerini döndür
        trends = {
            "empathy": {"current": 0.5, "trend": 0.0},
            "curiosity": {"current": 0.5, "trend": 0.0},
            "assertiveness": {"current": 0.5, "trend": 0.0},
            "humor": {"current": 0.5, "trend": 0.0},
            "skepticism": {"current": 0.5, "trend": 0.0}
        }

        # Eğer veri mevcutsa, trend'leri güncelle
        if personality_data:
            for key in trends:
                if key in personality_data:
                    trends[key]["current"] = personality_data[key]

        return trends

    def _analyze_recent_interactions(self, recent_conversations):
        """Son konuşmalardan durum analizi yapar."""
        # Basit bir implementasyon - gerçek uygulamada NLP kullanılmalı
        return {
            "emotional_state": self._extract_emotional_state(recent_conversations),
            "topic_focus": self._extract_topic_focus(recent_conversations),
            "interaction_mode": self._extract_interaction_mode(recent_conversations),
            "recent_context": self._extract_recent_context(recent_conversations)
        }

    def _extract_conversation_patterns(self, conversations):
        """Konuşma örüntülerini analiz eder."""
        # Basit bir implementasyon
        return {
            "preferred_topics": self._extract_preferred_topics(conversations),
            "response_styles": {},
            "question_frequency": self._calculate_question_frequency(conversations),
            "typical_session_length": self._calculate_typical_session_length(conversations)
        }

    def _extract_memory_themes(self, memories):
        """Hafıza verilerinden tematik bilgileri çıkarır."""
        # Basit bir implementasyon
        return {
            "dominant_topics": [],
            "recurring_entities": {},
            "emotional_associations": {},
            "memory_clusters": []
        }

    def _perform_cross_correlations(self, model):
        """Farklı hafıza türleri arasında korelasyon analizi yapar."""
        # Basit implementasyon - ileri düzey uygulamada gerçek korelasyon yapılmalı
        pass

    def _integrate_dynamic_personality(self, model, dynamic_personality):
        """Mevcut dynamic_personality değerlerini modele entegre eder."""
        if not dynamic_personality:
            return

        for key, value in dynamic_personality.items():
            if key in model.personality_trends:
                model.personality_trends[key]["current"] = value

    # Yardımcı analiz metodları - gerçek uygulamada NLP, ML gibi teknolojilerle geliştirilmeli
    def _extract_emotional_state(self, conversations):
        return {"primary": "neutral", "intensity": 0.5}

    def _extract_topic_focus(self, conversations):
        return []

    def _extract_interaction_mode(self, conversations):
        return "casual"

    def _extract_recent_context(self, conversations):
        return {}

    def _extract_preferred_topics(self, conversations):
        return []

    def _calculate_question_frequency(self, conversations):
        return 0.0

    def _calculate_typical_session_length(self, conversations):
        return 0

    # Vira'ya özgü zenginleştirme fonksiyonları
    def enhance_memory_retrieval(self, query: str, model: UserMentalModel,
                                memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hafıza erişimini kullanıcı modeline göre geliştirir.

        Args:
            query: Kullanıcı sorgusu
            model: Kullanıcı mental modeli
            memories: Temel hafıza araması sonuçları

        Returns:
            Kişilik ve bağlama göre yeniden sıralanmış hafıza sonuçları
        """
        # Eğer model yoksa, mevcut hafızaları döndür
        if not model:
            return memories

        # Basit implementasyon - gerçek uygulamada daha gelişmiş bir algoritma kullanılmalı

        # Kişilik eğilimlerine göre hafızaları ağırlıklandır
        weighted_memories = self._weight_memories_by_personality(memories, model.personality_trends)

        # Bağlama göre ağırlıklandır
        context_weighted_memories = self._weight_memories_by_context(
            weighted_memories, model.current_state
        )

        # Sonuçları sırala
        sorted_memories = sorted(
            context_weighted_memories,
            key=lambda x: x.get("_relevance_score", 0),
            reverse=True
        )

        return sorted_memories

    def enhance_intent_classification(self, intent: str, model: UserMentalModel) -> str:
        """
        Niyet sınıflandırmasını kullanıcı modeline göre geliştirir.

        Args:
            intent: Temel niyet sınıflandırması
            model: Kullanıcı mental modeli

        Returns:
            Geliştirilmiş niyet
        """
        # Eğer model yoksa, mevcut niyeti döndür
        if not model:
            return intent

        # Basit implementasyon - gerçek uygulamada daha gelişmiş bir algoritma kullanılmalı

        # Kişilik eğilimlerine göre niyet ayarlaması
        # Örnek: Meraklılık yüksekse soru niyetlerini güçlendir
        if model.personality_trends.get("curiosity", {}).get("current", 0) > 0.7 and intent == "unknown":
            return "question"

        # Örnek: Felsefi eğilim yüksekse, genel konuşmaları felsefi olarak yorumla
        if model.personality_trends.get("empathy", {}).get("current", 0) > 0.8 and intent == "information":
            return "philosophical"

        return intent

    # Hafıza ağırlıklandırma yardımcı metodları
    def _weight_memories_by_personality(self, memories, personality_trends):
        """Kişilik eğilimlerine göre hafızaları ağırlıklandırır."""
        if not memories:
            return []

        weighted_memories = []
        for memory in memories:
            # Hafızaya temel bir relevance skoru ekle (varsa koru)
            relevance = memory.get("_relevance_score", 0.5)

            # Kişilik bazlı ağırlıklandırma (basit implementasyon)
            # Örnek: Meraklılık yüksekse, soru içeren hafızalara daha fazla ağırlık ver
            if "question" in memory.get("content", "").lower() and personality_trends.get("curiosity", {}).get("current", 0) > 0.6:
                relevance *= 1.2

            # Güncellenmiş skoru ekle
            memory["_relevance_score"] = min(relevance, 1.0)  # 1.0'dan büyük olmasın
            weighted_memories.append(memory)

        return weighted_memories

    def _weight_memories_by_context(self, memories, current_state):
        """Mevcut bağlama göre hafızaları ağırlıklandırır."""
        if not memories:
            return []

        # Mevcut durum analizi
        current_topics = current_state.get("topic_focus", [])
        emotional_state = current_state.get("emotional_state", {}).get("primary", "neutral")

        weighted_memories = []
        for memory in memories:
            # Hafızanın mevcut relevance skoru
            relevance = memory.get("_relevance_score", 0.5)

            # Konu bazlı ağırlıklandırma
            memory_content = memory.get("content", "").lower()
            for topic in current_topics:
                if topic.lower() in memory_content:
                    relevance *= 1.2
                    break

            # Duygusal durum bazlı ağırlıklandırma
            if emotional_state in memory_content:
                relevance *= 1.1

            # Güncellenmiş skoru ekle
            memory["_relevance_score"] = min(relevance, 1.0)
            weighted_memories.append(memory)

        return weighted_memories