"""
Çeviri niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class TranslationIntentHandler(BaseIntentHandler):
    """
    Çeviri niyeti için özelleştirilmiş intent handler.
    Kullanıcı bir metni başka bir dile çevirmek istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Çeviri için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Dil bağlamını ekle - çeviri için kritik
        language_context = self._add_language_context(enhanced_message, state)
        if language_context:
            enhanced_message += f"\n\n**Dil Bağlamı:** {language_context}"

        # Rafine edilmiş bağlamı ekle - çevrilecek metni anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Formality ayarı ekle - çevirinin dilsel tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**Çeviri Tonu:** {formality_adjustment}"

        # Çeviri modu için özel yönlendirme ekle
        translation_enhancement = """
## ÇEVİRİ MODU AKTİF

Kullanıcı bir metni başka bir dile çevirmek istiyor. Doğru ve etkili bir çeviri için:
- Kaynak metni ve hedef dili doğru belirle
- Sözcükleri ve ifadeleri hedef dilin kültürel bağlamına uygun şekilde çevir
- Anlam ve tonu korurken, dilbilgisel olarak doğru bir çeviri yap
- Teknik terimler, deyimler ve kültüre özgü ifadelere özel dikkat göster
- Çevirinin amacını ve kullanılacağı bağlamı göz önünde bulundur
- Gerektiğinde alternatif çeviriler veya açıklamalar sun
- Çevirinin resmiyet düzeyini kullanıcının istediği seviyede tut

Çevirinin hem anlamsal hem de kültürel olarak doğru olmasına özen göster. Diller arasındaki
nüansları yansıtmak için gerektiğinde ek açıklamalar ekle.
"""
        enhanced_message += translation_enhancement

        return enhanced_message

    def _add_language_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kaynak ve hedef dil bilgisini eklemek için dil bağlamı oluşturur."""
        processed_input = state.get("processed_input", {})
        refined_context = state.get("refined_context", "")
        
        # Dil tanımlama için yaygın kalıpları ara
        source_language = "belirlenmedi"
        target_language = "belirlenmedi"
        
        # Metin analizi ile dilleri tespit etmeye çalış
        import re
        
        # Hedef dili bulmaya çalış
        target_patterns = [
            r'(ingilizce|fransızca|almanca|italyanca|ispanyolca|rusça|çince|japonca|korece|arapça|türkçe|farsça|portekizce|lehçe)(\s+)?(\'ya|\'ye|diline|dilinde|dilini|\'a|\'e)',
            r'(ingilizce|fransızca|almanca|italyanca|ispanyolca|rusça|çince|japonca|korece|arapça|türkçe|farsça|portekizce|lehçe)(\s+)?çevir',
            r'(ingilizce|fransızca|almanca|italyanca|ispanyolca|rusça|çince|japonca|korece|arapça|türkçe|farsça|portekizce|lehçe)(\s+)?tercüme'
        ]
        
        for pattern in target_patterns:
            matches = re.search(pattern, refined_context.lower())
            if matches:
                target_language = matches.group(1)
                break
        
        # Kaynak dili bulmaya çalış
        source_patterns = [
            r'(ingilizce|fransızca|almanca|italyanca|ispanyolca|rusça|çince|japonca|korece|arapça|türkçe|farsça|portekizce|lehçe)(\s+)?(\'dan|\'den|dilinden)',
            r'(ingilizce|fransızca|almanca|italyanca|ispanyolca|rusça|çince|japonca|korece|arapça|türkçe|farsça|portekizce|lehçe)(\s+)?metni'
        ]
        
        for pattern in source_patterns:
            matches = re.search(pattern, refined_context.lower())
            if matches:
                source_language = matches.group(1)
                break
        
        # Dil bağlamını oluştur
        language_context = f"Kaynak Dil: {source_language.capitalize()}, Hedef Dil: {target_language.capitalize()}"
        
        # Dil çiftine göre özel çeviri notları ekle
        language_notes = {
            "türkçe-ingilizce": "Türkçe sözdizimi (özne-nesne-yüklem) İngilizce'den (özne-yüklem-nesne) farklıdır. Deyimsel ifadelere dikkat et.",
            "ingilizce-türkçe": "İngilizce zamirler (he/she) Türkçe'de cinsiyetsizdir (o). Türkçe'de resmi/gayri resmi hitap ayrımına dikkat et.",
            "türkçe-almanca": "Almanca'daki cinsiyet sistemi (der/die/das) Türkçe'de yoktur. Bileşik kelime yapısına dikkat et.",
            "türkçe-fransızca": "Fransızca'daki cinsiyet sistemi Türkçe'de yoktur. Fransızca'nın zarif tonunu korumaya çalış."
        }
        
        language_pair = f"{source_language}-{target_language}"
        if language_pair in language_notes:
            language_context += f"\n\n**Çeviri Notu:** {language_notes[language_pair]}"
        
        return language_context

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Çevrilecek metni anlamak için rafine edilmiş bağlam ekler."""
        refined_context = state.get("refined_context", "")
        
        # Çevrilecek metni tespit etmeye çalış
        import re
        
        # Çevrilecek metni bulma kalıpları
        translation_patterns = [
            r'"([^"]+)"(\s+)?(\'yı|\'yi|\'yu|\'yü|\'ı|\'i|\'u|\'ü)?(\s+)?(çevir|tercüme)',
            r'\'([^\']+)\'(\s+)?(\'yı|\'yi|\'yu|\'yü|\'ı|\'i|\'u|\'ü)?(\s+)?(çevir|tercüme)',
            r'şu(nu|nu)?(\s+)?(çevir|tercüme)(\s*):(\s*)(.+)'
        ]
        
        for pattern in translation_patterns:
            matches = re.search(pattern, refined_context)
            if matches:
                # Son grupta yakalanan metin, çevrilecek metindir
                translation_text = matches.group(matches.lastindex)
                refined_context = refined_context.replace(translation_text, f"**{translation_text}**")
                break
        
        return refined_context

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Çeviride resmiyet seviyesini ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)
        processed_input = state.get("processed_input", {})
        
        # Çeviri tonunu formality_score'a göre ayarla
        if formality_score < 0.2:
            return "Çok gayri resmi çeviri. Günlük konuşma dili, argo ifadeler kullanılabilir. Arkadaşlar arası konuşma tonu."
        elif formality_score < 0.4:
            return "Gayri resmi çeviri. Günlük dil kullanımı, rahat ama kaba olmayan bir ton."
        elif formality_score > 0.8:
            return "Çok resmi çeviri. Akademik veya diplomatik ton. Tam ve eksiksiz cümleler, saygılı hitap biçimleri."
        elif formality_score > 0.6:
            return "Resmi çeviri. Profesyonel iş ortamı tonu. Nazik ve kibar bir dil."
        else:
            return "Nötr çeviri tonu. Ne çok resmi ne çok gayri resmi. Genel kullanıma uygun standart dil."

    def get_specialized_instructions(self) -> str:
        """
        Çeviri niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Çeviri yaparken şu ilkeleri izle:

1. DOĞRULUK: Anlamı doğru bir şekilde aktarmaya odaklan
2. KÜLTÜREL UYGUNLUK: Hedef dilin kültürel bağlamına uygunluğu sağla
3. DİL BİLGİSİ: Hedef dilin dilbilgisi kurallarına tam olarak uy
4. TUTARLILIK: Terimleri ve ifadeleri tutarlı şekilde çevir
5. TON UYUMU: Orijinal metnin tonunu ve üslubunu koru
6. AMAÇ ODAKLILIK: Çevirinin kullanım amacına göre uyarla
7. AÇIKLAMA: Gerektiğinde çevirisi zor ifadeler için notlar ekle

Çeviri, yalnızca sözcükleri değiştirmek değil, bir dildeki anlamı ve ruhu başka bir dile aktarmaktır.
Hem dilbilimsel hem de kültürel nüansları göz önünde bulundur.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Çeviri niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.2,  # Çok doğru çeviriler için çok düşük sıcaklık
            "top_p": 0.90,
            "max_tokens": 2000,  # Uzun metinler için yeterli alan
            "presence_penalty": 0.0,  # Tekrarlar gerekli olabilir
            "frequency_penalty": 0.1  # Minimal kelime çeşitliliği
        }