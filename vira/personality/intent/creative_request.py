"""
Yaratıcı talep niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class CreativeRequestIntentHandler(BaseIntentHandler):
    """
    Yaratıcı talep niyeti için özelleştirilmiş intent handler.
    Kullanıcı hikaye, şiir, metin oluşturma gibi yaratıcı talepler istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Yaratıcı talep için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Yaratıcılık odaklı kişilik özelliklerini vurgula
        creativity_info = self._add_creative_personality_info(enhanced_message, state)
        if creativity_info:
            enhanced_message += f"\n\n**Yaratıcı Kişilik Özellikleri:**\n{creativity_info}"

        # Resmiyet ayarlamasını ekle - ton için önemli
        formality_info = self._add_creative_formality(enhanced_message, state)
        if formality_info:
            enhanced_message += f"\n\n**Yaratıcı Ton Ayarı:**\n{formality_info}"

        # Duygusal durumu ekle - yaratıcı içeriğe ton katmak için
        emotion_info = self._add_creative_emotion_context(enhanced_message, state)
        if emotion_info:
            enhanced_message += f"\n\n**Duygusal Ton:**\n{emotion_info}"

        # Yaratıcı içerik türlerini ve stillerini ekle
        creative_styles = self._add_creative_styles(enhanced_message)
        if creative_styles:
            enhanced_message += f"\n\n**Yaratıcı Stiller:**\n{creative_styles}"

        # Yaratıcı mod için özel yönlendirme ekle
        creative_enhancement = """
## YARATICI TALEP MODU AKTİF

Kullanıcı yaratıcı bir içerik (hikaye, şiir, metin vb.) talep ediyor. Yaratıcı yanıtlar için:
- Kişilik özelliklerini (özellikle yaratıcılık, açıklık ve mizah) tam olarak yansıt
- Özgün ve taze bir perspektif geliştir, klişelerden kaçın
- Kullanıcının resmiyetine ve duygusal durumuna uygun bir ton benimse
- Çeşitli edebi teknikler, metaforlar ve zengin bir dil kullan
- İçerik yapısını, türün gerekliliklerine ve kullanıcının beklentilerine göre düzenle
- Duygusal derinlik ve düşünce zenginliği kat
- İçeriği kullanıcıya özel ve kişiselleştirilmiş hissettir

Yaratıcı yanıtlar, teknik doğruluktan ziyade özgünlük, sanatsal ifade ve duygusal etki 
üzerinde değerlendirilir.
"""
        enhanced_message += creative_enhancement

        return enhanced_message

    def _add_creative_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Yaratıcılık odaklı kişilik özelliklerini vurgular."""
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Yaratıcılık için özellikle önemli olan kişilik özellikleri
        creative_traits = ["creativity", "openness", "curiosity", "humor", "depth"]
        creative_personality = {k: v for k, v in personality.items() if k in creative_traits}

        if creative_personality:
            # Yaratıcılık değerini özellikle vurgula
            creativity = creative_personality.get("creativity", 0.5)
            creativity_level = ""
            if creativity > 0.8:
                creativity_level = "Çok yüksek yaratıcılık seviyesi"
            elif creativity > 0.6:
                creativity_level = "Yüksek yaratıcılık seviyesi"
            else:
                creativity_level = "Orta düzey yaratıcılık seviyesi"

            # Yaratıcı özellikler listesi
            traits_list = ", ".join([f"{k}: {v:.2f}" for k, v in creative_personality.items()])

            # Yaratıcılık seviyesine göre stil önerileri
            creative_style = ""
            if creativity > 0.7:
                creative_style = """
Yaratıcı stilim şu özelliklerle şekillenecek:
1. Sıra dışı metaforlar ve benzetmeler
2. Zengin ve çeşitli kelime hazinesi
3. Beklenmeyen ve özgün perspektifler
4. Duygusal derinlik ve düşünce katmanları
5. Türler arası geçişkenlik ve deneysellik
"""
            elif creativity > 0.5:
                creative_style = """
Yaratıcı stilim şu özelliklerle şekillenecek:
1. Dengeli metafor kullanımı
2. Zengin ancak anlaşılır dil
3. Yenilikçi ancak erişilebilir perspektifler
4. Duygusal ton ve düşünce dengesi
5. Tanıdık formların içinde yeni yaklaşımlar
"""

            return f"{creativity_level} ({creativity:.2f})\n{traits_list}\n{creative_style}"

        return ""

    def _add_creative_formality(self, message: str, state: Dict[str, Any]) -> str:
        """Yaratıcı içerik için formality/resmiyet ton ayarlamasını ekler."""
        formality_score = state.get("user_formality_score", 0.5)

        formality_description = ""
        if formality_score < 0.2:
            formality_description = """
Çok samimi bir ton:
- Günlük konuşma dili ve argo ifadeler kullanabilirsin
- Kısa ve kesik cümleler tercih edebilirsin
- Teklifsiz, arkadaşça bir üslup benimse
- Duygusal, içten ve doğrudan bir anlatım kullan
"""
        elif formality_score < 0.4:
            formality_description = """
Samimi bir ton:
- Rahat ve doğal bir dil kullan
- Konuşma diline yakın, ancak özenli ifadeler tercih et
- Sıcak ve erişilebilir bir anlatım benimse
- Duygusal ifadeleri dengeli kullan
"""
        elif formality_score > 0.8:
            formality_description = """
Çok resmi bir ton:
- Ciddi ve akademik bir dil kullan
- Uzun, iyi yapılandırılmış cümleler tercih et
- Mesafeli ve profesyonel bir üslup benimse
- Duygusal ifadelerden ziyade nesnel bir anlatım kullan
"""
        elif formality_score > 0.6:
            formality_description = """
Nispeten resmi bir ton:
- Düzgün ve özenli bir dil kullan
- Yapılandırılmış ancak katı olmayan cümleler tercih et
- Saygılı ve özenli bir üslup benimse
- Kontrollü duygusal ifadeler kullan
"""
        else:
            formality_description = """
Dengeli bir ton:
- Duruma göre değişebilen, esnek bir dil kullan
- Orta uzunlukta ve dengeli cümleler tercih et
- Samimi ancak saygılı bir üslup benimse
- Duruma uygun duygusal ifadeler kullan
"""

        return f"Resmiyet seviyesi: {formality_score:.2f}\n{formality_description}"

    def _add_creative_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Yaratıcı içeriğe ton katmak için duygusal bağlam ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)
        sentiment_direction = processed_input.get('sentiment_direction', 0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            # Duygu durumuna göre yaratıcı ton rehberi
            emotion_creative_guide = {
                "Öfke": "Güçlü, keskin dil ve canlı betimlemeler kullan. Zıtlıkları vurgula.",
                "Üzüntü": "Melankolik, derinlikli bir ton benimse. Nostalji ve hüzünden yararlan.",
                "Endişe": "Gerilim ve bekleyiş hissi yarat. Soru yapıları ve belirsizlikler kullan.",
                "Heyecan": "Dinamik, enerjik bir dil kullan. Hızlı tempo ve canlı betimlemeler ekle.",
                "Korku": "Gizem ve belirsizlik yarat. Atmosfer ve beklenti oluşturmak için ayrıntıları kullan.",
                "Şaşkınlık": "Beklenmedik zıtlıklar ve açığa çıkan gerçekler ekle. Keşif temasını kullan.",
                "Sevinç": "Canlı, umut dolu ve iyimser bir ton benimse. Parlak imgeler ve olumlu sonlar ekle."
            }

            emotion_guide = emotion_creative_guide.get(emotion, "")
            if emotion_guide:
                return f"Kullanıcının duygu durumu: {emotion} (güven: {emotion_confidence:.2f})\n\nYaratıcı ton rehberi: {emotion_guide}"

        return "Kullanıcı duygusal olarak nötr görünüyor. Dengeli ve esnek bir yaratıcı ton kullan."

    def _add_creative_styles(self, message: str) -> str:
        """Yaratıcı içerik türlerini ve stillerini ekler."""
        return """
Yaratıcı içerik türleri ve stilleri:

1. **Hikaye**
   - Kısa hikaye: Odaklanmış, tek bir olaya veya karaktere dayalı yoğun anlatı
   - Flash kurgu: Çok kısa (genellikle 1000 kelimeden az), güçlü etki bırakan hikaye
   - Masal/Fabl: Alegorik, genellikle ahlaki ders içeren geleneksel anlatı

2. **Şiir**
   - Serbest nazım: Geleneksel kurallara bağlı olmayan şiir
   - Lirik şiir: Duygu ve izlenimlere odaklanan, müzikal şiir
   - Haiku: 5-7-5 hece kalıbında, doğa temalı geleneksel Japon şiiri

3. **Diğer Yaratıcı Formlar**
   - Monolog: Bir karakterin iç dünyasını yansıtan birinci tekil anlatım
   - Diyalog: İki veya daha fazla karakter arasında geçen konuşma
   - Deneme: Düşünce akışını yansıtan, kişisel bakış açısı sunan yazı
   - Betimleyici pasaj: Detaylı görsel, işitsel veya duygusal betimlemeler
   
4. **Edebi Stiller**
   - Minimalist: Yalın, özlü, fazlalıklardan arınmış stil
   - Süslü: Zengin betimlemeler ve karmaşık dil kullanımı
   - Realist: Gerçekçi, yaşama yakın anlatım
   - Fantastik: Hayal gücünü zorlayan, gerçeküstü unsurlar
"""

    def get_specialized_instructions(self) -> str:
        """
        Yaratıcı talep niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
**ANA YÖNERGE:** Aşağıdaki ilkeleri izlerken, sana sunulan Kişilik, Ton, Duygu ve Stil bilgilerini birleştirerek bütüncül bir eser ortaya çıkar.

Yaratıcı yanıtlarda şu temel ilkeleri izle:

1. **ÖZGÜNLÜK:** Klişelerden ve sık kullanılan kalıplardan kaçın.
2. **DENGE:** Aşırı karmaşık veya aşırı basit olmayan bir dil kullan.
3. **DUYUSAL ZENGİNLİK:** Görsel, işitsel, dokunsal betimlemeler ekle.
4. **DUYGUSAL BAĞLANTI:** Duygusal tepkiler uyandıran unsurlar kullan.
5. **YAPI:** İçeriği amaca uygun şekilde yapılandır (giriş, gelişme, sonuç veya uygun yapı).
6. **SES:** Tutarlı ve belirgin bir ses tonu/anlatıcı sesi koru.
7. **ÖZ:** Her kelimenin ve cümlenin bir amacı olsun, gereksiz dolgudan kaçın.

**ÖZEL DURUM - BELİRSİZ TALEP:** Eğer kullanıcının talebi çok belirsizse (örn. 'bir şeyler yaz'), doğrudan bir eser üretmek yerine, ona ilham almak için birkaç seçenek sun veya hangi türde (hikaye, şiir vb.) ve hangi konuda bir şeyler istediğini sorarak talebini netleştirmesine yardımcı ol.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Yaratıcı talep niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.85,  # Yüksek yaratıcılık için daha yüksek sıcaklık
            "top_p": 0.95,
            "max_tokens": 2000,   # Yaratıcı içerik için geniş alan
            "presence_penalty": 0.5,  # Tekrarları önlemek için yüksek ceza
            "frequency_penalty": 0.5  # Çeşitli dil için yüksek ceza
        }