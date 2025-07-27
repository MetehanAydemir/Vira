"""
Kullanıcı etkileşim desenlerini analiz eden modül.
Zamansal ve davranışsal desenleri tespit eder.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class TemporalPatternAnalyzer:
    """Zaman bazlı desen analizi"""
    
    def analyze_conversation_timing(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Konuşma zamanlaması analizi"""
        if not conversations:
            return {"error": "No conversations to analyze"}
        
        timestamps = [conv.get('created_at') for conv in conversations if conv.get('created_at')]
        if not timestamps:
            return {"error": "No valid timestamps found"}
        
        # Saat bazlı dağılım
        hourly_distribution = {}
        for ts in timestamps:
            hour = ts.hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        # En aktif saatleri bul
        preferred_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "preferred_hours": [hour for hour, count in preferred_hours],
            "hourly_distribution": hourly_distribution,
            "most_active_period": self._find_most_active_period(timestamps)
        }
    
    def detect_emotional_cycles(self, emotional_timeline: List[Dict]) -> Dict[str, Any]:
        """Duygusal döngüleri tespit et"""
        if not emotional_timeline:
            return {"error": "No emotional data to analyze"}
        
        # Haftalık pattern'leri bul
        weekly_emotions = {}
        for emotion_data in emotional_timeline:
            if not emotion_data.get('created_at'):
                continue
                
            day_of_week = emotion_data['created_at'].weekday()
            if day_of_week not in weekly_emotions:
                weekly_emotions[day_of_week] = []
                
            weekly_emotions[day_of_week].append(emotion_data.get('emotional_tone', 'neutral'))
        
        # Pattern'leri analiz et
        patterns = {}
        for day, emotions in weekly_emotions.items():
            # En sık görülen duygu
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
            if emotion_counts:
                dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
                patterns[day] = dominant_emotion[0]
        
        return {
            "weekly_emotional_pattern": patterns,
            "emotional_stability": self._calculate_emotional_stability(emotional_timeline),
            "mood_swing_frequency": self._detect_mood_swings(emotional_timeline)
        }
    
    def _find_most_active_period(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """En aktif zaman dilimini bul"""
        # Sabah, öğle, akşam ve gece olarak kategorize et
        periods = {
            "morning": 0,   # 6-12
            "afternoon": 0, # 12-18
            "evening": 0,   # 18-24
            "night": 0      # 0-6
        }
        
        for ts in timestamps:
            hour = ts.hour
            if 6 <= hour < 12:
                periods["morning"] += 1
            elif 12 <= hour < 18:
                periods["afternoon"] += 1
            elif 18 <= hour < 24:
                periods["evening"] += 1
            else:
                periods["night"] += 1
        
        most_active = max(periods.items(), key=lambda x: x[1])
        return {
            "period": most_active[0],
            "count": most_active[1],
            "all_periods": periods
        }
    
    def _calculate_emotional_stability(self, emotional_timeline: List[Dict]) -> float:
        """Duygusal stabilite skorunu hesapla"""
        if not emotional_timeline:
            return 0.0
            
        # Basit implementasyon: Aynı duygunun tekrar oranı
        emotions = [e.get('emotional_tone', 'neutral') for e in emotional_timeline]
        unique_emotions = set(emotions)
        
        if not emotions:
            return 0.0
            
        # Daha az benzersiz duygu = daha stabil
        stability = 1 - (len(unique_emotions) / len(emotions))
        return stability
    
    def _detect_mood_swings(self, emotional_timeline: List[Dict]) -> Dict[str, Any]:
        """Ruh hali değişimlerini tespit et"""
        if len(emotional_timeline) < 2:
            return {"frequency": 0, "changes": []}
            
        changes = []
        prev_emotion = emotional_timeline[0].get('emotional_tone', 'neutral')
        
        for i in range(1, len(emotional_timeline)):
            curr_emotion = emotional_timeline[i].get('emotional_tone', 'neutral')
            if curr_emotion != prev_emotion:
                changes.append({
                    "from": prev_emotion,
                    "to": curr_emotion,
                    "timestamp": emotional_timeline[i].get('created_at')
                })
                prev_emotion = curr_emotion
        
        return {
            "frequency": len(changes),
            "changes": changes
        }


class BehavioralPatternAnalyzer:
    """Davranış deseni analizi"""
    
    def analyze_communication_style(self, conversations: List[Dict]) -> Dict[str, Any]:
        """İletişim tarzı analizi"""
        if not conversations:
            return {"error": "No conversations to analyze"}
            
        message_lengths = [len(conv.get('message', '')) for conv in conversations]
        response_preferences = [len(conv.get('response', '')) for conv in conversations]
        
        if not message_lengths or not response_preferences:
            return {"error": "Invalid conversation data"}
            
        return {
            "avg_message_length": sum(message_lengths) / max(len(message_lengths), 1),
            "preferred_response_length": sum(response_preferences) / max(len(response_preferences), 1),
            "communication_frequency": len(conversations),
            "question_asking_frequency": self._count_questions(conversations)
        }
    
    def analyze_help_seeking_behavior(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Yardım arama davranışı"""
        if not conversations:
            return {"error": "No conversations to analyze"}
            
        help_seeking_intents = ['problem_solving', 'advice_seeking', 'emotional_support', 'technical_help']
        help_conversations = [c for c in conversations if c.get('intent_type') in help_seeking_intents]
        
        if not help_conversations:
            return {
                "help_seeking_frequency": 0,
                "preferred_help_type": None,
                "problem_solving_approach": None
            }
            
        return {
            "help_seeking_frequency": len(help_conversations),
            "preferred_help_type": self._find_dominant_help_type(help_conversations),
            "problem_solving_approach": self._analyze_problem_solving_style(help_conversations)
        }
    
    def _count_questions(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Soru sorma sıklığını sayar"""
        question_count = 0
        total_msgs = len(conversations)
        
        for conv in conversations:
            message = conv.get('message', '')
            if message and ('?' in message or message.lower().startswith(('what', 'why', 'how', 'when', 'where', 'who', 'which'))):
                question_count += 1
        
        return {
            "total": question_count,
            "percentage": (question_count / total_msgs) * 100 if total_msgs > 0 else 0
        }
    
    def _find_dominant_help_type(self, help_conversations: List[Dict]) -> str:
        """En baskın yardım türünü bul"""
        intent_counts = {}
        for conv in help_conversations:
            intent = conv.get('intent_type', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        if not intent_counts:
            return "unknown"
            
        return max(intent_counts.items(), key=lambda x: x[1])[0]
    
    def _analyze_problem_solving_style(self, help_conversations: List[Dict]) -> Dict[str, Any]:
        """Problem çözme yaklaşımını analiz et"""
        # Basit implementasyon - gerçek sistemde NLP ile daha detaylı analiz yapılabilir
        message_lengths = [len(conv.get('message', '')) for conv in help_conversations]
        avg_length = sum(message_lengths) / max(len(message_lengths), 1) if message_lengths else 0
        
        if avg_length < 50:
            style = "direct"
            description = "Kullanıcı sorunları kısa ve öz bir şekilde ifade ediyor"
        elif avg_length < 150:
            style = "balanced"
            description = "Kullanıcı sorunları makul detaylarla açıklıyor"
        else:
            style = "detailed"
            description = "Kullanıcı sorunları çok detaylı ve kapsamlı anlatıyor"
        
        return {
            "style": style,
            "description": description,
            "avg_problem_description_length": avg_length
        }