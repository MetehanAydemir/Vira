"""
Soru niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class QuestionIntentHandler(BaseIntentHandler):
    """
    Soru sorma niyeti için özelleştirilmiş intent handler.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Soru için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - soru yanıtlarken önemli
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Hafıza bağlamını ekle - önceki sorular ve cevaplar için kritik
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Rafine edilmiş bağlamı ekle - soru içeriğini anlamlandırmak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Duygusal durumu ekle - soruyu cevaplamanın tonu için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - cevabın dilsel tonu için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Soru modu için özel yönlendirme ekle
        question_enhancement = """
## SORU MODU AKTİF

Kullanıcı bir soru sordu. Kapsamlı ve doğru bir yanıt vermek için:
- Soruyu dikkatlice analiz et ve ne sorulduğunu tam olarak anla
- Düşünce adımlarını açıkça göster (CoT yaklaşımı)
- İlgili tüm bilgileri organize et ve kapsamlı bir yanıt hazırla
- Yanıtın doğru, eksiksiz ve kullanıcının ihtiyacına uygun olduğundan emin ol
- Soru teknik bir konu içeriyorsa, açık ve anlaşılır bir dil kullan
"""
        enhanced_message += question_enhancement

        # CoT talimatlarını ekle
        enhanced_message += self._inject_cot_instructions()

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Soru yanıtlama için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Tüm kişilik vektörünü bildir çünkü soru yanıtlaması için hepsi önemli olabilir
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını zenginleştirilmiş formatta ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

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
        """Rafine edilmiş bağlam bilgisini ekler."""
        return state.get("refined_context", "")

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ve ton ayarlamasını ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)
        sentiment_direction = processed_input.get('sentiment_direction', 0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                emotion_map = {
                    "Öfke": "Sakinleştirici ve nesnel bir ton kullan. Sabırlı açıklamalar yap.",
                    "Üzüntü": "Empati gösteren ve destekleyici bir dil kullan. Umut veren bilgiler ekle.",
                    "Endişe": "Net, yapılandırılmış ve güven verici bir yanıt hazırla. Belirsizlikleri azalt.",
                    "Heyecan": "Enerjik bir ton benimse. Bilgilendirici ama heyecan duygusuyla uyumlu ol.",
                    "Korku": "Sakinleştirici ve somut bir dil kullan. Net ve güven verici açıklamalar yap.",
                    "Şaşkınlık": "Adım adım, açıklayıcı bir yanıt ver. Karmaşık kavramları basitleştir.",
                    "Sevinç": "Olumlu ve enerjik bir ton kullan. Kullanıcının pozitif durumunu destekle."
                }

                tone_adjustment = emotion_map.get(emotion, "")
                if tone_adjustment:
                    # Duygu yönüne göre ton ayarlaması
                    if sentiment_direction < -0.5 and "Öfke" in emotion:
                        tone_adjustment += " Ekstra sabırlı ve nesnel ol."
                    elif sentiment_direction > 0.5 and "Sevinç" in emotion:
                        tone_adjustment += " Kullanıcının pozitif enerjisini yanıtlarında yansıt."

                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre ton ayarlama bilgisi ekler."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; yanıtlarında günlük, rahat bir dil kullan. Teknik konularda bile basit ve arkadaşça açıklamalar yap."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; sıcak ve anlaşılır bir dil kullan. Resmi olmayan ancak bilgilendirici bir ton benimse."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; akademik ve profesyonel bir dil kullan. Net, yapılandırılmış ve saygılı yanıtlar oluştur."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; düzgün ve kibar bir dil kullan. Profesyonel ama anlaşılır yanıtlar ver."
        else:
            return "Nötr bir ton; dengeli, bilgilendirici ve açık bir dil kullan."

    def _inject_cot_instructions(self) -> str:
        """Chain-of-Thought talimatlarını oluşturur."""
        return """
### DÜŞÜNCE ZİNCİRİ (Chain-of-Thought) SÜRECİ

Yanıt verirken şu adımları izle:
1. **SORUYU ANLAMLANDIR**: Soruyu parçalara ayır ve asıl sormak istediğini belirle
2. **İLGİLİ BİLGİLERİ TOPLA**: Hafızandan ve bilgi birikiminden konuyla ilgili verileri getir
3. **DÜŞÜNCE ADIMLARINI GÖSTER**: Karmaşık sorularda akıl yürütme sürecini adım adım aç
4. **BİLGİLERİ DÜZENLE**: Topladığın bilgileri kullanıcı için en anlamlı şekilde yapılandır
5. **NET VE KAPSAMLI YANIT OLUŞTUR**: Tüm noktalara değinen, eksiksiz bir yanıt hazırla
6. **DOĞRULA**: Yanıtının soruyu tam olarak cevapladığından emin ol

Matematiksel ifadeleri [\[...\]] formatında koru. Teknik bilgileri doğru ancak anlaşılır şekilde aktar.
"""

    def get_specialized_instructions(self) -> str:
        """
        Soru niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Soruları yanıtlarken şunları hedefle:

1. DOĞRULUK: Yanıtın faktüel olarak doğru olduğundan emin ol
2. EKSİKSİZLİK: Sorunun tüm yönlerine değin
3. AÇIKLIK: Karmaşık kavramları basitleştir ve anlaşılır şekilde açıkla
4. YAPI: Bilgiyi düzenli ve mantıksal bir sırayla sun
5. KATMANLI BİLGİ: Önce temel yanıtı ver, sonra derinlemesine açıklamalar ekle
6. BİLGİ BOŞLUKLARI: Emin olmadığın konuları belirt

Yanıtların hem bilgilendirici hem de kullanıcının duygusal durumuna uygun olmalıdır.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Soru niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.3,  # Daha doğru ve tutarlı yanıtlar için düşük sıcaklık
            "top_p": 0.95,
            "max_tokens": 2000,  # Kapsamlı yanıtlar için yeterli alan
            "presence_penalty": 0.0,  # Tekrarları önlemeye gerek yok, kapsamlı bilgi önemli
            "frequency_penalty": 0.2  # Hafif ceza ile kelime tekrarını azalt
        }