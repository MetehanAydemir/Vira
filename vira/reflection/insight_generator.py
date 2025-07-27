"""
Kullanıcı desenlerinden içgörü üretme modülü.
Desenlerden anlamlı içgörüler ve öneriler çıkarır.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..memory.reflector import Reflector
from ..utils.llm_client import LLMClient

class InsightGenerator:
    """Desenlerden içgörü üretme"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, reflector: Optional[Reflector] = None):
        """Initialize with optional LLM client and reflector."""
        self.llm = llm_client or LLMClient()
        self.reflector = reflector or Reflector(llm_client=self.llm)
    
    def generate_temporal_insights(self, temporal_patterns: Dict) -> List[Dict]:
        """Zamansal desenlerden içgörüler"""
        insights = []
        
        # Temporal patterns JSON'ı string'e dönüştür
        patterns_text = json.dumps(temporal_patterns, default=str)

        # Reflector'ün extract_meaningful_insights metodunu kullan
        insight_texts = self.reflector.extract_meaningful_insights(
            f"Temporal patterns analysis: {patterns_text}",
            count=3
        )
        
        # İçgörüleri yapılandırılmış formata dönüştür
        for i, text in enumerate(insight_texts):
            confidence = 0.8 if i == 0 else (0.7 if i == 1 else 0.6)  # İlk içgörü daha güvenilir
            
            # Actionable olup olmadığını belirle
            actionable = "time" in text.lower() or "hour" in text.lower() or "day" in text.lower()
            suggested_action = ""
            
            if actionable:
                # Proaktif aksiyon önerisi için Reflector'ü kullan
                action_prompt = f"Suggest a proactive action based on this insight: {text}"
                action_suggestions = self.reflector.extract_meaningful_insights(action_prompt, count=1)
                suggested_action = action_suggestions[0] if action_suggestions else ""

            insights.append({
                "type": "temporal_insight",
                "text": text,
                "confidence": confidence,
                "actionable": actionable,
                "suggested_action": suggested_action
            })
        
        return insights
    
    def generate_behavioral_insights(self, behavioral_patterns: Dict) -> List[Dict]:
        """Davranışsal desenlerden içgörüler"""
        # Behavioral patterns JSON'ı string'e dönüştür
        patterns_text = json.dumps(behavioral_patterns, default=str)

        # Reflector'ün extract_meaningful_insights metodunu kullan
        insight_texts = self.reflector.extract_meaningful_insights(
            f"Behavioral patterns analysis: {patterns_text}",
            count=3
        )

        # İçgörüleri yapılandırılmış formata dönüştür
        insights = []
        for i, text in enumerate(insight_texts):
            confidence = 0.8 if i == 0 else (0.7 if i == 1 else 0.6)

            # İçgörü tipini belirle
            insight_type = "communication_preference"
            if "help" in text.lower() or "support" in text.lower():
                insight_type = "help_preference"
            elif "emotion" in text.lower() or "feel" in text.lower():
                insight_type = "emotional_pattern"

            # Actionable olup olmadığını belirle
            actionable = True  # Çoğu davranışsal içgörü actionable olduğu varsayılır

            # Proaktif aksiyon önerisi için Reflector'ü kullan
            action_prompt = f"Suggest a proactive action based on this insight: {text}"
            action_suggestions = self.reflector.extract_meaningful_insights(action_prompt, count=1)
            suggested_action = action_suggestions[0] if action_suggestions else ""

            insights.append({
                "type": insight_type,
                "text": text,
                "confidence": confidence,
                "actionable": actionable,
                "suggested_action": suggested_action
            })
        
        return insights
    
    def synthesize_cross_pattern_insights(self, all_patterns: Dict) -> Dict[str, Any]:
        """Farklı desenleri birleştirerek meta-içgörüler"""
        # Tüm desenleri metin olarak birleştir
        all_patterns_text = f"""
        TEMPORAL PATTERNS: {json.dumps(all_patterns.get('temporal', {}), default=str)}
        BEHAVIORAL PATTERNS: {json.dumps(all_patterns.get('behavioral', {}), default=str)}
        EMOTIONAL PATTERNS: {json.dumps(all_patterns.get('emotional', {}), default=str)}
        """

        # Reflector'ün metodlarını kullanarak temalar ve içgörüler çıkar
        core_needs = self.reflector.extract_themes(
            [{"message": f"Core needs based on: {all_patterns_text}"}],
            top_n=3
        )

        support_areas = self.reflector.extract_themes(
            [{"message": f"Support areas based on: {all_patterns_text}"}],
            top_n=3
        )

        relationship_opportunities = self.reflector.extract_meaningful_insights(
            f"Relationship improvement opportunities based on: {all_patterns_text}",
            count=3
        )
        
        proactive_actions = self.reflector.extract_meaningful_insights(
            f"Proactive actions that could be taken based on: {all_patterns_text}",
            count=3
        )
        
        # Yapılandırılmış yanıt oluştur
        return {
            "core_needs": core_needs,
            "support_areas": support_areas,
            "relationship_opportunities": relationship_opportunities,
            "proactive_actions": proactive_actions
        }