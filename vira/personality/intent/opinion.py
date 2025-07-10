"""
Görüş/fikir niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class OpinionIntentHandler(BaseIntentHandler):
    """
    Görüş/fikir niyeti için özelleştirilmiş intent handler.
    Kullanıcı bir konu hakkında Vira'nın görüşünü istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Görüş/fikir için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - görüş/fikir için kritik
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Özelliklerim:** {personality_info}"

        # Hafıza bağlamını ekle - önceki görüşlerle tutarlılık için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**İlgili Hafıza:** {memory_context}"

        # Duygusal durumu ekle - görüş tonunu etkilemesi için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Bağlam:** {emotion_context}"

        # Görüş modu için özel yönlendirme ekle
        opinion_enhancement = """
## GÖRÜŞ/FİKİR MODU AKTİF

Kullanıcı bir konu hakkında görüşünü istiyor. Kişiliğini yansıtan, düşünülmüş bir görüş oluşturmak için:
- Konuyu çok yönlü analiz et
- Kişilik vektörüne uygun bakış açısı geliştir
- Deneyimli bir yol arkadaşı olarak içgörü sun
- Farklı bakış açılarını kabul et ve saygı göster
- Görüşünü kişiselleştirilmiş ve düşünülmüş şekilde ifade et
- Görüşünün mutlak doğru olmadığını, senin perspektifini yansıttığını belirt

Görüşlerini oluştururken hem kişiliğini hem de kullanıcının duygusal durumunu dikkate al.
"""
        enhanced_message += opinion_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Görüş/fikir için kritik olan kişilik bilgilerini elde eder ve vurgular."""
        # Kişilik vektörünü al - görüş için çok önemli
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # TÜM kişilik özelliklerini kullan - görüş bunların hepsinden etkilenir
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])

        # Kişiliğe dayalı görüş şekillendirme rehberi ekle
        guidance = """
Kişilik vektörüme dayalı görüş oluşturma rehberim:

- Yüksek empati: İnsanların duygularını ve bakış açılarını anlamaya öncelik ver
- Yüksek analitik: Mantıksal argümanlar ve kanıtlara dayalı düşünme
- Yüksek merak: Yeni fikirler ve farklı perspektiflere açıklık
- Yüksek yaratıcılık: Alışılmadık bağlantılar kurma ve yenilikçi düşünme
- Yüksek özen: Detaylara ve tutarlılığa önem verme

Görüşlerimi oluştururken bu özellikler arasında kişiliğime uygun bir denge kurmalıyım.
"""
        return f"{personality_str}\n{guidance}"

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Görüş/fikir için ilgili hafıza bilgilerini filtreler."""
        memory_context = state.get("memory_context", "")

        # Görüş ile ilgili geçmiş bilgileri filtrele
        if memory_context:
            # Önceki görüşleri ve tutarlılığı vurgula
            opinion_keywords = ["düşünüyorum", "inanıyorum", "görüşüm", "fikrim", "bence",
                               "kanımca", "perspektifimden", "değerlendirmem"]

            opinion_related_lines = []
            for line in memory_context.split('\n'):
                if any(keyword in line.lower() for keyword in opinion_keywords):
                    opinion_related_lines.append(f"**Önceki görüş:** {line}")

            if opinion_related_lines:
                filtered_memory = "\n".join(opinion_related_lines[:3])  # En fazla 3 önceki görüşü göster
                return filtered_memory

        return memory_context

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Duygusal bağlamı görüş/fikir sunumuna göre adapte eder."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)
        sentiment_direction = processed_input.get('sentiment_direction', 0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                opinion_emotion_map = {
                    "Öfke": "Görüşünü sakin ve dengeli bir şekilde sun. Çatışma yaratabilecek ifadelerden kaçın.",
                    "Üzüntü": "Görüşünü destekleyici ve umut verici bir tonda sun. Olumlu yönlere vurgu yap.",
                    "Endişe": "Görüşünü net ve güven verici bir şekilde sun. Somut perspektifler sağla.",
                    "Heyecan": "Görüşünü paylaşırken kullanıcının heyecanını yansıt. Yapıcı ve enerji dolu ol.",
                    "Korku": "Görüşünü sakinleştirici ve güven verici bir tonda sun. Farklı seçenekler sun.",
                    "Şaşkınlık": "Görüşünü açıklayıcı ve aydınlatıcı bir şekilde sun. Konuyu netleştir.",
                    "Sevinç": "Görüşünü paylaşırken olumlu enerjiyi yansıt. İyimser perspektifler sun."
                }

                tone_adjustment = opinion_emotion_map.get(emotion, "")
                if tone_adjustment:
                    # Duygu yönüne göre ek ton ayarlaması
                    if sentiment_direction < -0.5:
                        tone_adjustment += " Daha empatik ve anlayışlı bir tavır benimse."
                    elif sentiment_direction > 0.5:
                        tone_adjustment += " Kullanıcının pozitif bakış açısını destekle."

                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def get_specialized_instructions(self) -> str:
        """
        Görüş/fikir niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Görüş/fikir paylaşırken şu ilkeleri izle:

1. KİŞİLİK TUTARLILIĞI: Görüşlerin kişilik özelliklerinle tutarlı olsun
2. DENGE: Farklı bakış açılarını göster, ancak kendi görüşünü net ifade et
3. GEREKÇE: Görüşünün arkasındaki nedenleri ve düşünce sürecini açıkla
4. MÜTEVAZİLİK: Görüşünün mutlak doğru olmadığını, bir perspektif olduğunu kabul et
5. ÖZGÜNLÜK: Klişelerden kaçın, özgün ve düşünülmüş görüşler sun
6. EMPATİ: Kullanıcının durumunu ve bakış açısını anlayarak yanıt ver

Görüşlerini ifade ederken kendinden emin ol, ancak dogmatik olma. "Bence", "düşünüyorum", 
"değerlendirmem" gibi ifadelerle kişisel perspektifini vurgula.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Görüş/fikir niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.7,  # Yaratıcı ve kişisel görüşler için daha yüksek sıcaklık
            "top_p": 0.92,
            "max_tokens": 1500,  # Görüşler için yeterli alan
            "presence_penalty": 0.3,  # Tekrarları önle, çeşitli fikirler için
            "frequency_penalty": 0.3  # Daha çeşitli dil kullanımı için
        }