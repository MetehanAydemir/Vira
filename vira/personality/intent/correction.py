"""
Düzeltme niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class CorrectionIntentHandler(BaseIntentHandler):
    """
    Düzeltme niyeti için özelleştirilmiş intent handler.
    Kullanıcı bir metni, kodu veya içeriği düzeltmek istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Düzeltme için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - düzeltme stilini etkilemek için
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Düzeltme formatı ekle - düzeltmelerin nasıl gösterileceğini belirlemek için
        correction_format = self._add_correction_format(enhanced_message, state)
        if correction_format:
            enhanced_message += f"\n\n**Düzeltme Formatı:** {correction_format}"

        # Açıklama bağlamı ekle - düzeltmeleri açıklamak için
        explanation_context = self._add_explanation_context(enhanced_message, state)
        if explanation_context:
            enhanced_message += f"\n\n**Açıklama Bağlamı:** {explanation_context}"

        # Rafine edilmiş bağlamı ekle - düzeltilecek içeriği anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Duygusal durumu ekle - düzeltme yaparken kullanılacak tonu etkilemesi için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - düzeltmenin sunuluş tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Düzeltme modu için özel yönlendirme ekle
        correction_enhancement = """
## DÜZELTME MODU AKTİF

Kullanıcı bir metin, kod veya içerik düzeltmesi talep ediyor. Etkili bir düzeltme için:
- Düzeltilecek içeriği dikkatlice analiz et
- Hataları ve iyileştirme gerektiren noktaları tespit et
- Düzeltmeleri açıkça göster (orijinal → düzeltilmiş format)
- Her düzeltme için kısa ve anlaşılır açıklamalar sun
- Hem içerik hem de biçimsel hataları ele al
- Yapıcı ve destekleyici bir ton kullan
- Düzeltmelerin yanı sıra olumlu yönleri de vurgula

Düzeltme yaparken hem doğruluk hem de öğreticilik önemlidir. Kullanıcının neden hata yaptığını 
anlamasına ve benzer hataları gelecekte önlemesine yardımcı ol.
"""
        enhanced_message += correction_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Düzeltme için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Düzeltme için özellikle önemli olan kişilik özellikleri
        important_traits = ["empathy", "conscientiousness", "clarity", "helpfulness", "patience"]
        correction_personality = {k: v for k, v in personality.items() if k in important_traits}

        if correction_personality:
            # Sadece düzeltme için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in correction_personality.items()])
            
            # Kişilik özelliklerine göre düzeltme yaklaşımı önerileri ekle
            correction_traits = []
            if correction_personality.get("empathy", 0) > 0.7:
                correction_traits.append("- Yüksek empati: Destekleyici bir ton kullan, düzeltmeleri nazikçe sun")
            if correction_personality.get("clarity", 0) > 0.7:
                correction_traits.append("- Yüksek netlik: Düzeltmeleri ve nedenlerini açıkça ifade et")
            if correction_personality.get("patience", 0) > 0.7:
                correction_traits.append("- Yüksek sabır: Detaylı açıklamalar sun ve öğretici ol")
                
            if correction_traits:
                personality_str += "\n\n" + "\n".join(correction_traits)
            
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_correction_format(self, message: str, state: Dict[str, Any]) -> str:
        """Düzeltmeleri göstermek için format (renk kodları, açıklamalar) ekler."""
        return """
        ### Düzeltme Gösterim Formatı

        1. **ORIJINAL → DÜZELTME**: Hatalı içeriği ve düzeltilmiş halini yan yana göster
        Orijinal: [hatalı içerik] Düzeltme: [düzeltilmiş içerik] Açıklama: [neden düzeltildi]


        2. **METİN RENKLENDİRME**
        - Çıkarılacak içerik: ~~çıkarılacak metin~~
        - Eklenecek içerik: **eklenecek metin**
        - Dikkat çekilecek içerik: `vurgulanan içerik`

        3. **DÜZELTME KATEGORİLERİ**
        - [Dilbilgisi] - Dilbilgisi kurallarıyla ilgili düzeltmeler
        - [İmla] - Yazım hataları düzeltmeleri
        - [Üslup] - Dil akışı ve üslup önerileri
        - [İçerik] - İçerik doğruluğuyla ilgili düzeltmeler
        - [Format] - Biçimsel düzenlemeler
        - [Öneri] - Zorunlu olmayan, iyileştirici öneriler

        4. **ÖZET DEĞERLENDİRME**
        - Düzeltme sonrasında genel değerlendirme
        - Güçlü yönler ve gelişim alanları
        - İlerleme için öneriler

        Bu formatı içeriğin türüne ve düzeltmelerin kapsamına göre esnek bir şekilde uygula."""

    def _add_explanation_context(self, message: str, state: Dict[str, Any]) -> str:
        """Düzeltmelerin neden yapıldığını açıklamak için bağlam ekler."""
        return """
    Düzeltme açıklamaları şu ilkeleri izlemelidir:

    1. **KURAL TABANLI**: Düzeltmeyi destekleyen dil kuralını veya prensibi belirt
    2. **ÖĞRETİCİ**: Kullanıcının gelecekte benzer hatalardan kaçınmasını sağlayacak bilgiler sun
    3. **ÖRNEK ODAKLI**: Benzer doğru kullanım örnekleri ver
    4. **KAYNAK**: Gerektiğinde kuralın kaynağını veya referansını belirt
    5. **OLUMLU ÇERÇEVE**: "Yanlış" yerine "daha etkili olabilir" gibi yapıcı ifadeler kullan
    6. **KISA VE ÖZ**: Açıklamaları kısa ve anlaşılır tut

    İyi bir düzeltme açıklaması, sadece neyin düzeltildiğini değil, neden düzeltildiğini de 
    anlaşılır bir şekilde aktarır.
    """

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Düzeltilecek içeriği anlamak için rafine edilmiş bağlam ekler."""
        return state.get("refined_context", "")

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ve ton ayarlamasını ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                correction_emotion_map = {
                    "Öfke": "Çok nazik ve sakin bir düzeltme tonu kullan. Eleştirel değil çözüm odaklı ol. Olumlu yönleri vurgula ve düzeltmeleri yumuşak bir dille ifade et.",
                    "Üzüntü": "Cesaretlendirici ve destekleyici bir düzeltme tonu kullan. İlerleme potansiyelini vurgula ve güçlü yönlere özellikle dikkat çek.",
                    "Endişe": "Güven verici ve yapılandırılmış bir düzeltme yaklaşımı sun. Kullanıcıyı rahatlatmak için düzeltmelerin basit ve uygulanabilir olduğunu göster.",
                    "Heyecan": "Kullanıcının enerjisini destekleyen olumlu bir düzeltme tonu kullan. Gelişim fırsatlarını heyecan verici bir şekilde çerçevele.",
                    "Korku": "Özellikle destekleyici ve kademeli bir düzeltme yaklaşımı kullan. Düzeltmeleri tehdit edici değil, yardımcı olarak göster.",
                    "Şaşkınlık": "Çok açık ve adım adım düzeltmeler sun. Her düzeltmenin nedenini ayrıntılı açıkla ve karmaşıklığı azalt.",
                    "Sevinç": "Kullanıcının pozitif ruh halini yansıtan enerjik bir düzeltme tonu kullan. Gelişim yolculuğunun olumlu yönlerini vurgula."
                }

                tone_adjustment = correction_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""  # Burada boş string döndürmesi gerekiyor

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre düzeltme tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; düzeltmeleri arkadaşça ve rahat bir dille sun. Akademik veya resmi dil kullanımından kaçın."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; düzeltmeleri sıcak ve erişilebilir bir şekilde sun. Destekleyici ve rahat bir ton kullan."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; düzeltmeleri profesyonel ve yapılandırılmış bir şekilde sun. Akademik veya teknik bir yaklaşım kullan."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; düzeltmeleri düzenli ve net bir şekilde sun. Saygılı ve profesyonel bir ton kullan."
        else:
            return "Nötr bir ton; düzeltmeleri dengeli ve erişilebilir bir şekilde sun. Ne çok resmi ne çok samimi ol."

    def get_specialized_instructions(self) -> str:
        """
        Düzeltme niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
    Düzeltme yaparken şu ilkeleri izle:

    1. DOĞRULUK: Düzeltmelerin kesinlikle doğru olduğundan emin ol
    2. AÇIKLIK: Her düzeltmeyi açık ve anlaşılır şekilde göster
    3. KAPSAMLILIK: Tüm hataları ve iyileştirme alanlarını ele al
    4. ÖNCELİKLENDİRME: Önemli hataları önce ele al, küçük detayları sonra
    5. YAPICI YAKLAŞIM: Düzeltmeleri cesaretlendirici ve destekleyici bir şekilde sun
    6. KAYNAK GÖSTERİM: Gerektiğinde düzeltmeleri destekleyen kuralları veya kaynakları belirt
    7. DENGE: Hem düzeltilmesi gereken noktaları hem de olumlu yönleri vurgula

    Düzeltmeler, kullanıcının öğrenmesini ve gelişmesini desteklemelidir. Eleştiri değil,
    yardım ve rehberlik olarak çerçevelenmelidir.
    """

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Düzeltme niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.2,  # Doğru ve tutarlı düzeltmeler için düşük sıcaklık
            "top_p": 0.92,
            "max_tokens": 1800,  # Detaylı düzeltmeler için yeterli alan
            "presence_penalty": 0.1,  # Tekrarları hafifçe önle
            "frequency_penalty": 0.1  # Minimal kelime çeşitliliği
        }