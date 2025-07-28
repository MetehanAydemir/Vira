"""
Kullanıcı desenlerinden içgörü üretme modülü.
Desenlerden anlamlı içgörüler ve öneriler çıkarır.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..memory.reflector import Reflector
from ..utils.logger import get_logger

logger = get_logger(__name__)

class InsightGenerator:
    """Desenlerden içgörü üretme"""
    
    def __init__(self, reflector: Optional[Reflector] = None):
        """Initialize with optional reflector."""
        self.reflector = reflector or Reflector()
    
    def generate_temporal_insights(self, temporal_patterns: Dict) -> List[Dict]:
        """Zamansal desenlerden içgörüler"""
        insights = []
        
        try:
            # Zamansal desenleri analiz et
            time_analysis = self._analyze_temporal_patterns(temporal_patterns)
            
            # Temporal patterns JSON'ı string'e dönüştür
            patterns_text = json.dumps(temporal_patterns, default=str)

            # Gelişmiş zamansal analiz için özel prompt
            enhanced_prompt = f"""
            Zamansal Desenler Analizi:
            {patterns_text}
            
            Analiz Sonuçları:
            - En aktif saatler: {time_analysis.get('peak_hours', [])}
            - Haftalık desenler: {time_analysis.get('weekly_patterns', {})}
            - Aktivite sıklığı: {time_analysis.get('frequency_pattern', 'düzenli')}
            
            Bu verilerden actionable ve kişiselleştirilmiş zamansal içgörüler çıkar.
            """

            # Reflector'ün extract_meaningful_insights metodunu kullan
            insight_texts = self.reflector.extract_meaningful_insights(enhanced_prompt, count=3)
            
            # İçgörüleri yapılandırılmış formata dönüştür
            for i, text in enumerate(insight_texts):
                confidence = 0.9 if i == 0 else (0.8 if i == 1 else 0.7)  # İlk içgörü daha güvenilir
                
                # Zamansal içgörüler genellikle actionable'dır
                actionable = True
                
                # Proaktif aksiyon önerisi için Reflector'ü kullan
                action_prompt = f"Bu zamansal içgörüye dayalı proaktif aksiyon öner: {text}"
                action_suggestions = self.reflector.extract_meaningful_insights(action_prompt, count=1)
                suggested_action = action_suggestions[0] if action_suggestions else ""

                # Zamansal içgörü tipini belirle
                insight_type = "temporal_pattern"
                if "saat" in text.lower() or "hour" in text.lower():
                    insight_type = "time_preference"
                elif "gün" in text.lower() or "day" in text.lower():
                    insight_type = "daily_pattern"
                elif "hafta" in text.lower() or "week" in text.lower():
                    insight_type = "weekly_pattern"

                insights.append({
                    "type": insight_type,
                    "text": text,
                    "confidence": confidence,
                    "actionable": actionable,
                    "suggested_action": suggested_action,
                    "temporal_data": time_analysis
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Zamansal içgörü üretme hatası: {str(e)}")
            # Fallback içgörüler
            return [{
                "type": "temporal_pattern",
                "text": "Kullanıcı düzenli etkileşim saatleri gösteriyor, bu alışkanlık desteklenebilir.",
                "confidence": 0.7,
                "actionable": True,
                "suggested_action": "Kullanıcının aktif olduğu saatlerde proaktif destek sunmak."
            }]
    
    def _analyze_temporal_patterns(self, temporal_patterns: Dict) -> Dict:
        """Zamansal desenleri detaylı analiz eder."""
        try:
            analysis = {
                "peak_hours": [],
                "weekly_patterns": {},
                "frequency_pattern": "düzenli",
                "activity_distribution": {}
            }
            
            # Saat bazlı analiz
            if "hourly_activity" in temporal_patterns:
                hourly_data = temporal_patterns["hourly_activity"]
                if isinstance(hourly_data, dict):
                    # En aktif saatleri bul
                    sorted_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)
                    analysis["peak_hours"] = [hour for hour, count in sorted_hours[:3] if count > 0]
            
            # Haftalık analiz
            if "daily_activity" in temporal_patterns:
                daily_data = temporal_patterns["daily_activity"]
                if isinstance(daily_data, dict):
                    analysis["weekly_patterns"] = daily_data
                    
                    # Hafta içi vs hafta sonu
                    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    weekends = ["saturday", "sunday"]
                    
                    weekday_total = sum(daily_data.get(day, 0) for day in weekdays)
                    weekend_total = sum(daily_data.get(day, 0) for day in weekends)
                    
                    if weekday_total > weekend_total * 2:
                        analysis["frequency_pattern"] = "hafta_içi_odaklı"
                    elif weekend_total > weekday_total:
                        analysis["frequency_pattern"] = "hafta_sonu_odaklı"
                    else:
                        analysis["frequency_pattern"] = "dengeli"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Zamansal desen analizi hatası: {str(e)}")
            return {
                "peak_hours": [],
                "weekly_patterns": {},
                "frequency_pattern": "düzenli",
                "activity_distribution": {}
            }
    
    def generate_behavioral_insights(self, behavioral_patterns: Dict) -> List[Dict]:
        """Davranışsal desenlerden içgörüler"""
        try:
            # Davranışsal desenleri detaylı analiz et
            behavior_analysis = self._analyze_behavioral_patterns(behavioral_patterns)
            
            # Behavioral patterns JSON'ı string'e dönüştür
            patterns_text = json.dumps(behavioral_patterns, default=str)

            # Gelişmiş davranışsal analiz için özel prompt
            enhanced_prompt = f"""
            Davranışsal Desenler Analizi:
            {patterns_text}
            
            Detaylı Analiz:
            - İletişim stili: {behavior_analysis.get('communication_style', 'bilinmiyor')}
            - Yardım arama kalıpları: {behavior_analysis.get('help_seeking_patterns', [])}
            - Duygusal ifade tarzı: {behavior_analysis.get('emotional_expression', 'nötr')}
            - Etkileşim sıklığı: {behavior_analysis.get('interaction_frequency', 'orta')}
            - Tercih edilen konular: {behavior_analysis.get('preferred_topics', [])}
            
            Bu verilerden actionable ve kişiselleştirilmiş davranışsal içgörüler çıkar.
            Kullanıcının gelişimi ve daha iyi destek alması için öneriler sun.
            """

            # Reflector'ün extract_meaningful_insights metodunu kullan
            insight_texts = self.reflector.extract_meaningful_insights(enhanced_prompt, count=4)

            # İçgörüleri yapılandırılmış formata dönüştür
            insights = []
            for i, text in enumerate(insight_texts):
                confidence = 0.9 if i == 0 else (0.8 if i == 1 else (0.7 if i == 2 else 0.6))

                # İçgörü tipini gelişmiş analiz ile belirle
                insight_type = self._determine_behavioral_insight_type(text, behavior_analysis)

                # Davranışsal içgörüler genellikle actionable'dır
                actionable = True

                # Proaktif aksiyon önerisi için Reflector'ü kullan
                action_prompt = f"Bu davranışsal içgörüye dayalı spesifik ve uygulanabilir aksiyon öner: {text}"
                action_suggestions = self.reflector.extract_meaningful_insights(action_prompt, count=1)
                suggested_action = action_suggestions[0] if action_suggestions else ""

                insights.append({
                    "type": insight_type,
                    "text": text,
                    "confidence": confidence,
                    "actionable": actionable,
                    "suggested_action": suggested_action,
                    "behavioral_data": behavior_analysis
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Davranışsal içgörü üretme hatası: {str(e)}")
            # Fallback içgörüler
            return [
                {
                    "type": "communication_preference",
                    "text": "Kullanıcı düzenli etkileşim kuruyor ve destek almaya açık görünüyor.",
                    "confidence": 0.7,
                    "actionable": True,
                    "suggested_action": "Proaktif destek ve kişiselleştirilmiş öneriler sunmak."
                },
                {
                    "type": "help_preference",
                    "text": "Kullanıcının yardım alma konusunda pozitif bir yaklaşımı var.",
                    "confidence": 0.6,
                    "actionable": True,
                    "suggested_action": "Çeşitli konularda rehberlik ve kaynak önerileri sunmak."
                }
            ]
    
    def _analyze_behavioral_patterns(self, behavioral_patterns: Dict) -> Dict:
        """Davranışsal desenleri detaylı analiz eder."""
        try:
            analysis = {
                "communication_style": "bilinmiyor",
                "help_seeking_patterns": [],
                "emotional_expression": "nötr",
                "interaction_frequency": "orta",
                "preferred_topics": [],
                "response_patterns": {},
                "engagement_level": "orta"
            }
            
            # İletişim stili analizi
            if "message_types" in behavioral_patterns:
                msg_types = behavioral_patterns["message_types"]
                if isinstance(msg_types, dict):
                    total_messages = sum(msg_types.values())
                    if total_messages > 0:
                        question_ratio = msg_types.get("questions", 0) / total_messages
                        statement_ratio = msg_types.get("statements", 0) / total_messages
                        
                        if question_ratio > 0.4:
                            analysis["communication_style"] = "sorgulayıcı"
                        elif statement_ratio > 0.6:
                            analysis["communication_style"] = "bildirimsel"
                        else:
                            analysis["communication_style"] = "dengeli"
            
            # Yardım arama kalıpları
            if "help_requests" in behavioral_patterns:
                help_data = behavioral_patterns["help_requests"]
                if isinstance(help_data, dict):
                    analysis["help_seeking_patterns"] = list(help_data.keys())
            
            # Duygusal ifade analizi
            if "emotional_indicators" in behavioral_patterns:
                emotional_data = behavioral_patterns["emotional_indicators"]
                if isinstance(emotional_data, dict):
                    dominant_emotion = max(emotional_data.items(), key=lambda x: x[1])[0] if emotional_data else "nötr"
                    analysis["emotional_expression"] = dominant_emotion
            
            # Etkileşim sıklığı
            if "interaction_frequency" in behavioral_patterns:
                freq = behavioral_patterns["interaction_frequency"]
                if isinstance(freq, (int, float)):
                    if freq > 10:
                        analysis["interaction_frequency"] = "yüksek"
                    elif freq > 5:
                        analysis["interaction_frequency"] = "orta"
                    else:
                        analysis["interaction_frequency"] = "düşük"
            
            # Tercih edilen konular
            if "topic_preferences" in behavioral_patterns:
                topics = behavioral_patterns["topic_preferences"]
                if isinstance(topics, list):
                    analysis["preferred_topics"] = topics[:5]  # En fazla 5 konu
                elif isinstance(topics, dict):
                    # Sıklığa göre sırala
                    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
                    analysis["preferred_topics"] = [topic for topic, count in sorted_topics[:5]]
            
            # Engagement seviyesi
            engagement_indicators = 0
            if behavioral_patterns.get("session_length", 0) > 5:
                engagement_indicators += 1
            if behavioral_patterns.get("follow_up_questions", 0) > 2:
                engagement_indicators += 1
            if behavioral_patterns.get("detailed_responses", 0) > 3:
                engagement_indicators += 1
            
            if engagement_indicators >= 2:
                analysis["engagement_level"] = "yüksek"
            elif engagement_indicators == 1:
                analysis["engagement_level"] = "orta"
            else:
                analysis["engagement_level"] = "düşük"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Davranışsal desen analizi hatası: {str(e)}")
            return {
                "communication_style": "bilinmiyor",
                "help_seeking_patterns": [],
                "emotional_expression": "nötr",
                "interaction_frequency": "orta",
                "preferred_topics": [],
                "response_patterns": {},
                "engagement_level": "orta"
            }
    
    def _determine_behavioral_insight_type(self, insight_text: str, behavior_analysis: Dict) -> str:
        """İçgörü metnine ve davranışsal analize göre içgörü tipini belirler."""
        text_lower = insight_text.lower()
        
        # Anahtar kelime bazlı sınıflandırma
        if any(word in text_lower for word in ["iletişim", "konuşma", "soru", "yanıt"]):
            return "communication_preference"
        elif any(word in text_lower for word in ["yardım", "destek", "çözüm", "problem"]):
            return "help_preference"
        elif any(word in text_lower for word in ["duygu", "his", "emotion", "feel"]):
            return "emotional_pattern"
        elif any(word in text_lower for word in ["zaman", "saat", "sıklık", "düzen"]):
            return "temporal_behavior"
        elif any(word in text_lower for word in ["konu", "ilgi", "tercih", "odak"]):
            return "interest_pattern"
        elif any(word in text_lower for word in ["öğren", "gelişim", "ilerleme", "başarı"]):
            return "learning_pattern"
        else:
            # Davranışsal analiz verilerine göre varsayılan tip belirle
            if behavior_analysis.get("communication_style") == "sorgulayıcı":
                return "curiosity_pattern"
            elif behavior_analysis.get("engagement_level") == "yüksek":
                return "engagement_pattern"
            else:
                return "general_behavior"
    
    def synthesize_cross_pattern_insights(self, all_patterns: Dict) -> Dict[str, Any]:
        """Farklı desenleri birleştirerek meta-içgörüler"""
        try:
            # Çapraz desen analizi yap
            cross_analysis = self._perform_cross_pattern_analysis(all_patterns)
            
            # Tüm desenleri metin olarak birleştir
            all_patterns_text = f"""
            TEMPORAL PATTERNS: {json.dumps(all_patterns.get('temporal', {}), default=str)}
            BEHAVIORAL PATTERNS: {json.dumps(all_patterns.get('behavioral', {}), default=str)}
            EMOTIONAL PATTERNS: {json.dumps(all_patterns.get('emotional', {}), default=str)}
            
            CROSS-PATTERN ANALYSIS:
            - Pattern correlations: {cross_analysis.get('correlations', {})}
            - Dominant themes: {cross_analysis.get('dominant_themes', [])}
            - Behavioral-temporal alignment: {cross_analysis.get('behavioral_temporal_alignment', 'unknown')}
            - Emotional consistency: {cross_analysis.get('emotional_consistency', 'stable')}
            """

            # Gelişmiş çapraz analiz için özel promptlar
            core_needs_prompt = f"""
            Bu kapsamlı kullanıcı verilerinden temel ihtiyaçları belirle:
            {all_patterns_text}
            
            Kullanıcının en temel 3 ihtiyacını belirle (örn: sosyal_bağlantı, öğrenme_desteği, zaman_yönetimi).
            """
            
            support_areas_prompt = f"""
            Bu kullanıcı verilerinden destek alanlarını belirle:
            {all_patterns_text}
            
            Kullanıcının en çok desteğe ihtiyaç duyduğu 3 alanı belirle.
            """

            # Reflector'ün metodlarını kullanarak temalar ve içgörüler çıkar
            core_needs = self.reflector.extract_themes(
                [{"message": core_needs_prompt}],
                top_n=3
            )

            support_areas = self.reflector.extract_themes(
                [{"message": support_areas_prompt}],
                top_n=3
            )

            # Gelişmiş içgörü üretimi
            relationship_opportunities = self.reflector.extract_meaningful_insights(
                f"""Bu çapraz desen analizine dayalı ilişki geliştirme fırsatları:
                {all_patterns_text}
                
                Kullanıcı ile daha güçlü bir ilişki kurmak için spesifik fırsatları belirle.""",
                count=3
            )
            
            proactive_actions = self.reflector.extract_meaningful_insights(
                f"""Bu kapsamlı analize dayalı proaktif aksiyonlar:
                {all_patterns_text}
                
                Kullanıcının deneyimini iyileştirmek için alınabilecek spesifik ve uygulanabilir aksiyonları belirle.""",
                count=4
            )
            
            # Gelişmiş meta-içgörüler
            meta_insights = self.reflector.extract_meaningful_insights(
                f"""Bu çapraz desen analizinden meta-seviye içgörüler:
                {all_patterns_text}
                
                Kullanıcının genel davranış kalıpları, motivasyonları ve gelişim potansiyeli hakkında üst düzey içgörüler çıkar.""",
                count=3
            )
            
            # Yapılandırılmış yanıt oluştur
            return {
                "core_needs": core_needs,
                "support_areas": support_areas,
                "relationship_opportunities": relationship_opportunities,
                "proactive_actions": proactive_actions,
                "meta_insights": meta_insights,
                "cross_pattern_analysis": cross_analysis,
                "synthesis_confidence": self._calculate_synthesis_confidence(all_patterns),
                "recommended_focus_areas": self._identify_focus_areas(cross_analysis, core_needs)
            }
            
        except Exception as e:
            logger.error(f"Çapraz desen sentezi hatası: {str(e)}")
            # Fallback yanıt
            return {
                "core_needs": ["genel_destek", "bilgi_erişimi", "etkileşim"],
                "support_areas": ["teknik_yardım", "rehberlik", "motivasyon"],
                "relationship_opportunities": [
                    "Daha kişiselleştirilmiş etkileşimler kurma",
                    "Kullanıcı tercihlerini daha iyi anlama",
                    "Proaktif destek sunma"
                ],
                "proactive_actions": [
                    "Düzenli check-in'ler yapma",
                    "Kişiselleştirilmiş öneriler sunma",
                    "Kullanıcı feedback'i alma"
                ],
                "meta_insights": [
                    "Kullanıcı sistemle pozitif etkileşim kuruyor",
                    "Gelişim odaklı bir yaklaşım sergiliyor",
                    "Destek almaya açık görünüyor"
                ],
                "synthesis_confidence": 0.6
            }
    
    def _perform_cross_pattern_analysis(self, all_patterns: Dict) -> Dict:
        """Farklı desenler arasında çapraz analiz yapar."""
        try:
            analysis = {
                "correlations": {},
                "dominant_themes": [],
                "behavioral_temporal_alignment": "unknown",
                "emotional_consistency": "stable",
                "pattern_strength": {}
            }
            
            temporal = all_patterns.get('temporal', {})
            behavioral = all_patterns.get('behavioral', {})
            emotional = all_patterns.get('emotional', {})
            
            # Temporal-Behavioral korelasyon
            if temporal and behavioral:
                # Aktivite saatleri ile davranış kalıpları arasında uyum var mı?
                peak_hours = temporal.get('peak_hours', [])
                interaction_freq = behavioral.get('interaction_frequency', 'orta')
                
                if peak_hours and interaction_freq == 'yüksek':
                    analysis["behavioral_temporal_alignment"] = "strong"
                elif peak_hours:
                    analysis["behavioral_temporal_alignment"] = "moderate"
                else:
                    analysis["behavioral_temporal_alignment"] = "weak"
            
            # Duygusal tutarlılık
            if emotional:
                emotional_variance = emotional.get('emotional_variance', 0.5)
                if emotional_variance < 0.3:
                    analysis["emotional_consistency"] = "very_stable"
                elif emotional_variance < 0.6:
                    analysis["emotional_consistency"] = "stable"
                else:
                    analysis["emotional_consistency"] = "variable"
            
            # Dominant temalar
            themes = []
            if behavioral.get('preferred_topics'):
                themes.extend(behavioral['preferred_topics'][:3])
            if temporal.get('activity_patterns'):
                themes.append("time_conscious")
            if emotional.get('dominant_emotion') and emotional['dominant_emotion'] != 'neutral':
                themes.append(f"emotionally_{emotional['dominant_emotion']}")
            
            analysis["dominant_themes"] = themes[:5]
            
            # Desen güçleri
            analysis["pattern_strength"] = {
                "temporal": len(temporal) / 5.0 if temporal else 0.0,  # Normalize to 0-1
                "behavioral": len(behavioral) / 7.0 if behavioral else 0.0,
                "emotional": len(emotional) / 4.0 if emotional else 0.0
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Çapraz desen analizi hatası: {str(e)}")
            return {
                "correlations": {},
                "dominant_themes": [],
                "behavioral_temporal_alignment": "unknown",
                "emotional_consistency": "stable",
                "pattern_strength": {}
            }
    
    def _calculate_synthesis_confidence(self, all_patterns: Dict) -> float:
        """Sentez güvenilirlik skorunu hesaplar."""
        try:
            confidence = 0.0
            pattern_count = 0
            
            # Her desen türü için veri kalitesini değerlendir
            for pattern_type, patterns in all_patterns.items():
                if patterns and isinstance(patterns, dict):
                    pattern_count += 1
                    # Veri zenginliğine göre güven skoru
                    data_richness = len(patterns) / 10.0  # Normalize
                    confidence += min(data_richness, 1.0)
            
            if pattern_count > 0:
                confidence = confidence / pattern_count
            else:
                confidence = 0.3  # Minimum güven
            
            # Çapraz korelasyon varsa güveni artır
            if pattern_count >= 2:
                confidence += 0.1
            if pattern_count >= 3:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Güven skoru hesaplama hatası: {str(e)}")
            return 0.5
    
    def _identify_focus_areas(self, cross_analysis: Dict, core_needs: List[str]) -> List[str]:
        """Odaklanılması gereken alanları belirler."""
        try:
            focus_areas = []
            
            # Güçlü desenler varsa onlara odaklan
            pattern_strength = cross_analysis.get('pattern_strength', {})
            strongest_pattern = max(pattern_strength.items(), key=lambda x: x[1])[0] if pattern_strength else None
            
            if strongest_pattern:
                focus_areas.append(f"{strongest_pattern}_optimization")
            
            # Temel ihtiyaçları ekle
            focus_areas.extend(core_needs[:2])  # En önemli 2 ihtiyaç
            
            # Çapraz korelasyonlara göre ek alanlar
            alignment = cross_analysis.get('behavioral_temporal_alignment', 'unknown')
            if alignment == 'weak':
                focus_areas.append("temporal_behavioral_sync")
            
            consistency = cross_analysis.get('emotional_consistency', 'stable')
            if consistency == 'variable':
                focus_areas.append("emotional_stability_support")
            
            return focus_areas[:4]  # En fazla 4 odak alanı
            
        except Exception as e:
            logger.error(f"Odak alanları belirleme hatası: {str(e)}")
            return ["general_improvement", "user_engagement"]