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

    # Yardımcı analiz metodları - gerçek NLP implementasyonu
    def _extract_emotional_state(self, conversations):
        """Konuşmalardan duygusal durumu çıkarır."""
        if not conversations:
            return {"primary": "neutral", "intensity": 0.5}
        
        try:
            from vira.utils.llm_client import call_chat_model
            
            # Son birkaç konuşmayı analiz et
            recent_messages = []
            for conv in conversations[-5:]:  # Son 5 konuşma
                if isinstance(conv, dict):
                    content = conv.get("content", conv.get("message", ""))
                    if content:
                        recent_messages.append(content)
            
            if not recent_messages:
                return {"primary": "neutral", "intensity": 0.5}
            
            combined_text = " ".join(recent_messages)
            
            messages = [
                {
                    "role": "system",
                    "content": """Sen bir duygusal analiz uzmanısın. Verilen metinlerdeki duygusal durumu analiz et.

Yanıtını JSON formatında ver:
{
    "primary": "positive/negative/neutral/excited/anxious/frustrated/happy/sad/angry/curious",
    "intensity": 0.0-1.0 arası sayı (0=çok hafif, 1=çok yoğun)
}"""
                },
                {
                    "role": "user",
                    "content": f"Bu konuşmalardaki duygusal durumu analiz et:\n\n{combined_text[:1000]}"
                }
            ]
            
            response = call_chat_model(
                messages,
                temperature=0.3,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            import json
            result = self._parse_emotional_state_with_fallback(response)
            return result
            
        except Exception as e:
            logger.error(f"Duygusal durum analizi hatası: {str(e)}")
            return {"primary": "neutral", "intensity": 0.5}

    def _extract_topic_focus(self, conversations):
        """Konuşmalardan odaklanılan konuları çıkarır."""
        if not conversations:
            return []
        
        try:
            from vira.utils.llm_client import call_chat_model
            
            # Konuşma içeriklerini topla
            all_content = []
            for conv in conversations[-10:]:  # Son 10 konuşma
                if isinstance(conv, dict):
                    content = conv.get("content", conv.get("message", ""))
                    if content:
                        all_content.append(content)
            
            if not all_content:
                return []
            
            combined_text = " ".join(all_content)
            
            messages = [
                {
                    "role": "system",
                    "content": """Sen bir metin analisti ve konu çıkarma uzmanısın. Verilen konuşmalardan ana konuları çıkar.

Konular kısa ve öz olmalı (1-3 kelime). En fazla 5 konu çıkar.
Her konuyu ayrı satırda ver, numaralandırma kullanma.
Türkçe konu isimleri kullan."""
                },
                {
                    "role": "user",
                    "content": f"Bu konuşmalardan ana konuları çıkar:\n\n{combined_text[:1500]}"
                }
            ]
            
            response = call_chat_model(messages, temperature=0.5, max_tokens=200)
            
            # Yanıtı temizle ve konuları çıkar
            topics = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Numaralandırma ve işaretleri temizle
                    import re
                    line = re.sub(r'^\d+[\.\)]\s*', '', line)
                    line = re.sub(r'^[-\*]\s*', '', line)
                    topic = line.strip()
                    if topic and len(topic) > 2:
                        topics.append(topic)
            
            return topics[:5]  # En fazla 5 konu
            
        except Exception as e:
            logger.error(f"Konu analizi hatası: {str(e)}")
            return []

    def _extract_interaction_mode(self, conversations):
        """Konuşmalardan etkileşim modunu çıkarır."""
        if not conversations:
            return "casual"
        
        try:
            from vira.utils.llm_client import call_chat_model
            
            # Son birkaç konuşmayı analiz et
            recent_messages = []
            for conv in conversations[-5:]:
                if isinstance(conv, dict):
                    content = conv.get("content", conv.get("message", ""))
                    if content:
                        recent_messages.append(content)
            
            if not recent_messages:
                return "casual"
            
            combined_text = " ".join(recent_messages)
            
            messages = [
                {
                    "role": "system",
                    "content": """Sen bir iletişim analisti uzmanısın. Verilen konuşmalardaki etkileşim modunu belirle.

Etkileşim modları:
- formal: Resmi, profesyonel ton
- casual: Günlük, rahat konuşma
- technical: Teknik, detaylı açıklamalar
- emotional: Duygusal, kişisel paylaşımlar
- help_seeking: Yardım arama, problem çözme
- exploratory: Keşfetme, öğrenme odaklı

Sadece mod ismini ver, açıklama yapma."""
                },
                {
                    "role": "user",
                    "content": f"Bu konuşmalardaki etkileşim modunu belirle:\n\n{combined_text[:1000]}"
                }
            ]
            
            response = call_chat_model(messages, temperature=0.3, max_tokens=50)
            
            # Yanıtı temizle
            mode = response.strip().lower()
            valid_modes = ["formal", "casual", "technical", "emotional", "help_seeking", "exploratory"]
            
            for valid_mode in valid_modes:
                if valid_mode in mode:
                    return valid_mode
            
            return "casual"  # Varsayılan
            
        except Exception as e:
            logger.error(f"Etkileşim modu analizi hatası: {str(e)}")
            return "casual"

    def _extract_recent_context(self, conversations):
        """Son konuşmalardan bağlamsal bilgileri çıkarır."""
        if not conversations:
            return {}
        
        try:
            # Son konuşmadan temel bilgileri çıkar
            last_conv = conversations[-1] if conversations else {}
            
            context = {
                "last_interaction_time": last_conv.get("timestamp", ""),
                "conversation_count": len(conversations),
                "recent_topics": self._extract_topic_focus(conversations[-3:]),  # Son 3 konuşma
                "session_active": len(conversations) > 0
            }
            
            # Zaman analizi
            if len(conversations) >= 2:
                try:
                    from datetime import datetime
                    last_time = last_conv.get("timestamp", "")
                    if last_time:
                        # Basit zaman analizi
                        context["time_since_last"] = "recent"
                except:
                    pass
            
            return context
            
        except Exception as e:
            logger.error(f"Bağlam analizi hatası: {str(e)}")
            return {}

    def _extract_preferred_topics(self, conversations):
        """Konuşmalardan tercih edilen konuları çıkarır."""
        if not conversations:
            return []
        
        try:
            # Tüm konuşmalardan konuları çıkar ve frekanslarını hesapla
            all_topics = []
            
            # Konuşmaları gruplara böl (her 5 konuşma bir grup)
            for i in range(0, len(conversations), 5):
                group = conversations[i:i+5]
                topics = self._extract_topic_focus(group)
                all_topics.extend(topics)
            
            if not all_topics:
                return []
            
            # Konu frekanslarını hesapla
            topic_counts = {}
            for topic in all_topics:
                topic_lower = topic.lower()
                topic_counts[topic_lower] = topic_counts.get(topic_lower, 0) + 1
            
            # En sık geçen konuları sırala
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            
            # En fazla 5 tercih edilen konu döndür
            preferred = [topic for topic, count in sorted_topics[:5] if count > 1]
            
            return preferred
            
        except Exception as e:
            logger.error(f"Tercih edilen konular analizi hatası: {str(e)}")
            return []

    def _calculate_question_frequency(self, conversations):
        """Konuşmalardaki soru sıklığını hesaplar."""
        if not conversations:
            return 0.0
        
        try:
            question_count = 0
            total_messages = 0
            
            for conv in conversations:
                if isinstance(conv, dict):
                    content = conv.get("content", conv.get("message", ""))
                    if content:
                        total_messages += 1
                        # Soru işaretlerini say
                        question_count += content.count("?")
                        # Soru kelimelerini say
                        question_words = ["nasıl", "neden", "ne", "kim", "nerede", "ne zaman", "hangi"]
                        content_lower = content.lower()
                        for word in question_words:
                            if word in content_lower:
                                question_count += 0.5  # Kısmi puan
            
            if total_messages == 0:
                return 0.0
            
            return min(question_count / total_messages, 2.0)  # Maksimum 2.0
            
        except Exception as e:
            logger.error(f"Soru sıklığı hesaplama hatası: {str(e)}")
            return 0.0

    def _calculate_typical_session_length(self, conversations):
        """Tipik oturum uzunluğunu hesaplar."""
        if not conversations:
            return 0
        
        try:
            # Basit bir hesaplama: toplam konuşma sayısını oturum sayısına böl
            # Gerçek implementasyonda zaman damgalarına göre oturumlar ayrılabilir
            
            total_conversations = len(conversations)
            
            # Zaman damgalarına göre oturum analizi yapmaya çalış
            sessions = []
            current_session = []
            
            for i, conv in enumerate(conversations):
                if isinstance(conv, dict):
                    timestamp = conv.get("timestamp", "")
                    
                    if current_session and timestamp:
                        # Basit oturum ayrımı: 1 saatten fazla ara varsa yeni oturum
                        try:
                            from datetime import datetime, timedelta
                            # Bu basit bir implementasyon, gerçekte daha karmaşık olabilir
                            current_session.append(conv)
                        except:
                            current_session.append(conv)
                    else:
                        current_session.append(conv)
                    
                    # Her 10 konuşmada bir oturum bitir (basit yaklaşım)
                    if len(current_session) >= 10:
                        sessions.append(len(current_session))
                        current_session = []
            
            # Son oturumu da ekle
            if current_session:
                sessions.append(len(current_session))
            
            if not sessions:
                return total_conversations
            
            # Ortalama oturum uzunluğu
            return sum(sessions) // len(sessions)
            
        except Exception as e:
            logger.error(f"Oturum uzunluğu hesaplama hatası: {str(e)}")
            return len(conversations) if conversations else 0

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

    def _parse_emotional_state_with_fallback(self, response):
        """
        Robust parsing function for emotional state with multiple fallback strategies.
        """
        import json
        import re
        
        if not response or not response.strip():
            return {"primary": "neutral", "intensity": 0.5}
        
        # Strategy 1: Try direct JSON parsing
        try:
            result = json.loads(response)
            if "primary" in result and "intensity" in result:
                return {
                    "primary": result["primary"],
                    "intensity": max(0.0, min(1.0, float(result["intensity"])))
                }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
        
        # Strategy 2: Extract JSON from text
        extracted_json = self._extract_json_from_text(response)
        if extracted_json:
            try:
                result = json.loads(extracted_json)
                if "primary" in result and "intensity" in result:
                    return {
                        "primary": result["primary"],
                        "intensity": max(0.0, min(1.0, float(result["intensity"])))
                    }
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        
        # Strategy 3: Pattern matching for key-value pairs
        # Look for primary emotion
        primary_match = re.search(r'primary["\']?\s*:\s*["\']?(\w+)["\']?', response, re.IGNORECASE)
        primary = primary_match.group(1) if primary_match else "neutral"
        
        # Look for intensity
        intensity_match = re.search(r'intensity["\']?\s*:\s*["\']?([0-9.]+)["\']?', response, re.IGNORECASE)
        intensity = float(intensity_match.group(1)) if intensity_match else 0.5
        
        if primary_match or intensity_match:
            return {
                "primary": primary.lower(),
                "intensity": max(0.0, min(1.0, intensity))
            }
        
        # Strategy 4: Natural language parsing
        emotion_keywords = {
            "happy": ["happy", "joy", "pleased", "content", "cheerful"],
            "sad": ["sad", "depressed", "down", "melancholy"],
            "angry": ["angry", "mad", "furious", "irritated"],
            "excited": ["excited", "enthusiastic", "thrilled"],
            "anxious": ["anxious", "worried", "nervous", "concerned"],
            "frustrated": ["frustrated", "annoyed", "bothered"],
            "curious": ["curious", "interested", "wondering"],
            "positive": ["positive", "good", "great", "excellent"],
            "negative": ["negative", "bad", "poor", "terrible"]
        }
        
        response_lower = response.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                # Try to extract intensity from numbers in the text
                numbers = re.findall(r'[0-9.]+', response)
                intensity = 0.5
                if numbers:
                    try:
                        intensity = max(0.0, min(1.0, float(numbers[0])))
                    except:
                        pass
                
                return {"primary": emotion, "intensity": intensity}
        
        # Strategy 5: Default fallback
        return {"primary": "neutral", "intensity": 0.5}

    def _extract_json_from_text(self, text):
        """Extract JSON object from text that might contain other content."""
        import json
        import re
        
        # Try to find JSON object in the text
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text)
        
        if matches:
            # Return the first match that looks like JSON
            for match in matches:
                try:
                    json.loads(match)  # Test if it's valid JSON
                    return match
                except:
                    continue
        
        # Try to find content between curly braces (more flexible)
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            potential_json = text[start:end+1]
            try:
                json.loads(potential_json)
                return potential_json
            except:
                pass
        
        return None

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