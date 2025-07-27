"""
Yansıtma (reflection) için veri toplama modülü.
Kullanıcı etkileşimleri ve hafıza üzerinden desenleri analiz eder.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

from ..db.repository import DatabaseRepository
from ..utils.llm_client import LLMClient

class ReflectionDataGatherer:
    """Yansıtma için veri toplama - mevcut veritabanından"""
    
    def __init__(self, db_repository: Optional[DatabaseRepository] = None, llm_client: Optional[LLMClient] = None):
        """Initialize with optional database repository and LLM client."""
        self.db = db_repository or DatabaseRepository()
        self.llm = llm_client or LLMClient()
    
    def gather_conversation_patterns(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Konuşma desenlerini topla"""
        try:
            # Mevcut DatabaseRepository metodunu kullan
            conversations = self.db.get_user_interactions(uuid.UUID(user_id), limit=100)

            # Tarih filtreleme
            cutoff_date = datetime.now() - timedelta(days=days_back)
            conversations = [c for c in conversations if c.get('created_at', datetime.now()) >= cutoff_date]

            # Duygusal ton analizi yap
            for conv in conversations:
                if 'message' in conv and conv['message']:
                    # LLMClient'ın analyze_sentiment metodunu kullan
                    sentiment = self.llm.analyze_sentiment(conv['message'])
                    conv['emotional_tone'] = sentiment.get('sentiment', 'neutral')
                    conv['emotional_intensity'] = sentiment.get('intensity', 0.5)
                else:
                    conv['emotional_tone'] = 'neutral'
                    conv['emotional_intensity'] = 0.5
            
            return {
                "total_conversations": len(conversations),
                "conversation_frequency": self._calculate_frequency(conversations),
                "topic_distribution": self._analyze_topics(conversations),
                "emotional_journey": self._build_emotional_timeline(conversations),
                "response_patterns": self._analyze_response_patterns(conversations)
            }
        except Exception as e:
            # Hata durumunda boş sonuç döndür
            return {
                "total_conversations": 0,
                "error": str(e)
            }
    
    def gather_memory_patterns(self, user_id: str, min_importance: float = 0.6) -> Dict[str, Any]:
        """Hafıza desenlerini topla"""
        try:
            # Filtreleme için metadata hazırla
            metadata_filter = {"user_id": str(user_id)}

            # Mevcut DatabaseRepository metodunu kullan
            memories = self.db.filter_long_term_memory(metadata_filter, limit=50)

            # Önem skoru filtreleme
            memories = [m for m in memories if m.get('importance_score', 0.5) >= min_importance]
            
            return {
                "important_memories": memories,
                "memory_themes": self._extract_memory_themes(memories),
                "temporal_distribution": self._analyze_memory_timeline(memories),
                "emotional_memories": self._categorize_emotional_memories(memories)
            }
        except Exception as e:
            return {
                "important_memories": [],
                "error": str(e)
            }
    
    def _calculate_frequency(self, conversations):
        """Konuşma sıklığını hesapla"""
        if not conversations:
            return {"daily": 0, "weekly": 0, "monthly": 0}
        
        # Tarih bazlı gruplandırma
        date_counts = {}
        for conv in conversations:
            date_str = conv['created_at'].strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        # Ortalama hesapla
        total_days = len(date_counts)
        total_msgs = len(conversations)
        active_days = len([count for count in date_counts.values() if count > 0])
        
        return {
            "daily_average": total_msgs / max(total_days, 1),
            "active_days_ratio": active_days / max(total_days, 1),
            "most_active_day": max(date_counts.items(), key=lambda x: x[1])[0] if date_counts else None
        }
    
    def _analyze_topics(self, conversations):
        """Konu dağılımını analiz et"""
        if not conversations:
            return {}
        
        # Intent type'lara göre grupla
        intent_counts = {}
        for conv in conversations:
            intent = conv.get('intent_type', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Yüzdelik dağılım hesapla
        total = len(conversations)
        distribution = {intent: (count / total) * 100 for intent, count in intent_counts.items()}
        
        # En çok konuşulan 3 konu
        top_intents = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "distribution": distribution,
            "top_intents": [{"intent": intent, "percentage": pct} for intent, pct in top_intents]
        }
    
    def _build_emotional_timeline(self, conversations):
        """Duygusal zaman çizelgesi oluştur"""
        if not conversations:
            return []
        
        timeline = []
        for conv in conversations:
            timeline.append({
                "created_at": conv['created_at'],
                "emotional_tone": conv.get('emotional_tone', 'neutral'),
                "emotional_intensity": float(conv.get('emotional_intensity', 0.5))
            })
        
        return timeline
    
    def _analyze_response_patterns(self, conversations):
        """Yanıt desenlerini analiz et"""
        if not conversations:
            return {}
        
        # Ortalama yanıt uzunluğu
        response_lengths = [len(conv.get('response', '')) for conv in conversations]
        avg_response_length = sum(response_lengths) / max(len(response_lengths), 1)
        
        return {
            "average_response_length": avg_response_length,
            "min_response_length": min(response_lengths) if response_lengths else 0,
            "max_response_length": max(response_lengths) if response_lengths else 0
        }
    
    def _extract_memory_themes(self, memories):
        """Hafıza temalarını çıkart"""
        if not memories or len(memories) == 0:
            return {"themes": []}

        # Mevcut hafıza içeriklerini birleştir
        combined_content = " ".join([m.get('content', '') for m in memories])

        # LLM kullanarak temalar çıkart
        prompt = f"""
        Analyze the following memory contents and extract 3-5 main themes or topics.
        Return only a list of themes, separated by commas.
        
        Memories: "{combined_content[:1000]}"  # İlk 1000 karakteri kullan
        
        Themes:
        """

        try:
            response = self.llm.generate(prompt)
            themes = [theme.strip() for theme in response.split(",")]
            return {"themes": themes[:5]}  # En fazla 5 tema döndür
        except Exception:
            return {"themes": []}
    
    def _analyze_memory_timeline(self, memories):
        """Hafıza zaman çizelgesi analizi"""
        if not memories:
            return {"timeline": []}

        # Tarihlere göre hafızaları grupla
        timeline = []
        for memory in memories:
            created_at = memory.get('created_at')
            if created_at:
                timeline.append({
                    "date": created_at.strftime('%Y-%m-%d'),
                    "importance": memory.get('importance_score', 0.5),
                    "content_preview": memory.get('content', '')[:50]
                })

        # Tarihe göre sırala
        timeline.sort(key=lambda x: x['date'])

        return {"timeline": timeline}
    
    def _categorize_emotional_memories(self, memories):
        """Duygusal hafızaları kategorize et"""
        if not memories:
            return {"emotional_categories": []}

        # Duygusal ton analizi yap
        emotional_categories = {}

        for memory in memories:
            content = memory.get('content', '')
            if content:
                # LLM'in analyze_sentiment metodunu kullan
                sentiment = self.llm.analyze_sentiment(content)
                emotions = sentiment.get('emotions', ['neutral'])

                # İlk duyguyu ana duygu olarak al
                primary_emotion = emotions[0] if emotions else 'neutral'

                # Duygulara göre grupla
                if primary_emotion not in emotional_categories:
                    emotional_categories[primary_emotion] = []

                emotional_categories[primary_emotion].append({
                    "content_preview": content[:50],
                    "importance": memory.get('importance_score', 0.5),
                    "created_at": memory.get('created_at')
                })

        return {
            "emotional_categories": [
                {"emotion": emotion, "memories": memories[:3]}  # Her duygu için en fazla 3 hafıza
                for emotion, memories in emotional_categories.items()
            ]
        }