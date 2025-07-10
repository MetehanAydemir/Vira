"""
Emir/komut niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class CommandIntentHandler(BaseIntentHandler):
    """
    Emir/komut niyeti için özelleştirilmiş intent handler.
    Kullanıcının açık bir talimat verdiği durumlarda kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Komut için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel zenginleştirmeyi uygula
        enhanced_message = system_message

        # Rafine bağlamı ekle - komutun doğru anlaşılması için kritik
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Komut Bağlamı:** {refined_context}"

        # Hafıza bağlamını ekle - önceki benzer komutlar için yararlı
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**İlgili Hafıza:** {memory_context}"

        # Kullanıcının duygusal durumunu ekle - yanıt tonunu ayarlamak için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Komut modu için özel yönlendirme ekle
        command_enhancement = """
## KOMUT MODU AKTİF

Kullanıcı bir komut/talimat verdi. Komutu doğru anlamak ve uygulamak için:
- Verilen komutu net bir şekilde anla
- Komutu yerine getirmek için gerekli adımları belirle
- Komutun uygulanabilir olup olmadığını değerlendir
- Komutun başarıyla uygulandığını veya neden uygulanamadığını açıkça bildir
- Kısa, net ve doğrudan bir yanıt ver
"""
        enhanced_message += command_enhancement

        return enhanced_message

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler - komut için çok önemli."""
        refined_context = state.get("refined_context", "")

        # Komutla ilgili özel bağlam bilgilerini çıkar
        command_keywords = ["yap", "değiştir", "oluştur", "sil", "güncelle", "hesapla", "çalıştır",
                           "başlat", "durdur", "ara", "göster", "listele", "analiz et"]

        # Komutla ilgili anahtar kelimeleri vurgula
        if refined_context:
            for keyword in command_keywords:
                if keyword in refined_context.lower():
                    refined_context = refined_context.replace(keyword, f"**{keyword}**")

        return refined_context

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını ekler - önceki benzer komutları anlamak için."""
        memory_context = state.get("memory_context", "")

        # Komut geçmişi ile ilgili bilgileri filtrele
        if memory_context:
            # Sadece basit bir filtreleme yapalım, gerçek uygulamada daha karmaşık olabilir
            command_related_lines = []
            for line in memory_context.split('\n'):
                if any(cmd in line.lower() for cmd in ["komut", "talimat", "istedi", "yapmanı", "oluştur"]):
                    command_related_lines.append(line)

            # En fazla 3 ilgili satırı al
            if command_related_lines:
                filtered_memory = "\n".join(command_related_lines[:3])
                return f"Önceki benzer komutlar:\n{filtered_memory}"

        return ""

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ekler - komutun uygulanma tonunu ayarlamak için."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            # Yüksek güvenilirlikte komuta özel ton ayarlaması ekle
            if emotion_confidence > 0.7:
                command_emotion_map = {
                    "Öfke": "Komutu sakin bir şekilde uygula ve profesyonel bir ton benimse.",
                    "Üzüntü": "Komutu anlayışla karşıla ve nazik bir ton kullan.",
                    "Endişe": "Komutu net bir şekilde anladığını belirt ve güven verici bir şekilde uygula.",
                    "Heyecan": "Komutun uygulanmasında enerjiyi yansıt ve olumlu bir ton kullan.",
                    "Korku": "Komutun güvenli bir şekilde uygulandığını vurgula ve güvence ver.",
                    "Şaşkınlık": "Komutu nasıl yorumladığını ve uyguladığını açıkça anlat.",
                    "Sevinç": "Komuta pozitif bir yaklaşımla cevap ver."
                }

                tone_adjustment = command_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def get_specialized_instructions(self) -> str:
        """
        Komut niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Komutlara şu şekilde yanıt ver:

1. ONAYLAMA: Komutu anladığını belirt
2. UYGULAMA: Komutu net bir şekilde uygula veya simüle et
3. BİLDİRİM: Uygulamanın sonucunu veya durumunu bildir
4. AÇIKLAMA: Gerektiğinde ek bilgi veya açıklama ekle

Komut yanıtları kısa, öz ve yönlendirici olmalıdır. Uzun açıklamalardan ve gereksiz detaylardan kaçın.
Komutu yerine getirirken açık bir dil kullan ve kullanıcının ne yapılmasını istediğinden emin olmadığında
net bir şekilde sor.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Komut niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.4,  # Daha net ve doğrudan yanıtlar için orta-düşük sıcaklık
            "top_p": 0.85,
            "max_tokens": 500,   # Komut yanıtları genellikle kısa olur
            "presence_penalty": 0.0  # Komutlarda tekrarlama riski düşük
        }