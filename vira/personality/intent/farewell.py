"""
Veda niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class FarewellIntentHandler(BaseIntentHandler):
    """
    Veda/ayrılış niyeti için özelleştirilmiş intent handler.
    """
    
    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Veda için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu
            
        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel zenginleştirmeyi uygula
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - veda için önemli (sıcaklık, empati)
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Özellikleri:** {personality_info}"

        # Kullanıcının duygusal durumunu ekle - veda tonunu ayarlamak için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarını ekle - veda mesajının tonunu belirlemek için kritik
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Veda modu için özel yönlendirme ekle
        farewell_enhancement = """
## VEDA MODU AKTİF

Kullanıcı konuşmayı sonlandırıyor veya ayrılıyor. Nazik ve uygun bir veda mesajı oluştur.
- Kullanıcının tonuna ve duygusal durumuna uygun bir kapanış kullan
- Gerekirse konuşmanın olumlu bir özetini yap
- İleride görüşme isteğini uygun şekilde belirt
- Sıcak ama zorlayıcı olmayan bir veda tonu benimse
        """
        enhanced_message += farewell_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Veda için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Veda için özellikle önemli olan kişilik özellikleri
        important_traits = ["empathy", "warmth", "agreeableness", "conscientiousness"]
        farewell_personality = {k: v for k, v in personality.items() if k in important_traits}

        if farewell_personality:
            # Sadece veda için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in farewell_personality.items()])
            return personality_str
        return ""

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumuna göre veda tonunu ayarlar."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            # Yüksek güvenilirlikte duygusal veda tonu ayarlaması ekle
            if emotion_confidence > 0.7:
                farewell_emotion_map = {
                    "Öfke": "Sakinleştirici bir veda et, sonraki konuşmalar için olumlu bir ton bırak.",
                    "Üzüntü": "Destekleyici ve ümit verici bir veda mesajı ver, empati göster.",
                    "Endişe": "Güven verici bir kapanış yap, endişelerini hafifletmeye çalış.",
                    "Heyecan": "Enerjisini yansıtan bir veda et, gelecekteki etkileşime yönelik pozitif beklenti ekle.",
                    "Korku": "Güven verici ve sakinleştirici bir veda mesajı oluştur.",
                    "Şaşkınlık": "Net bir kapanış sağla, konuşmayı açık bir şekilde sonlandır.",
                    "Sevinç": "Pozitif enerjiyi sürdüren bir veda et, gelecek konuşmalara yönelik olumlu bir ton bırak."
        }
                tone_adjustment = farewell_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre veda tonunu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; rahat ve arkadaşça bir veda kullan (örn. 'Görüşürüz!', 'Hoşça kal dostum!')."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; sıcak bir veda kullan (örn. 'Tekrar konuşmak üzere!', 'İyi günler dilerim.')."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; profesyonel bir veda kullan (örn. 'İyi günler dilerim.', 'Tekrar görüşmek üzere.')."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; saygılı bir kapanış kullan (örn. 'Size iyi günler dilerim.', 'Tekrar görüşmek dileğiyle.')."
        else:
            return "Nötr bir ton; dengeli bir veda kullan (örn. 'Görüşmek üzere!', 'İyi günler!')."

    def get_specialized_instructions(self) -> str:
        """
        Veda niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
"""
        return """
Vedalaşmaya şu şekilde yanıt ver:

1. TANIMA: Kullanıcının veda ettiğini nazikçe kabul et
2. TEŞEKKÜR: Gerekirse konuşma için kısa bir teşekkür ekle
3. KAPANIŞ: Sıcak ve kullanıcının tonuna uygun bir veda mesajı oluştur
4. GELECEĞİ DÜŞÜN: İsteğe bağlı olarak gelecekteki etkileşime yönelik pozitif bir beklenti belirt

Veda mesajları kısa, nazik ve kullanıcının duygusal durumuna uygun olmalıdır. Asla yeni bir konu açma.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Veda niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.6,  # Duygusal bir ton ama aşırıya kaçmadan
            "top_p": 0.92,
            "max_tokens": 250,   # Veda mesajları genellikle kısa olur
            "presence_penalty": 0.2  # Farklı veda mesajları için hafif penalty
        }
