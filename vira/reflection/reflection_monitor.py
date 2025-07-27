"""
Self-reflection sisteminin performansını izleyen modül.
Sistemin etkinliğini ölçer ve iyileştirir.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ReflectionMonitor:
    """Self-reflection sisteminin performansını izle"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def track_reflection_effectiveness(self, user_id: str, reflection_session_id: str) -> Dict[str, Any]:
        """Yansıtmanın etkinliğini takip et"""
        # Yansıtma sonrası kullanıcı davranışını izle
        post_reflection_interactions = self.get_interactions_after_reflection(
            user_id, reflection_session_id
        )
        
        effectiveness_metrics = {
            "user_engagement_change": self.measure_engagement_change(post_reflection_interactions),
            "emotional_state_improvement": self.measure_emotional_improvement(post_reflection_interactions),
            "goal_progress": self.track_goal_progress(user_id, reflection_session_id),
            "proactive_message_reception": self.measure_proactive_message_success(user_id)
        }
        
        return effectiveness_metrics
    
    def adjust_reflection_frequency(self, user_id: str, effectiveness_metrics: Dict[str, Any]) -> str:
        """Yansıtma sıklığını etkinliğe göre ayarla"""
        engagement_change = effectiveness_metrics.get("user_engagement_change", 0)
        
        if engagement_change > 0.2:
            # Etkili ise sıklığı artır
            return "increase_frequency"
        elif engagement_change < -0.1:
            # Etkisiz ise azalt
            return "decrease_frequency"
        else:
            return "maintain_frequency"
    
    def get_interactions_after_reflection(self, user_id: str, reflection_session_id: str) -> List[Dict]:
        """Yansıtma sonrası etkileşimleri getir"""
        # Yansıtma oturumunun zamanını al
        reflection_session = self.db.get_reflection_session(reflection_session_id)
        
        if not reflection_session:
            return []
        
        reflection_time = reflection_session.get('created_at')
        if not reflection_time:
            return []
        
        # Yansıtma sonrası etkileşimleri getir
        interactions = self.db.get_interactions_after_time(user_id, reflection_time)
        return interactions
    
    def measure_engagement_change(self, post_reflection_interactions: List[Dict]) -> float:
        """Kullanıcı katılımındaki değişimi ölç"""
        if not post_reflection_interactions:
            return 0.0
        
        # Basit implementasyon: Etkileşim sayısındaki değişim
        # Gerçek uygulamada önceki dönemle karşılaştırma yapılabilir
        message_lengths = [len(interaction.get('message', '')) for interaction in post_reflection_interactions]
        avg_length = sum(message_lengths) / max(len(message_lengths), 1)
        
        # Varsayılan ortalama mesaj uzunluğu (100 karakter) ile karşılaştır
        baseline_avg_length = 100
        
        # -1 ile 1 arasında değişim skoru
        change_score = (avg_length - baseline_avg_length) / baseline_avg_length
        
        # Skoru -1 ile 1 arasında sınırla
        return max(min(change_score, 1.0), -1.0)
    
    def measure_emotional_improvement(self, post_reflection_interactions: List[Dict]) -> float:
        """Duygusal durumdaki iyileşmeyi ölç"""
        if not post_reflection_interactions:
            return 0.0
        
        # Duygusal değerlendirme
        emotion_scores = {
            'happy': 1.0,
            'satisfied': 0.8,
            'neutral': 0.5,
            'frustrated': 0.3,
            'sad': 0.2,
            'angry': 0.1
        }
        
        emotional_tones = [interaction.get('emotional_tone', 'neutral') for interaction in post_reflection_interactions]
        scores = [emotion_scores.get(tone, 0.5) for tone in emotional_tones]
        
        if not scores:
            return 0.0
        
        avg_score = sum(scores) / len(scores)
        
        # Nötr (0.5) ile karşılaştır
        return avg_score - 0.5
    
    def track_goal_progress(self, user_id: str, reflection_session_id: str) -> Dict[str, Any]:
        """Hedef ilerlemesini takip et"""
        # Yansıtma oturumunda oluşturulan hedefleri getir
        goals = self.db.get_goals_from_reflection(reflection_session_id)
        
        progress_data = {
            "total_goals": len(goals),
            "completed_goals": 0,
            "in_progress_goals": 0,
            "not_started_goals": 0
        }
        
        for goal in goals:
            status = goal.get('status', 'active')
            if status == 'completed':
                progress_data["completed_goals"] += 1
            elif status == 'active':
                progress_data["in_progress_goals"] += 1
            else:
                progress_data["not_started_goals"] += 1
        
        # Tamamlanma oranı
        if progress_data["total_goals"] > 0:
            progress_data["completion_rate"] = progress_data["completed_goals"] / progress_data["total_goals"]
        else:
            progress_data["completion_rate"] = 0.0
        
        return progress_data
    
    def measure_proactive_message_success(self, user_id: str) -> Dict[str, Any]:
        """Proaktif mesajların başarısını ölç"""
        # Son 7 gün içinde gönderilen proaktif mesajları getir
        week_ago = datetime.now() - timedelta(days=7)
        proactive_messages = self.db.get_proactive_messages(user_id, week_ago)
        
        if not proactive_messages:
            return {
                "sent_count": 0,
                "response_rate": 0.0,
                "positive_responses": 0,
                "success_rate": 0.0
            }
        
        # Yanıt verilen mesajları say
        responded_count = sum(1 for msg in proactive_messages if msg.get('is_responded', False))
        
        # Olumlu yanıtları say (duygusal tonu olumlu olanlar)
        positive_responses = sum(1 for msg in proactive_messages 
                                if msg.get('is_responded', False) and 
                                msg.get('response_emotional_tone') in ['happy', 'satisfied', 'positive'])
        
        return {
            "sent_count": len(proactive_messages),
            "response_rate": responded_count / len(proactive_messages),
            "positive_responses": positive_responses,
            "success_rate": positive_responses / len(proactive_messages) if proactive_messages else 0.0
        }