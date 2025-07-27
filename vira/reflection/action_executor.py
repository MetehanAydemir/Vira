"""
Hedefler doğrultusunda aksiyonlar uygulayan modül.
Proaktif mesajlar göndermek gibi somut aksiyonları gerçekleştirir.
"""

import json
import random
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..db.repository import DatabaseRepository
from ..utils.message_service import MessageService

class ActionExecutor:
    """Belirlenen aksiyonları uygulama"""
    
    def __init__(self, db_repository: Optional[DatabaseRepository] = None, message_service: Optional[MessageService] = None):
        """Initialize with database repository and message service"""
        self.db = db_repository or DatabaseRepository()
        self.message_service = message_service or MessageService()

    def execute_action(self, goal_id: str) -> Dict[str, Any]:
        """
        Ana aksiyon uygulama metodu - goal_id'ye göre uygun aksiyonu seçer ve uygular
        """
        try:
            # Hedefi veritabanından al
            goal = self.db.get_goal_by_id(uuid.UUID(goal_id))
            if not goal:
                return {"status": "error", "error": "Goal not found"}

            # Kullanıcı bağlamını al
            user_id = goal.get('user_id')
            user_context = self._get_user_context(user_id)

            # Hedef tipine göre uygun aksiyonu seç
            goal_type = goal.get('goal_type', '')
            result = {"status": "unknown", "goal_id": goal_id}

            if goal_type == "proactive_engagement":
                result = self.execute_proactive_engagement(goal, user_context)
            elif goal_type == "emotional_support":
                result = self.execute_emotional_support(goal, user_context)
            elif goal_type == "communication_optimization":
                result = self.execute_communication_optimization(goal, user_context)
            elif goal_type == "support_optimization":
                result = self.execute_support_optimization(goal, user_context)
            elif goal_type == "relationship_building":
                result = self.execute_relationship_building(goal, user_context)
            else:
                result = {"status": "unsupported_goal_type", "goal_type": goal_type}

            # Aksiyon sonucunu kaydet
            self._save_action_result(goal_id, result)

            return result
        except Exception as e:
            error_result = {"status": "error", "error": str(e)}
            # Hata durumunda da kaydet
            if 'goal_id' in locals():
                self._save_action_result(goal_id, error_result)
            return error_result
    
    def execute_proactive_engagement(self, goal: Dict, user_context: Dict) -> Dict[str, Any]:
        """Proaktif etkileşim aksiyonu"""
        # Kullanıcının aktif saatlerini al
        preferred_hours = user_context.get('preferred_hours', [])
        if not preferred_hours:
            return {"status": "insufficient_data"}
        
        # Proaktif mesaj üret
        message = self._generate_proactive_message(user_context)
        
        # Mesajı uygun zamanda gönderilmek üzere kuyruğa al
        next_optimal_time = self._calculate_next_optimal_time(preferred_hours)
        
        try:
            # MessageService sınıfını kullanarak mesajı planla
            message_id = self.message_service.schedule_message(
                user_id=goal.get('user_id'),
                message=message,
                scheduled_time=next_optimal_time,
                message_type="proactive_check_in"
            )
            
            return {
                "status": "scheduled",
                "scheduled_time": next_optimal_time,
                "message": message,
                "message_id": message_id
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def execute_emotional_support(self, goal: Dict, user_context: Dict) -> Dict[str, Any]:
        """Duygusal destek aksiyonu"""
        # Duygusal desenleri al
        emotional_patterns = user_context.get('emotional_patterns', {})
        difficult_days = emotional_patterns.get('difficult_days', [])
        
        if not difficult_days:
            return {"status": "insufficient_data"}
        
        # Bir sonraki zor günü tahmin et
        next_difficult_day = self._predict_next_difficult_day(difficult_days)
        
        # Destek mesajını hazırla
        support_message = self._generate_support_message(user_context)
        
        # Zor günden bir gün önce mesaj gönder
        support_time = next_difficult_day - timedelta(days=1)
        
        try:
            self.message_queue.schedule_message(
                user_id=goal['user_id'],
                message=support_message,
                scheduled_time=support_time,
                message_type="predictive_support"
            )
            
            return {
                "status": "scheduled",
                "support_date": support_time,
                "message": support_message
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def execute_communication_optimization(self, goal: Dict, user_context: Dict) -> Dict[str, Any]:
        """İletişim optimizasyonu aksiyonu"""
        # Kullanıcı iletişim tercihlerini al
        comm_style = user_context.get('communication_style', {})
        
        # Veritabanında iletişim stilini güncelle
        try:
            user_id = goal.get('user_id')
            if user_id:
                # Kullanıcı tercihlerini metaveri olarak kaydet
                self.db.update_user_preferences(
                    user_id=user_id,
                    preferences={
                        "preferred_message_length": comm_style.get('avg_message_length', 100),
                        "communication_style": "concise" if comm_style.get('avg_message_length', 100) < 100 else "detailed",
                        "last_updated": datetime.now().isoformat()
                    }
                )
                
                return {
                    "status": "updated",
                    "communication_style": "concise" if comm_style.get('avg_message_length', 100) < 100 else "detailed"
                }
            else:
                return {"status": "error", "error": "User ID missing"}
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_proactive_message(self, user_context: Dict) -> str:
        """Proaktif mesaj üret"""
        recent_topics = user_context.get('recent_topics', [])
        emotional_state = user_context.get('current_emotional_state', 'neutral')
        
        templates = [
            "Merhaba! Nasılsın? Son zamanlarda {topic} hakkında konuşmuştuk, merak ettim.",
            "Selam! Bir süredir konuşmamıştık. Bugün nasıl geçiyor?",
            "Hey! Aklıma geldin. {topic} konusunda bir gelişme var mı?",
            "Merhaba! Bugün nasılsın? Seninle tekrar konuşmak güzel.",
            "Selam! Umarım günün iyi geçiyordur. Yardıma ihtiyacın var mı?"
        ]
        
        template = random.choice(templates)
        
        if recent_topics:
            topic = recent_topics[0]
            message = template.format(topic=topic)
        else:
            message = "Merhaba! Nasılsın? Bugün nasıl geçiyor?"
        
        return message
    
    def _calculate_next_optimal_time(self, preferred_hours: List[int]) -> datetime:
        """Bir sonraki optimal zamanı hesapla"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Saatleri sırala
        sorted_hours = sorted(preferred_hours)
        
        # Bugün için kalan en yakın tercih edilen saati bul
        for hour in sorted_hours:
            candidate = today.replace(hour=hour)
            if candidate > now:
                return candidate
        
        # Bugün uygun saat kalmadıysa, yarın ilk tercih edilen saati kullan
        tomorrow = today + timedelta(days=1)
        return tomorrow.replace(hour=sorted_hours[0])
    
    def _predict_next_difficult_day(self, difficult_days: List[int]) -> datetime:
        """Bir sonraki zor günü tahmin et"""
        today = datetime.now()
        today_weekday = today.weekday()
        
        # Zor günleri sayısal olarak sırala (0=Pazartesi, 6=Pazar)
        sorted_difficult_days = sorted(difficult_days)
        
        # Bugünden sonraki ilk zor günü bul
        for day in sorted_difficult_days:
            if day > today_weekday:
                days_ahead = day - today_weekday
                return today + timedelta(days=days_ahead)
        
        # Eğer bu hafta kalan zor gün yoksa, gelecek haftanın ilk zor gününü al
        days_until_next_week = 7 - today_weekday + sorted_difficult_days[0]
        return today + timedelta(days=days_until_next_week)
    
    def _generate_support_message(self, user_context: Dict) -> str:
        """Destek mesajı üret"""
        templates = [
            "Merhaba! Yarın zor bir gün olabileceğini düşündüm ve sana destek olmak istedim. Nasılsın?",
            "Selam! Yarın için nasıl hissediyorsun? Yardımcı olabileceğim bir şey var mı?",
            "Hey! Yarın için biraz destek vermek istedim. Bugün kendine iyi bakıyor musun?",
            "Merhaba! Yarın için motivasyon veya desteğe ihtiyacın olabileceğini düşündüm. Nasıl yardımcı olabilirim?"
        ]
        
        return random.choice(templates)