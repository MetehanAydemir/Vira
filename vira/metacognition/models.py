"""
Metacognitive sistem için veri modelleri.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class UserMentalModel:
    """
    Kullanıcının birleştirilmiş zihinsel modelini temsil eder.
    
    Tüm hafıza sistemlerinden (LongTerm, ShortTerm, Interaction, Personality)
    bilgileri birleştirerek bütünleşik bir kullanıcı anlayışı sağlar.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        
        # Şu anki durum (son etkileşimlerden)
        self.current_state = {
            "emotional_state": {},  # Duygu durumu (mutlu, üzgün, meraklı vb.)
            "topic_focus": [],      # Odaklanılan konular
            "interaction_mode": "", # Etkileşim modu (formal, casual, exploratory vb.)
            "recent_context": {}    # Son bağlam bilgileri
        }
        
        # Kişilik eğilimleri ve gelişimi
        self.personality_trends = {
            "empathy": {"current": 0.5, "trend": 0.0},       # Empati seviyesi ve eğilimi
            "curiosity": {"current": 0.5, "trend": 0.0},     # Meraklılık seviyesi ve eğilimi
            "assertiveness": {"current": 0.5, "trend": 0.0}, # Kendinden eminlik seviyesi ve eğilimi
            "humor": {"current": 0.5, "trend": 0.0},         # Mizah seviyesi ve eğilimi
            "skepticism": {"current": 0.5, "trend": 0.0}     # Şüphecilik seviyesi ve eğilimi
        }
        
        # Uzun süreli hafıza temaları
        self.memory_themes = {
            "dominant_topics": [],         # Baskın konular
            "recurring_entities": {},      # Tekrarlanan varlıklar (kişi, yer, nesne vb.)
            "emotional_associations": {},  # Duygusal çağrışımlar
            "memory_clusters": []          # Bellek kümeleri
        }
        
        # Konuşma örüntüleri
        self.conversation_patterns = {
            "preferred_topics": [],        # Tercih edilen konular
            "response_styles": {},         # Yanıt stilleri
            "question_frequency": 0.0,     # Soru sorma sıklığı
            "typical_session_length": 0    # Tipik oturum uzunluğu
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Modeli sözlük formatına dönüştürür (ViraState ile uyumluluk için).
        """
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_state": self.current_state,
            "personality_trends": self.personality_trends,
            "memory_themes": self.memory_themes,
            "conversation_patterns": self.conversation_patterns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMentalModel':
        """
        Sözlük verilerinden model oluşturur.
        """
        if not data:
            return None

        model = cls(data["user_id"])

        # datetime string'lerini parse et
        model.created_at = datetime.fromisoformat(data["created_at"])
        model.updated_at = datetime.fromisoformat(data["updated_at"])

        # Diğer özellikleri kopyala
        model.current_state = data.get("current_state", model.current_state)
        model.personality_trends = data.get("personality_trends", model.personality_trends)
        model.memory_themes = data.get("memory_themes", model.memory_themes)
        model.conversation_patterns = data.get("conversation_patterns", model.conversation_patterns)
        
        return model