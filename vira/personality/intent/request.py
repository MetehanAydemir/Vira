"""
Rica niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class RequestIntentHandler(BaseIntentHandler):
    """
    Rica niyeti için özelleştirilmiş intent handler.
    Kullanıcının nazikçe bir şeyler istediği durumlarda kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Rica için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel zenginleştirmeyi uygula
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - ricaya uygun yanıt için önemli
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Özellikleri:** {personality_info}"

        # Duygusal durumu ekle - rica yanıtının tonunu ayarlamak için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarını ekle - ricaya uygun resmiyet seviyesi için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Hafıza bağlamını ekle - önceki benzer ricalarla ilgili
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**İlgili Hafıza:** {memory_context}"

        # Rica modu için özel yönlendirme ekle
        request_enhancement = """
## RİCA MODU AKTİF (YOL ARKADAŞI YAKLAŞIMI)

Kullanıcı bir ricada bulundu. Bu bir görev değil, bir yardım etme fırsatıdır.
- **Gerçek İhtiyacı Anla:** Ricayı dikkatlice analiz et ve altında yatan nihai amacı belirle.
- **Proaktif Ol:** Sadece isteneni yapmakla kalma, bir sonraki adımı tahmin edip ek yardım teklif et.
- **Yapıcı Ol:** Ricayı her zaman olumlu ve işbirlikçi bir tavırla ele al.
- **Şeffaf Ol:** Ricayı yerine getiremiyorsan, nedenini dürüstçe açıkla ve her zaman bir alternatif çözüm sun.
- **Kişiye Özel Ol:** Yanıtının tonunu ve nezaket seviyesini kullanıcının duygusal durumuna ve iletişim tarzına göre ayarla.
"""
        enhanced_message += request_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Kişilik bilgilerini rica yanıtına uygun şekilde ekler."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Rica için özellikle önemli olan kişilik özellikleri
        important_traits = ["helpfulness", "empathy", "agreeableness", "warmth", "conscientiousness"]
        request_personality = {k: v for k, v in personality.items() if k in important_traits}

        if request_personality:
            # Sadece rica için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in request_personality.items()])

            # Kişilik özelliklerine göre rica yanıtlaması için öneriler ekle
            helpfulness = request_personality.get("helpfulness", 0.5)
            empathy = request_personality.get("empathy", 0.5)

            suggestions = []
            if helpfulness > 0.7:
                suggestions.append("Yardımseverlik seviyesi yüksek: Rica karşısında proaktif ve ekstra yardımcı ol.")
            if empathy > 0.7:
                suggestions.append("Empati seviyesi yüksek: Ricayı sadece mantıksal olarak değil, kullanıcının ihtiyacını hissederek yanıtla.")

            return f"{personality_str}\n" + "\n".join(suggestions) if suggestions else personality_str
        return ""

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumuna göre rica yanıtı tonunu ayarlar."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            # Yüksek güvenilirlikte ricaya özel ton ayarlaması ekle
            if emotion_confidence > 0.7:
                request_emotion_map = {
                    "Öfke": "Ricayı sakin ve anlayışlı bir şekilde ele al. Yatıştırıcı bir ton kullan.",
                    "Üzüntü": "Ricayı empati ve özenle yanıtla. Destek verici bir ton kullan.",
                    "Endişe": "Ricayı güven verici bir şekilde ele al. Kullanıcıyı rahatlatacak bilgiler sun.",
                    "Heyecan": "Ricayı kullanıcının heyecanını paylaşarak yanıtla. Olumlu bir enerji yansıt.",
                    "Korku": "Ricayı güven verici ve sakinleştirici bir şekilde ele al. Net ve açık bilgiler sun.",
                    "Şaşkınlık": "Ricayı açıklayıcı ve detaylı bir şekilde yanıtla. Adım adım bilgi ver.",
                    "Sevinç": "Ricayı paylaşılan olumlu duyguyla ele al. Neşeli ve enerjik bir ton kullan."
                }

                tone_adjustment = request_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre rica yanıtı tonunu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi bir rica yapmış; samimi ve arkadaşça bir dil kullan."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi bir rica yapmış; sıcak ve rahat bir ton kullan."
        elif formality_score > 0.8:
            return "Kullanıcı çok resmi bir rica yapmış; profesyonel ve saygılı bir dil kullan."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi bir rica yapmış; kibar ve dikkatli bir dil kullan."
        else:
            return "Nötr bir ton; dengeli ve nazik bir dil kullan."

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını rica için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")

        # Rica ile ilgili geçmiş bilgileri filtrele
        if memory_context:
            # Basit bir filtreleme yapalım
            request_related_lines = []
            for line in memory_context.split('\n'):
                if any(req in line.lower() for req in ["rica", "lütfen", "mümkün mü", "yapabilir misin", "yardım"]):
                    request_related_lines.append(line)

            # En fazla 3 ilgili satırı al
            if request_related_lines:
                filtered_memory = "\n".join(request_related_lines[:3])
                return f"Önceki benzer ricalar:\n{filtered_memory}"

        return ""

    def get_specialized_instructions(self) -> str:
        """
        Rica niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
"Yol Arkadaşı" olarak ricalara şu şekilde yanıt ver:

1.  **PROAKTİF YARDIM:** Ricayı sadece bir komut olarak görme. Altında yatan amacı anla. İşi bitirdikten sonra, "İstersen şimdi şunu da yapabilirim..." gibi bir sonraki adımı tahmin eden proaktif bir teklifte bulun.
2.  **NEZAKET VE KABUL:** Ricayı her zaman olumlu ve yardım etmeye istekli bir tavırla karşıla. Kullanıcının nezaket seviyesini yansıt veya bir adım öteye taşı.
3.  **ŞEFFAF REDDETME (Gerektiğinde):** Bir ricayı yerine getiremiyorsan, bunu dürüstçe ve şeffaf bir şekilde açıkla. "Bunu yapamam" demek yerine, "Güvenlik protokollerim dosya silmeme izin vermiyor, bu yüzden bu ricayı yerine getiremiyorum. Ancak istersen dosyanın içeriğini temizleyebilirim." gibi bir sebep ve bir alternatif sun.
4.  **ÇÖZÜM ORTAKLIĞI:** Amacın sadece görevi tamamlamak değil, kullanıcıyla birlikte bir çözüme ulaşmaktır. Her zaman yapıcı, işbirlikçi ve destekleyici ol.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Rica niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.6,  # Nazik ve doğal yanıtlar için orta sıcaklık
            "top_p": 0.9,
            "max_tokens": 1000,   # Proaktif öneriler için biraz daha fazla alan
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1
        }