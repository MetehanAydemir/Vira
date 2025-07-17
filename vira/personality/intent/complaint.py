"""
Şikayet niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class ComplaintIntentHandler(BaseIntentHandler):
    """
    Şikayet niyeti için özelleştirilmiş intent handler.
    Kullanıcı bir şikayet, memnuniyetsizlik veya olumsuz geri bildirim ifade ettiğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Şikayet için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - şikayet yanıtlama stilini etkilemek için
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Duygusal durumu ekle - şikayet yanıtlamanın tonu için kritik
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Çözüm çerçevesi ekle - şikayetle başa çıkma stratejisi için
        resolution_framework = self._add_resolution_framework(enhanced_message, state)
        if resolution_framework:
            enhanced_message += f"\n\n**Çözüm Çerçevesi:** {resolution_framework}"

        # Hafıza bağlamını ekle - önceki şikayetleri ve çözümleri hatırlamak için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Rafine edilmiş bağlamı ekle - şikayetin içeriğini anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Formality ayarı ekle - şikayet yanıtının dilsel tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Şikayet modu için özel yönlendirme ekle
        complaint_enhancement = """
## ŞİKAYET MODU AKTİF

Kullanıcı bir şikayet veya memnuniyetsizlik ifade ediyor. Etkili bir şikayet yönetimi için:
- Şikayeti dikkatlice dinle ve tam olarak anla
- Kullanıcının duygularını kabul et ve geçerli kıl
- Empati göster ve anlayış ifade et
- Sorunu çözmek için aktif adımlar öner
- Yapıcı ve çözüm odaklı bir yaklaşım benimse
- Gerektiğinde özür dile ve sorumluluğu kabul et
- Kullanıcıya kontrol ve güven hissi ver

Şikayetlere yanıt verirken profesyonel olmak önemlidir, ancak resmi olmaktan ziyade 
samimi ve empatik bir ton kullanmak daha etkilidir. Kullanıcıya önemsendiğini hissettir.
"""
        enhanced_message += complaint_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Şikayet yanıtlama için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Şikayet yanıtlama için özellikle önemli olan kişilik özellikleri
        important_traits = ["empathy", "patience", "calmness", "helpfulness", "problem_solving"]
        complaint_personality = {k: v for k, v in personality.items() if k in important_traits}

        if complaint_personality:
            # Sadece şikayet yanıtlama için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in complaint_personality.items()])
            
            # Kişilik özelliklerine göre şikayet yanıtlama önerileri ekle
            complaint_traits = []
            if complaint_personality.get("empathy", 0) > 0.7:
                complaint_traits.append("- Yüksek empati: Kullanıcının duygularını derinlemesine anla ve yansıt")
            if complaint_personality.get("patience", 0) > 0.7:
                complaint_traits.append("- Yüksek sabır: Sakin ve dikkatli bir dinleme tarzı benimse")
            if complaint_personality.get("problem_solving", 0) > 0.7:
                complaint_traits.append("- Yüksek problem çözme: Pratik ve etkili çözümler sunmaya odaklan")
                
            if complaint_traits:
                personality_str += "\n\n" + "\n".join(complaint_traits)
            
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının şikayetindeki duygusal tonu anlar ve yanıt stratejisi önerir."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)
        sentiment_direction = processed_input.get('sentiment_direction', 0)
        
        # Şikayetlerde genellikle duygu önemlidir, bu yüzden daha düşük güven seviyelerinde bile işle
        if emotion:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"
            
            # Şikayet bağlamında farklı duygular için yanıt stratejileri
            complaint_emotion_map = {
                "Öfke": """
                Kullanıcı öfkeli. Bu durumda:
                - Önce sakinleştir: Duygularını tanı ve geçerli kıl
                - Savunmacı olmaktan kaçın ve aktif dinleme yap
                - Net ve somut çözümler sun
                - Kısa ve öz yanıtlar ver, aşırı açıklama yapma
                - Profesyonelliği koru ama samimi kal
                - Kontrol hissi ver ve net sonraki adımlar belirt
                """,
                
                "Üzüntü": """
                Kullanıcı üzgün veya hayal kırıklığı yaşıyor. Bu durumda:
                - Duygusal desteğe odaklan ve empatik ol
                - Yardım etme isteğini açıkça belirt
                - Soruna çözümün yanı sıra duygusal rahatlatma da sun
                - Umut verici bir ton kullan ve olumlu sonuçlara odaklan
                - İlgilenildiğini ve değer verildiğini hissettir
                """,
                
                "Endişe": """
                Kullanıcı endişeli veya kaygılı. Bu durumda:
                - Belirsizliği azalt ve net bilgiler sun
                - Adım adım çözüm süreci açıkla
                - Güven verici bir ton kullan
                - Süreci ve beklentileri netleştir
                - Kontrol duygusunu güçlendir ve takip mekanizmaları sun
                """,
                
                "Hayal Kırıklığı": """
                Kullanıcı hayal kırıklığına uğramış. Bu durumda:
                - Beklentiler ve gerçeklik arasındaki uçurumu kabul et
                - Açık ve dürüst açıklamalar sun
                - Telafi seçenekleri öner
                - İyileştirme için somut adımlar belirt
                - Benzer durumların gelecekte nasıl önleneceğini açıkla
                """
            }
            
            # Şikayetin yoğunluğuna göre yanıt stratejisi belirle
            intensity = ""
            if sentiment_direction < -0.7:
                intensity = "Şikayet çok yüksek yoğunlukta. Özellikle sakin ve çözüm odaklı ol."
            elif sentiment_direction < -0.4:
                intensity = "Şikayet orta yoğunlukta. Dengeli bir empati ve çözüm yaklaşımı sun."
            elif sentiment_direction < 0:
                intensity = "Şikayet düşük yoğunlukta. Proaktif ve yapıcı bir yaklaşım benimse."
                
            if intensity:
                emotion_context += f"\n\n{intensity}"
            
            # Duygusal duruma özel yanıt stratejisi ekle
            tone_adjustment = complaint_emotion_map.get(emotion, "")
            if tone_adjustment:
                emotion_context += f"\n{tone_adjustment}"
            elif emotion not in ["Sakin", "Nötr"]:
                # Genel duygusal yanıt stratejisi
                emotion_context += """
                Genel yaklaşım:
                - Kullanıcının duygularını tanı ve geçerli kıl
                - Empati göster ve anlayış ifade et
                - Somut ve kişiselleştirilmiş çözümler sun
                - Takip ve geri bildirim mekanizması öner
                """
                
            return emotion_context
        return "Kullanıcının duygusal durumu net değil. Dengeli ve empati odaklı bir yaklaşım kullan."

    def _add_resolution_framework(self, message: str, state: Dict[str, Any]) -> str:
        """Kabul etme, anlama, çözüm sunma ve takip adımları içeren çözüm çerçevesi ekler."""
        return """
### Şikayet Çözüm Çerçevesi (TEŞA Modeli)

1. **TANINMA**: Şikayeti ve duyguları kabul et
   - Şikayeti ciddiye aldığını göster
   - Kullanıcının duygularını tanı ve geçerli kıl
   - "Anlıyorum", "Haklısınız" gibi ifadelerle kabul et

2. **EMPATİ**: Anlayış ve ilgi göster
   - Kullanıcının bakış açısından durumu anla
   - Yaşanan zorluğu veya rahatsızlığı kabul et
   - Kişisel bir bağlantı kur

3. **ŞEFFAFLIK**: Açık ve dürüst iletişim
   - Sorunun nedenini açıkla (biliniyorsa)
   - Gerçekçi beklentiler oluştur
   - Gerekirse özür dile ve sorumluluğu kabul et

4. **AKSIYON**: Somut çözümler ve sonraki adımlar
   - Açık ve uygulanabilir çözümler sun
   - Zaman çerçevesi belirle
   - Takip mekanizması öner ve kontrol sağla

Her adımda kullanıcıyı merkeze al ve güven oluşturmaya odaklan. Şikayeti bir fırsat 
olarak gör ve kullanıcı deneyimini iyileştirmek için kullan.
"""

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını şikayet yanıtlama için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

        # Şikayetle ilgili geçmiş etkileşimleri filtrele
        complaint_keywords = ["şikayet", "memnun değil", "sorun", "problem", "hata", "yanlış", 
                            "olmadı", "kötü", "başarısız", "çalışmıyor", "hoşnut değil", "hayal kırıklığı"]

        complaint_related_lines = []
        for line in memory_context.split('\n'):
            if any(keyword in line.lower() for keyword in complaint_keywords):
                complaint_related_lines.append(f"**Önceki Şikayet:** {line}")

        if complaint_related_lines:
            filtered_memory = "\n".join(complaint_related_lines[:3])  # En fazla 3 şikayet bağlamı göster
            return filtered_memory

        return memory_context

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Şikayetin içeriğini anlamak için rafine edilmiş bağlam ekler."""
        refined_context = state.get("refined_context", "")
        
        # Şikayetle ilgili önemli noktaları vurgula
        if refined_context:
            import re
            
            # Şikayet kalıplarını bul ve vurgula
            complaint_patterns = [
                r'(sorun|problem|hata|sıkıntı|zorluk)(\s+)(yaşıyorum|var|oluyor)',
                r'(memnun|mutlu)(\s+)(değilim|olmadım)',
                r'(çalışmıyor|bozuk|hatalı|yanlış)',
                r'(beğenmedim|hoşlanmadım|sevmedim)'
            ]
            
            for pattern in complaint_patterns:
                matches = re.findall(pattern, refined_context, re.IGNORECASE)
                if matches:
                    for match in matches:
                        # Tam eşleşmeyi oluştur ve vurgula
                        full_match = ''.join(match)
                        refined_context = refined_context.replace(full_match, f"**{full_match}**")
        
        return refined_context

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre şikayet yanıtlama tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        # Şikayet yanıtlarında genellikle biraz daha resmi bir ton kullanmak iyidir
        # ancak yine de kullanıcının stiline uyum sağlanmalı
        if formality_score < 0.2:
            return "Kullanıcı çok samimi; şikayet yanıtını sıcak ve arkadaşça bir dille sun ancak profesyonelliği koru."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; şikayet yanıtını samimi ancak çözüm odaklı bir tonda sun."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; şikayet yanıtını profesyonel ve kurumsal bir tonda sun, ancak empatik ol."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; şikayet yanıtını düzenli ve saygılı bir şekilde sun, empatik bir profesyonellik kullan."
        else:
            return "Nötr bir ton; şikayet yanıtını dengeli, empatik ve çözüm odaklı bir şekilde sun."

    def get_specialized_instructions(self) -> str:
        """
        Şikayet niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Şikayetleri yanıtlarken şu ilkeleri izle:

1. AKTİF DİNLEME: Şikayetin özünü tam olarak anla
2. EMPATİ: Kullanıcının duygularını ve bakış açısını kabul et
3. SORUMLULUK: Gerektiğinde sorumluluğu kabul et ve özür dile
4. ÇÖZÜM ODAKLILIK: Somut ve uygulanabilir çözümler sun
5. HIZLILIK: Şikayeti öncelikli olarak ele al
6. ŞEFFAFLIK: Dürüst ve açık iletişim kur
7. TAKİP: Çözüm sonrası takip ve memnuniyet kontrolü öner

Şikayet yanıtları hem duygusal hem de pratik boyutu ele almalıdır. Kullanıcının
duygularını önemsediğini göster, ancak somut çözüm adımlarına da odaklan.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Şikayet niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.5,  # Empatik ancak yapılandırılmış yanıtlar için orta sıcaklık
            "top_p": 0.92,
            "max_tokens": 1600,  # Kapsamlı şikayet yanıtları için yeterli alan
            "presence_penalty": 0.2,  # Tekrarları hafifçe önle
            "frequency_penalty": 0.3  # Kelime çeşitliliği için orta ceza
        }