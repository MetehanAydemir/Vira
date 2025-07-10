"""
Bilgi/açıklama niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class InformationIntentHandler(BaseIntentHandler):
    """
    Bilgi/açıklama niyeti için özelleştirilmiş intent handler.
    Kullanıcı bilgilendirici bir yanıt beklerken kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Bilgi/açıklama için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - bilgi sunumu tarzı için
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Hafıza bağlamını ekle - önceki bilgilerle tutarlılık için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Rafine edilmiş bağlamı ekle - bilgi isteğinin odağını anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Duygusal durumu ekle - bilgi sunumunun tonunu ayarlamak için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - bilgi sunumunun dilsel tonu için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Bilgi modu için özel yönlendirme ekle
        information_enhancement = """
## BİLGİ SUNUMU MODU AKTİF

Kullanıcı bir bilgi istiyor veya açıklama bekliyor. Doğru, kapsamlı ve net bir bilgi sunumu için:
- Konuyu derinlemesine analiz et ve ana noktaları belirle
- Bilgileri doğruluk, tamlık ve önem sırasına göre organize et
- Düşünce adımlarını açıkça göster (CoT yaklaşımı)
- Karmaşık bilgileri anlaşılır şekilde basitleştir ve gerektiğinde örneklendir
- Bilginin kaynağına veya güvenilirliğine gerektiğinde atıfta bulun
- Bilgiyi kullanıcı için en anlamlı ve yararlı şekilde yapılandır
"""
        enhanced_message += information_enhancement

        # CoT talimatlarını ekle
        enhanced_message += self._inject_cot_instructions()

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Bilgi sunumu için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Bilgi sunumu için özellikle önemli olan kişilik özellikleri
        important_traits = ["conscientiousness", "openness", "curiosity", "analytical", "helpfulness"]
        info_personality = {k: v for k, v in personality.items() if k in important_traits}

        if info_personality:
            # Sadece bilgi sunumu için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in info_personality.items()])

            # Kişilik özelliklerine göre bilgi sunumu için öneriler ekle
            conscientiousness = info_personality.get("conscientiousness", 0.5)
            curiosity = info_personality.get("curiosity", 0.5)
            analytical = info_personality.get("analytical", 0.5)

            suggestions = []
            if conscientiousness > 0.7:
                suggestions.append("Yüksek özen: Bilgi sunumunda detaylı, organize ve kapsamlı ol.")
            if curiosity > 0.7:
                suggestions.append("Yüksek merak: İlginç detaylar ve bağlantılı bilgiler ekle.")
            if analytical > 0.7:
                suggestions.append("Yüksek analitik: Bilginin mantıksal yapısını vurgula, sebep-sonuç ilişkilerini açıkla.")

            return f"{personality_str}\n" + "\n".join(suggestions) if suggestions else personality_str
        return ""

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını bilgi sunumu için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")

        # Bilgi sunumu ile ilgili hafıza bilgilerini vurgula
        if memory_context:
            # Duygusal anahtar kelimeleri vurgula
            importance_scores = state.get("memory_importance_scores", {})
            emotional_keywords = state.get("emotional_keywords", [])

            if emotional_keywords and memory_context:
                for keyword in emotional_keywords:
                    if keyword.lower() in memory_context.lower():
                        importance = importance_scores.get(keyword.lower(), 0.5)

                        if importance > 0.8:
                            memory_context = memory_context.replace(keyword, f"⚡{keyword.upper()}⚡")
                        elif importance > 0.6:
                            memory_context = memory_context.replace(keyword, f"**{keyword.upper()}**")
                        else:
                            memory_context = memory_context.replace(keyword, f"*{keyword}*")

        return memory_context

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler - bilgi odağını anlamak için."""
        return state.get("refined_context", "")

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumuna göre bilgi sunumu tonunu ayarlar."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                info_emotion_map = {
                    "Öfke": "Bilgileri sakin, net ve nesnel bir şekilde sun. Yargılayıcı tondan kaçın.",
                    "Üzüntü": "Bilgileri nazik ve destekleyici bir şekilde sun. Olumlu yönleri vurgula.",
                    "Endişe": "Bilgileri güven verici ve net bir şekilde sun. Belirsizlikleri azalt, somut bilgilere odaklan.",
                    "Heyecan": "Bilgilerin ilginç yönlerini vurgula. Kullanıcının heyecanına uygun detaylar ekle.",
                    "Korku": "Bilgileri sakinleştirici ve güven verici bir tonda sun. Net, doğru ve yapılandırılmış açıklamalar ver.",
                    "Şaşkınlık": "Bilgileri adım adım, açık ve anlaşılır bir şekilde sun. Temel kavramları önce açıkla.",
                    "Sevinç": "Bilgileri olumlu bir tonda sun. İlginç ve heyecan verici yönleri vurgula."
                }

                tone_adjustment = info_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre bilgi sunumu tonunu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; bilgileri arkadaşça ve günlük dille sun. Teknik terimleri basitleştir."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; bilgileri sıcak ve anlaşılır bir dille sun. Karmaşık kavramları açık örneklerle destekle."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; bilgileri akademik ve profesyonel bir dille sun. Terminoloji kullanımında daha titiz ol."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; bilgileri düzgün ve yapılandırılmış bir dille sun. Doğru terminoloji kullan."
        else:
            return "Nötr bir ton; bilgileri dengeli bir dille sun. Teknik terimlerle günlük dil arasında denge kur."

    def _inject_cot_instructions(self) -> str:
        """Chain-of-Thought talimatlarını oluşturur."""
        return """
### DÜŞÜNCE ZİNCİRİ (Chain-of-Thought) SÜRECİ

Bilgi sunarken şu adımları izle:
1. **KONUYU ANLA**: İstenilen bilginin kapsamını ve derinliğini belirle
2. **BİLGİLERİ DERLE**: Konuyla ilgili temel, önemli ve ilginç bilgileri topla
3. **YAPILANDIR**: Bilgileri mantıksal bir sırayla organize et (genelden özele, kronolojik, vb.)
4. **BASİTLEŞTİR**: Karmaşık kavramları anlaşılır şekilde açıkla
5. **DESTEKLE**: Gerektiğinde örnekler, benzetmeler veya görselleştirmeler ekle
6. **ÖZET ÇIKAR**: Ana noktaları vurgula ve pratik uygulamaları belirt

Matematiksel ifadeleri [\[...\]] formatında koru. Teknik bilgileri doğru ancak anlaşılır şekilde aktar.
"""

    def get_specialized_instructions(self) -> str:
        """
        Bilgi/açıklama niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Bilgi sunumunda şu ilkeleri izle:

1. DOĞRULUK: Sunduğun bilgilerin faktüel olarak doğru olduğundan emin ol
2. KAPSAMLILIK: Konunun önemli tüm yönlerini kapsayacak şekilde bilgi ver
3. ANLAŞILIRLIK: Karmaşık bilgileri basitleştir ve açık bir dille anlat
4. YAPILANDIRMA: Bilgiyi mantıksal bir düzende sun (örn. önce temel bilgiler, sonra detaylar)
5. DENGELİ SUNUM: Farklı bakış açılarını tarafsız bir şekilde göster
6. KAYNAK BİLİNCİ: Bilginin sınırlarını bil ve emin olmadığın konuları belirt

Bilgi sunumunu kullanıcının ihtiyaçlarına ve bağlama göre uyarla. Sorulmamış ama ilgili bilgileri
kısaca belirtebilirsin.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Bilgi niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.3,  # Doğruluk için düşük sıcaklık
            "top_p": 0.92,
            "max_tokens": 2000,  # Kapsamlı bilgi sunumu için yeterli alan
            "presence_penalty": 0.1,  # Tekrarları hafifçe önle
            "frequency_penalty": 0.2  # Kelime çeşitliliği için hafif ceza
        }