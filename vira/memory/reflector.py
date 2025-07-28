"""
Hafıza ve empati yansıtma işlemleri için yardımcı fonksiyonlar.
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from vira.utils.llm_client import call_chat_model
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class Reflector:
    """
    Hafıza verilerini analiz ederek anlamlı içgörüler ve temalar çıkaran sınıf.
    """
    
    def __init__(self, llm_client=None):
        """
        Reflector'ı başlatır.
        
        Args:
            llm_client: LLM istemcisi (opsiyonel)
        """
        self.llm_client = llm_client
        
    def extract_meaningful_insights(self, content: str, count: int = 3) -> List[str]:
        """
        Verilen içerikten anlamlı içgörüler çıkarır.
        
        Args:
            content: Analiz edilecek içerik
            count: Çıkarılacak içgörü sayısı
            
        Returns:
            İçgörü listesi
        """
        try:
            # LLM ile içgörü çıkarma
            messages = [
                {
                    "role": "system",
                    "content": """Sen bir uzman psikolog ve veri analistisin. Verilen içerikten anlamlı, actionable ve kişiselleştirilmiş içgörüler çıkarman gerekiyor.

İçgörüler şu kriterleri karşılamalı:
1. Spesifik ve actionable olmalı
2. Kullanıcının davranış kalıplarını yansıtmalı
3. Gelişim ve iyileştirme odaklı olmalı
4. Kısa ve net olmalı (1-2 cümle)

Her içgörüyü ayrı satırda ver, numaralandırma kullanma."""
                },
                {
                    "role": "user",
                    "content": f"Bu içerikten {count} adet anlamlı içgörü çıkar:\n\n{content}"
                }
            ]
            
            response = call_chat_model(messages, temperature=0.7, max_tokens=500)
            
            # Yanıtı satırlara böl ve temizle
            insights = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    # Numaralandırma varsa temizle
                    line = re.sub(r'^\d+[\.\)]\s*', '', line)
                    line = re.sub(r'^[-\*]\s*', '', line)
                    insights.append(line.strip())
            
            # İstenen sayıda içgörü döndür
            return insights[:count] if insights else [
                "Kullanıcı düzenli etkileşim gösteriyor, bu pozitif bir engagement işareti.",
                "Daha kişiselleştirilmiş destek sunmak için kullanıcı tercihlerini öğrenmek faydalı olabilir.",
                "Proaktif yardım önerileri kullanıcı deneyimini geliştirebilir."
            ][:count]
            
        except Exception as e:
            logger.error(f"İçgörü çıkarma hatası: {str(e)}")
            # Fallback içgörüler
            fallback_insights = [
                "Kullanıcı sistemle aktif olarak etkileşim kuruyor.",
                "Daha iyi destek için kullanıcı ihtiyaçlarını anlamak önemli.",
                "Kişiselleştirilmiş yaklaşım kullanıcı memnuniyetini artırabilir.",
                "Proaktif öneriler kullanıcı deneyimini zenginleştirebilir.",
                "Düzenli feedback alma kullanıcı ilişkisini güçlendirebilir."
            ]
            return fallback_insights[:count]
    
    def extract_themes(self, messages: List[Dict], top_n: int = 5) -> List[str]:
        """
        Mesajlardan ana temaları çıkarır.
        
        Args:
            messages: Mesaj listesi
            top_n: Çıkarılacak tema sayısı
            
        Returns:
            Tema listesi
        """
        try:
            # Mesajları birleştir
            combined_content = ""
            for msg in messages:
                if isinstance(msg, dict) and "message" in msg:
                    combined_content += msg["message"] + " "
                elif isinstance(msg, dict) and "content" in msg:
                    combined_content += msg["content"] + " "
                elif isinstance(msg, str):
                    combined_content += msg + " "
            
            if not combined_content.strip():
                return ["genel_konuşma", "yardım_talebi", "bilgi_paylaşımı"][:top_n]
            
            # LLM ile tema çıkarma
            messages_for_llm = [
                {
                    "role": "system",
                    "content": """Sen bir metin analisti ve tema çıkarma uzmanısın. Verilen metinlerden ana temaları çıkarman gerekiyor.

Temalar şu kriterleri karşılamalı:
1. Kısa ve öz olmalı (1-3 kelime)
2. Türkçe olmalı
3. Genel kategoriler olmalı (çok spesifik olmamalı)
4. Alt çizgi ile birleştirilmiş kelimeler kullan (örn: zaman_yönetimi)

Her temayı ayrı satırda ver, numaralandırma kullanma."""
                },
                {
                    "role": "user",
                    "content": f"Bu metinlerden {top_n} adet ana tema çıkar:\n\n{combined_content[:2000]}"
                }
            ]
            
            response = call_chat_model(messages_for_llm, temperature=0.5, max_tokens=300)
            
            # Yanıtı temizle ve temaları çıkar
            themes = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Numaralandırma ve işaretleri temizle
                    line = re.sub(r'^\d+[\.\)]\s*', '', line)
                    line = re.sub(r'^[-\*]\s*', '', line)
                    # Boşlukları alt çizgi ile değiştir
                    theme = line.strip().lower().replace(' ', '_').replace('-', '_')
                    if theme and len(theme) > 2:
                        themes.append(theme)
            
            # Fallback temalar
            if not themes:
                themes = ["genel_konuşma", "yardım_talebi", "bilgi_paylaşımı", "teknik_destek", "kişisel_gelişim"]
            
            return themes[:top_n]
            
        except Exception as e:
            logger.error(f"Tema çıkarma hatası: {str(e)}")
            # Fallback temalar
            return ["genel_konuşma", "yardım_talebi", "bilgi_paylaşımı", "teknik_destek", "kişisel_gelişim"][:top_n]
    
    def analyze_emotional_patterns(self, messages: List[Dict]) -> Dict[str, Any]:
        """
        Mesajlardan duygusal kalıpları analiz eder.
        
        Args:
            messages: Mesaj listesi
            
        Returns:
            Duygusal analiz sonuçları
        """
        try:
            # Mesajları birleştir
            combined_content = ""
            for msg in messages:
                if isinstance(msg, dict) and "message" in msg:
                    combined_content += msg["message"] + " "
                elif isinstance(msg, dict) and "content" in msg:
                    combined_content += msg["content"] + " "
            
            if not combined_content.strip():
                return {
                    "dominant_emotion": "neutral",
                    "emotion_intensity": 0.5,
                    "emotional_stability": 0.7,
                    "positive_ratio": 0.6
                }
            
            # LLM ile duygusal analiz
            messages_for_llm = [
                {
                    "role": "system",
                    "content": """Sen bir duygusal analiz uzmanısın. Verilen metinlerdeki duygusal kalıpları analiz etmen gerekiyor.

Analiz sonucunu JSON formatında ver:
{
    "dominant_emotion": "pozitif/negatif/neutral/mixed",
    "emotion_intensity": 0.0-1.0 arası sayı,
    "emotional_stability": 0.0-1.0 arası sayı,
    "positive_ratio": 0.0-1.0 arası sayı
}"""
                },
                {
                    "role": "user",
                    "content": f"Bu metinlerdeki duygusal kalıpları analiz et:\n\n{combined_content[:1500]}"
                }
            ]
            
            response = call_chat_model(
                messages_for_llm,
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            # JSON yanıtını parse et
            try:
                result = json.loads(response)
                # Değerleri doğrula ve sınırla
                return {
                    "dominant_emotion": result.get("dominant_emotion", "neutral"),
                    "emotion_intensity": max(0.0, min(1.0, float(result.get("emotion_intensity", 0.5)))),
                    "emotional_stability": max(0.0, min(1.0, float(result.get("emotional_stability", 0.7)))),
                    "positive_ratio": max(0.0, min(1.0, float(result.get("positive_ratio", 0.6))))
                }
            except (json.JSONDecodeError, ValueError, TypeError):
                logger.warning("LLM yanıtı JSON parse edilemedi, fallback değerler kullanılıyor")
                return {
                    "dominant_emotion": "neutral",
                    "emotion_intensity": 0.5,
                    "emotional_stability": 0.7,
                    "positive_ratio": 0.6
                }
                
        except Exception as e:
            logger.error(f"Duygusal analiz hatası: {str(e)}")
            return {
                "dominant_emotion": "neutral",
                "emotion_intensity": 0.5,
                "emotional_stability": 0.7,
                "positive_ratio": 0.6
            }

def compute_empathy_annotation(message: str, user_model: Optional[Dict[str, Any]] = None) -> str:
    """
    Kullanıcı mesajını analiz ederek empati notları oluşturur.
    
    Args:
        message: Kullanıcı mesajı
        user_model: Kullanıcı mental modeli (opsiyonel)
        
    Returns:
        Empati notları içeren string
    """
    # Basit bir empati notu oluştur
    # Gerçek implementasyonda daha karmaşık bir analiz yapılabilir
    empathy_note = "Bu mesajda kullanıcının duygusal durumunu dikkate al."
    
    # Eğer kullanıcı modeli varsa, daha kişiselleştirilmiş notlar ekle
    if user_model:
        if "emotional_state" in user_model:
            emotional_state = user_model["emotional_state"]
            empathy_note += f" Kullanıcının duygusal durumu: {emotional_state}."
            
        if "communication_preferences" in user_model:
            comm_prefs = user_model["communication_preferences"]
            empathy_note += f" İletişim tercihleri: {comm_prefs}."
    
    return empathy_note