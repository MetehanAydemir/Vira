"""
İçgörülerden hedef üretme modülü.
İçgörüleri somut, takip edilebilir hedeflere dönüştürür.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class EmergentGoalGenerator:
    """İçgörülerden hedef üretme"""
    
    def generate_goals_from_insights(self, insights: List[Dict], user_id: str) -> List[Dict]:
        """İçgörülerden actionable hedefler üret"""
        goals = []
        
        for insight in insights:
            if insight.get('actionable', False):
                goal = self._insight_to_goal(insight, user_id)
                if goal:
                    goals.append(goal)
        
        # Meta-hedefler ekle
        meta_goals = self._generate_meta_goals(insights, user_id)
        goals.extend(meta_goals)
        
        return goals
    
    def _insight_to_goal(self, insight: Dict, user_id: str) -> Optional[Dict]:
        """Tek bir içgörüden hedef üret"""
        goal_templates = {
            "temporal_preference": {
                "title": "Optimal zamanlarda proaktif etkileşim",
                "description": "Kullanıcının aktif olduğu saatlerde proaktif mesajlar gönder",
                "type": "proactive_engagement",
                "priority": 7
            },
            "emotional_cycle": {
                "title": "Duygusal zorluk dönemlerinde destek",
                "description": "Zor duygusal dönemlerde önceden destek sun",
                "type": "emotional_support",
                "priority": 9
            },
            "communication_preference": {
                "title": "İletişim tarzını optimize et",
                "description": "Kullanıcının tercih ettiği iletişim tarzına uyum sağla",
                "type": "communication_optimization",
                "priority": 6
            },
            "help_preference": {
                "title": "Tercih edilen yardım türüne odaklan",
                "description": "Kullanıcının en çok ihtiyaç duyduğu destek türünü proaktif olarak sağla",
                "type": "support_optimization",
                "priority": 8
            }
        }
        
        template = goal_templates.get(insight['type'])
        if not template:
            return None
        
        return {
            "user_id": user_id,
            "goal_text": template['title'],
            "description": template['description'],
            "goal_type": template['type'],
            "priority": template['priority'],
            "source_insight": insight['text'],
            "suggested_action": insight.get('suggested_action', ''),
            "status": "active",
            "created_at": datetime.now(),
            "success_metrics": self._define_success_metrics(template['type'])
        }
    
    def _generate_meta_goals(self, insights: List[Dict], user_id: str) -> List[Dict]:
        """Üst düzey meta-hedefler"""
        meta_goals = []
        
        # Genel ilişki geliştirme hedefi
        meta_goals.append({
            "user_id": user_id,
            "goal_text": "Kullanıcı ile daha derin ve anlamlı bir ilişki kurmak",
            "description": "Tüm içgörüleri kullanarak daha empatik ve proaktif bir asistan olmak",
            "goal_type": "relationship_building",
            "priority": 10,
            "status": "active",
            "created_at": datetime.now(),
            "success_metrics": [
                "Kullanıcı memnuniyetinde artış",
                "Daha kişisel konuların paylaşılması",
                "Proaktif mesajlara pozitif tepki"
            ]
        })
        
        return meta_goals
    
    def _define_success_metrics(self, goal_type: str) -> List[str]:
        """Hedef türüne göre başarı metrikleri tanımla"""
        metrics_map = {
            "proactive_engagement": [
                "Proaktif mesajlara olumlu yanıt oranı",
                "Kullanıcı başlatımlı sohbetlerde artış",
                "Sohbet süresinde artış"
            ],
            "emotional_support": [
                "Duygusal destek mesajlarına olumlu yanıt",
                "Kullanıcının duygusal paylaşımlarında artış",
                "Pozitif duygusal ton değişimi"
            ],
            "communication_optimization": [
                "Kullanıcı mesaj uzunluğuna uyum",
                "Mesaj stili uyumu",
                "Kullanıcı memnuniyetinde artış"
            ],
            "support_optimization": [
                "Kullanıcının yardım arama sıklığında azalma",
                "Çözüm önerilerine olumlu tepki",
                "Sorun çözme süresinde azalma"
            ]
        }
        
        return metrics_map.get(goal_type, ["Genel memnuniyet artışı"])