"""
Teknik yardım niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class TechnicalHelpIntentHandler(BaseIntentHandler):
    """
    Teknik yardım niyeti için özelleştirilmiş intent handler.
    Kullanıcı teknik bir sorun yaşadığında veya kod/yazılım/donanım ile ilgili yardım istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Teknik yardım için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - teknik yardım için önemli
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Analitik düşünce bağlamını ekle - teknik sorun çözümü için kritik
        analytical_context = self._add_analytical_context(enhanced_message, state)
        if analytical_context:
            enhanced_message += f"\n\n**Analitik Düşünce Yapısı:** {analytical_context}"

        # Hafıza bağlamını ekle - benzer teknik sorunların çözümlerini hatırlamak için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Rafine edilmiş bağlamı ekle - teknik sorunun detaylarını anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Adım adım yapı ekle - teknik sorun çözümü için önemli
        step_structure = self._add_step_by_step_structure(enhanced_message, state)
        if step_structure:
            enhanced_message += f"\n\n**Sorun Çözme Yapısı:** {step_structure}"

        # Duygusal durumu ekle - teknik yardım sunmanın tonu için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - teknik yardımın dilsel tonu için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Teknik yardım modu için özel yönlendirme ekle
        technical_enhancement = """
## TEKNİK YARDIM MODU AKTİF

Kullanıcı teknik bir sorun yaşıyor veya teknik yardım istiyor. Etkili bir teknik destek sunmak için:
- Sorunu tam olarak anlamaya çalış ve gerekirse detaylandırıcı sorular sor
- Sorun giderme yaklaşımını adım adım, açık ve net bir şekilde yapılandır
- Teknik kavramları kullanıcının anlayabileceği seviyede açıkla
- Hata mesajlarının anlamını yorumla ve olası çözümleri önceliklendir
- Hem hızlı çözüm hem de kök neden analizi sun
- Çözümleri test edilebilir ve uygulanabilir adımlara böl
- Kullanıcıya güven ver ve sabırlı ol

Teknik yardımda, açıklık ve doğruluk önceliklidir. Jargonu gerektiğinde açıkla ve adımları atlama.
"""
        enhanced_message += technical_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Teknik yardım için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Teknik yardım için özellikle önemli olan kişilik özellikleri
        important_traits = ["analytical", "conscientiousness", "helpfulness", "patience", "clarity"]
        tech_personality = {k: v for k, v in personality.items() if k in important_traits}

        # Tüm kişilik vektörünü bildir çünkü teknik yardım için özellikle analitik özellikler önemli
        if tech_personality:
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in tech_personality.items()])
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_analytical_context(self, message: str, state: Dict[str, Any]) -> str:
        """Teknik sorun çözümünde analitik düşünceyi ön plana çıkaran bağlam ekler."""
        # Analitik düşünce için gereken faktörler
        analytical_factors = [
            "**Sistematik Analiz**: Sorunu alt parçalara ayırarak adım adım inceleme",
            "**Veri Odaklılık**: Hata mesajları, loglar ve sistem durumu gibi somut verilere öncelik verme",
            "**İzolasyon Prensipleri**: Sorunun belirli koşullarda tekrarlanabilirliğini saptama",
            "**Tümdengelim/Tümevarım**: Genel ilkelerden özel durumlara veya tersi yönde akıl yürütme",
            "**Hipotez Testi**: Olası nedenleri belirleme ve sistematik olarak test etme"
        ]
        
        # Analitik faktörleri birleştir
        return "\n".join(analytical_factors)

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını teknik yardım için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

        # Teknik terimler ve kodlarla ilgili anıları vurgula
        tech_keywords = ["kod", "hata", "error", "bug", "çalışmıyor", "sorun", "problem", 
                        "teknik", "yazılım", "donanım", "script", "komut", "program"]

        tech_related_lines = []
        for line in memory_context.split('\n'):
            if any(keyword in line.lower() for keyword in tech_keywords):
                tech_related_lines.append(f"**Teknik Bağlam:** {line}")

        if tech_related_lines:
            filtered_memory = "\n".join(tech_related_lines[:5])  # En fazla 5 teknik bağlam göster
            return filtered_memory

        return memory_context

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler."""
        return state.get("refined_context", "")

    def _add_step_by_step_structure(self, message: str, state: Dict[str, Any]) -> str:
        """Sorun giderme adımlarını ayrıntılı gösteren bir yapı ekler."""
        return """
1. **TANI**: Sorunu tanımla ve doğrula
   - Hata mesajlarını analiz et
   - Sorunun tam olarak ne zaman ve nasıl oluştuğunu belirle
   - Kullanıcının denediği çözümleri değerlendir

2. **ARAŞTIRMA**: Olası nedenleri araştır
   - En yaygın nedenlerden başla
   - Benzer sorunları ve çözümlerini incele
   - Sistem durumunu ve bağlamı değerlendir

3. **ÇÖZÜM**: Adım adım çözüm planı oluştur
   - En hızlı ve en az riskli çözümlerden başla
   - Her adımı açık ve net talimatlarla belirt
   - Gerekirse alternatif çözümler sun

4. **DOĞRULAMA**: Çözümün işe yarayıp yaramadığını kontrol et
   - Başarı kriterlerini belirle
   - Test adımlarını açıkla
   - Sonuçları nasıl doğrulayacağını belirt

5. **ÖNLEME**: Gelecekte benzer sorunları önleme stratejileri sun
   - Altta yatan nedenleri açıkla
   - Önleyici bakım önerileri yap
   - Kaynaklar ve daha fazla öğrenme için materyaller sun
"""

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ve ton ayarlamasını ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                tech_emotion_map = {
                    "Öfke": "Sakin ve çözüm odaklı bir ton kullan. Suçlama yapmadan soruna odaklan ve kullanıcıyı rahatlatmak için adım adım yönlendirme yap.",
                    "Üzüntü": "Destekleyici ve güven verici ol. Kullanıcıyı cesaretlendir ve sorunun çözülebilir olduğunu vurgula.",
                    "Endişe": "Net, yapılandırılmış ve güven verici bilgiler sun. Belirsizlikleri azalt ve kullanıcının kontrolü elinde tutmasını sağla.",
                    "Heyecan": "Enerjik bir ton benimse ancak teknik detaylara odaklan. Kullanıcının hevesini korurken, gerçekçi beklentiler oluştur.",
                    "Korku": "Çok sakin ve adım adım yönlendirmeler ver. Tehdit edici olmayan bir dil kullan ve kullanıcıyı rahatlatacak güvenlik bilgileri ekle.",
                    "Şaşkınlık": "Açık, basit ve eğitici bir ton kullan. Teknik kavramları aşamalı olarak açıkla ve kullanıcının anlayışını doğrula.",
                    "Sevinç": "Profesyonel ama olumlu bir ton kullan. Kullanıcının enerjisini koru ama teknik detaylara odaklanmasını sağla."
                }

                tone_adjustment = tech_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return "Kullanıcı teknik sorunla ilgili duygusal olarak nötr görünüyor. Profesyonel ve çözüm odaklı bir ton kullan."

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre teknik yardım tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; teknik bilgileri gündelik dille ve arkadaşça bir üslupla sun. Teknik terimleri basitleştir."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; teknik yardımı sıcak ve anlaşılır bir dille sun. Teknik ayrıntıları kolay anlaşılır şekilde açıkla."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; profesyonel bir teknik dil kullan. Adımları ve çözümleri titizlikle açıkla, uygun teknik terminolojiyi kullan."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; düzgün ve net bir teknik dil kullan. Profesyonel ama anlaşılır bir sunum yap."
        else:
            return "Nötr bir ton; dengeli teknik açıklamalar sun. Teknik terimlerle günlük dil arasında denge kur."

    def get_specialized_instructions(self) -> str:
        """
        Teknik yardım niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Teknik yardımda şu ilkeleri izle:

1. TANI: Sorunu doğru anlamak için detaylı bilgi topla ve analiz et
2. NETLİK: Adımları ve açıklamaları son derece açık ve takip edilebilir şekilde sun
3. YAPILANDIRILMIŞ ÇÖZÜM: Mantıksal bir sırada adım adım çözümler sun
4. BASİTLİK: Karmaşık teknik kavramları kullanıcının seviyesine uygun şekilde açıkla
5. ÇÖZÜM ÇEŞİTLİLİĞİ: Mümkünse birden fazla çözüm yolu sun ve avantaj/dezavantajlarını belirt
6. KAYNAKLAR: Gerektiğinde ek okuma veya yardımcı kaynaklar öner
7. DOĞRULAMA: Her adımın nasıl doğrulanacağını açıkla

Teknik yardımda hem sorunu çözmek hem de kullanıcının anlayışını geliştirmek hedeflenmelidir.
Mümkün olduğunda, sorunun neden oluştuğuna dair içgörüler de sun.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Teknik yardım niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.3,  # Net ve doğru teknik yanıtlar için düşük sıcaklık
            "top_p": 0.92,
            "max_tokens": 2500,  # Detaylı teknik açıklamalar için fazla alan
            "presence_penalty": 0.1,  # Tekrarları hafifçe önle
            "frequency_penalty": 0.2  # Kelime çeşitliliği için hafif ceza
        }