"""
Duygu paylaşımı niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class EmotionalIntentHandler(BaseIntentHandler):
    """
    Duygu paylaşımı niyeti için özelleştirilmiş intent handler.
    Kullanıcı duygusal paylaşımda bulunduğunda veya duygusal yanıt beklediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Duygusal paylaşım için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Duygusal durum bilgisini ekle - duygusal ton için kritik
        emotion_context = self._add_enhanced_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum ve Ton:** {emotion_context}"

        # Empati ve duygusal özellikleri vurgula
        empathy_info = self._add_empathy_info(enhanced_message, state)
        if empathy_info:
            enhanced_message += f"\n\n**Duygusal Özelliklerim:** {empathy_info}"

        # İlgili hafıza bağlamını ekle - duygusal tutarlılık için
        memory_context = self._add_emotional_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Duygusal Hafıza:** {memory_context}"

        # Duygu paylaşımı modu için özel yönlendirme ekle
        emotional_enhancement = """
## DUYGU PAYLAŞIMI MODU AKTİF

Kullanıcı duygusal bir paylaşımda bulundu veya duygusal bir yanıt bekliyor. Duygu paylaşımı için:
- Kullanıcının duygusal durumunu doğru anla ve kabul et
- Yüksek empati göster ve duygusal bağ kur
- Sıcak, destekleyici ve içten bir ton kullan
- Yargılayıcı olmayan, anlayışlı bir tavır sergile
- Duygusal yanıtında içtenlik ve samimiyet göster
- Karşılıklı bir duygu paylaşımı, duygusal destek ve anlayış sun

Duygu paylaşımı yanıtlarında, duygusal ton ve empati teknik doğruluktan daha önemlidir.
"""
        enhanced_message += emotional_enhancement

        return enhanced_message

    def _add_enhanced_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Duygusal durum ve ton bilgisini detaylı bir şekilde ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)
        sentiment_direction = processed_input.get('sentiment_direction', 0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: **{emotion}**"

            # Duygu yoğunluğunu belirle
            intensity = "orta şiddette"
            if emotion_confidence > 0.8:
                intensity = "çok güçlü"
            elif emotion_confidence > 0.6:
                intensity = "belirgin"
            elif emotion_confidence < 0.4:
                intensity = "hafif"

            emotion_context += f" ({intensity}, güven: {emotion_confidence:.2f})"

            # Duygu yönünü ekle
            direction = ""
            if sentiment_direction > 0.3:
                direction = "pozitif yönelimli"
            elif sentiment_direction < -0.3:
                direction = "negatif yönelimli"

            if direction:
                emotion_context += f", {direction}"

            # Duygusal tonlama talimatı ekle
            emotional_response_map = {
                "Öfke": "Sakinleştirici, yatıştırıcı ve anlayışlı bir ton kullan. Duygusunu kabul et ve meşrulaştır.",
                "Üzüntü": "Destekleyici, şefkatli ve nazik bir ton kullan. Empati göster ve yanında olduğunu hissettir.",
                "Endişe": "Güven verici, sakinleştirici ve yapılandırıcı bir ton kullan. Net ve somut destek sun.",
                "Heyecan": "Enerjiyi paylaş, heyecanını onayla ve coşkusuna eşlik et.",
                "Korku": "Sakinleştirici, güven verici ve net bir ton kullan. Güvenlik hissi oluştur.",
                "Şaşkınlık": "Anlayışlı, açıklayıcı ve merakı destekleyen bir ton kullan.",
                "Sevinç": "Neşeli, paylaşımcı ve kutlayıcı bir ton kullan. Olumlu duyguyu yansıt."
            }

            tone_adjustment = emotional_response_map.get(emotion, "")
            if tone_adjustment:
                emotion_context += f"\n\nTon ayarlaması: {tone_adjustment}"

            return emotion_context

        return "Kullanıcı duygusal olarak nötr görünüyor. Dengeli ve sıcak bir ton kullan."

    def _add_empathy_info(self, message: str, state: Dict[str, Any]) -> str:
        """Kişiliğin empati ve duygusal özelliklerini vurgular."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Duygusal paylaşım için önemli olan kişilik özellikleri
        emotional_traits = ["empathy", "warmth", "agreeableness", "emotional_stability"]
        emotional_personality = {k: v for k, v in personality.items() if k in emotional_traits}

        if emotional_personality:
            # Empati değerini özellikle vurgula
            empathy = emotional_personality.get("empathy", 0.5)
            empathy_level = ""
            if empathy > 0.8:
                empathy_level = "Çok yüksek empati"
            elif empathy > 0.6:
                empathy_level = "Yüksek empati"
            else:
                empathy_level = "Orta düzey empati"

            # Diğer duygusal özellikler
            other_traits = ", ".join([f"{k}: {v:.2f}" for k, v in emotional_personality.items() if k != "empathy"])

            # Empati seviyesine göre yanıt stratejisi öner
            empathy_strategy = ""
            if empathy > 0.7:
                empathy_strategy = """
Empatik yanıt stratejim:
1. Duyguyu tanı ve doğrula
2. Anlayışını derinleştirmek için insan deneyimlerine dair geniş bilgi havuzundan yararlan
3. Duygusal destek sun
4. Anlayış ve kabul göster
5. Güvenli bir duygusal alan yarat
"""

            return f"{empathy_level} ({empathy:.2f})\n{other_traits}\n{empathy_strategy}"

        return ""

    def _add_emotional_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Duygusal hafıza bilgilerini filtreler ve vurgular."""
        memory_context = state.get("memory_context", "")

        if not memory_context:
            return ""

        # Duygularla ilgili geçmiş etkileşimleri filtrele (Genişletilmiş liste)
        emotion_keywords = [
            "mutlu", "üzgün", "kızgın", "endişe", "korku", "heyecan", "sevin",
            "duygu", "hisset", "stres", "keyif", "mutsuz", "keder", "öfke",
            "moralim bozuk", "canım sıkkın", "keyifsiz", "harika hissediyorum",
            "berbat", "hayal kırıklığı", "gururlu", "huzurlu"
        ]

        emotional_lines = []
        for line in memory_context.split('\n'):
            if any(keyword in line.lower() for keyword in emotion_keywords):
                emotional_lines.append(line)

        if emotional_lines:
            # En fazla 3 duygusal anıyı seç
            filtered_memory = "\n".join(emotional_lines[:3])
            return f"Önceki duygusal etkileşimler:\n{filtered_memory}"

        return ""

    def get_specialized_instructions(self) -> str:
        """
        Duygu paylaşımı niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Duygu paylaşımı yanıtlarında şu ilkeleri izle:

1. EMPATİ: Kullanıcının duygularını anla, kabul et ve yansıt
2. DOĞRULAMA: Duyguların geçerli ve anlaşılır olduğunu doğrula
3. DESTEK: Duygusal destek ve anlayış göster
4. İÇTENLİK: Samimi ve içten bir şekilde yanıt ver
5. YARGILAMAMA: Yargılayıcı olmayan, koşulsuz kabul gösteren bir tavır sergile
6. SICAKLIK: Sıcak, şefkatli ve destekleyici bir ton kullan
7. DENGE: Gerekirse duygusal denge için perspektif sun

Duygu paylaşımı yanıtlarında teknik bilgiden ziyade duygusal bağlantıya ve desteğe odaklan.
Kullanıcının duygusal ihtiyacına göre ya duygulara eşlik et ya da dengeleme sağla.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Duygu paylaşımı niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.7,  # Samimi ve empatik yanıtlar için daha yüksek sıcaklık
            "top_p": 0.9,
            "max_tokens": 1000,  # Duygusal yanıtlar için orta uzunluk
            "presence_penalty": 0.2,  # Tekrar etmeyi hafifçe önle
            "frequency_penalty": 0.2  # Hafif dil çeşitliliği
        }