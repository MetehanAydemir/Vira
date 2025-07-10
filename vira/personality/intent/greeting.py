"""
Selamlaşma niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class GreetingIntentHandler(BaseIntentHandler):
    """
    Selamlaşma niyeti için özelleştirilmiş intent handler.
    """
    
    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Selamlaşma için sistem mesajını zenginleştir.
        
        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu
            
        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel zenginleştirmeyi uygula
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - selamlaşma için önemli
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Kullanıcının duygusal durumunu ekle - ton ayarlaması için önemli
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Kullanıcı tarzına göre formality ayarını ekle - selamlaşma tonunu belirlemek için önemli
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Selamlaşma modu için özel yönlendirme ekle
        greeting_enhancement = """
## SELAMLAŞMA MODU AKTİF

Kullanıcı seni selamlıyor. Sıcak ve samimi bir karşılama ver.
- Günün saatine uygun selamlaşma kullan (sabah/öğle/akşam)
- Kullanıcının önceki etkileşimlerini dikkate al
- Konuşmayı başlatmaya yardımcı ol
- Karşılama tonunda kişiliğini yansıt
        """
        enhanced_message += greeting_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Selamlaşma için özellikle önemli olan kişilik özellikleri
        important_traits = ["empathy", "extraversion", "openness", "agreeableness"]
        greeting_personality = {k: v for k, v in personality.items() if k in important_traits}

        if greeting_personality:
            # Sadece selamlaşma için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in greeting_personality.items()])
            return personality_str
        return ""

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ve ton ayarlamasını ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            # Yüksek güvenilirlikte duygusal ton ayarlaması ekle
            if emotion_confidence > 0.7:
                emotion_map = {
                    "Öfke": "Yanıt verirken daha yatıştırıcı ol. Sakinleştirici bir ton kullan.",
                    "Üzüntü": "Nazik ve empatik bir ton benimse. Destek verici cümleler kullan.",
                    "Endişe": "Güven verici ve net bir dil kullan.",
                    "Heyecan": "Kullanıcının heyecanına karşılık ver ve enerjiyi yansıt.",
                    "Korku": "Sakinleştirici ve güven verici ol.",
                    "Şaşkınlık": "Açıklayıcı ve bilgilendirici ol.",
                    "Sevinç": "Olumlu enerjiyi yansıt, kutlayıcı bir dil kullan."
        }
                tone_adjustment = emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre ton ayarlama bilgisi ekler."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; sen de arkadaşça bir selamlama kullan."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; sıcak ve rahat bir karşılama yap."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; daha resmi bir selamlama kullan."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; saygılı bir karşılama tercih et."
        else:
            return "Nötr bir ton; dengeli bir karşılama kullan."

    def get_specialized_instructions(self) -> str:
        """
        Bu niyet türü için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Selamlaşmaya şu şekilde yanıt ver:

1. KARŞILAMA: Sıcak ve samimi bir selamlama ile başla.
2. KİŞİSELLEŞTİRME: Mümkünse kullanıcının adını kullan veya daha önceki etkileşimlere atıf yap.
3. ETKİLEŞİM: Kullanıcıyı konuşmaya teşvik edecek bir soru veya yorum ekle.

Selamlaşmalar kısa ve samimi olmalı, resmiyet düzeyini kullanıcının önceki etkileşimlerine göre ayarla.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Selamlaşma niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.7,  # Sıcak ve doğal bir ton için orta-yüksek sıcaklık
            "top_p": 0.9,
            "max_tokens": 300,   # Selamlaşmalar genellikle kısa olur
            "presence_penalty": 0.3  # Değişken yanıtlar için hafif penalty
        }
