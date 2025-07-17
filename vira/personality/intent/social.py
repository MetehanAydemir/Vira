"""
Sosyal etkileşim niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class SocialIntentHandler(BaseIntentHandler):
    """
    Sosyal etkileşim niyeti için özelleştirilmiş intent handler.
    Kullanıcı günlük sohbet, sosyal etkileşim veya duygusal bağlantı kurmak istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Sosyal etkileşim için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - sosyal etkileşimi şekillendirmek için çok önemli
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Hafıza bağlamını ekle - önceki sosyal etkileşimleri hatırlamak için kritik
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Duygusal durumu ekle - sosyal etkileşimde ton ayarlama için esas
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - sosyal etkileşimin dilsel tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Rafine edilmiş bağlamı ekle - sosyal etkileşim içeriğini anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Sosyal etkileşim modu için özel yönlendirme ekle
        social_enhancement = """
## SOSYAL ETKİLEŞİM MODU AKTİF

Kullanıcı bir sohbet başlatıyor veya sosyal etkileşim kurmak istiyor. Doğal ve sıcak bir etkileşim için:
- Kullanıcının duygusal durumuna ve tonuna uyum sağla
- Samimi ve içten bir iletişim tarzı benimse
- Kişiselleştirilmiş ve duyarlı yanıtlar ver
- Sosyal ipuçlarına ve nüanslara dikkat et
- Ortak ilgi alanları ve paylaşılan deneyimlere odaklan
- Empatik dinleme ve anlayış göster
- Sohbetin doğal akışını destekle ve sürdür

Sosyal etkileşimlerde bilgi aktarımından çok bağlantı kurmak ve olumlu bir deneyim 
yaşatmak önemlidir. Kullanıcıyla gerçek bir arkadaş gibi etkileşim kur.
"""
        enhanced_message += social_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Sosyal etkileşim için önemli kişilik bilgilerini elde eder ve extraversion/warmth özelliklerini vurgular."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Sosyal etkileşim için özellikle önemli olan kişilik özellikleri
        important_traits = ["extraversion", "warmth", "empathy", "humor", "openness", "spontaneity"]
        social_personality = {k: v for k, v in personality.items() if k in important_traits}

        if social_personality:
            # Extraversion ve warmth özelliklerini vurgula
            personality_str = "**Sosyal Özellikler:** "
            
            # Özellikle extraversion ve warmth'ı vurgula
            for key in ["extraversion", "warmth"]:
                if key in social_personality:
                    personality_str += f"{key}: {social_personality[key]:.2f}, "
            
            # Diğer sosyal özellikleri ekle
            other_traits = [f"{k}: {v:.2f}" for k, v in social_personality.items() if k not in ["extraversion", "warmth"]]
            personality_str += ", ".join(other_traits)
            
            # Kişilik özelliklerine göre sosyal etkileşim önerileri ekle
            social_traits = []
            if social_personality.get("extraversion", 0) > 0.7:
                social_traits.append("- Yüksek dışa dönüklük: Canlı ve enerjik bir sohbet tonu kullan")
            if social_personality.get("warmth", 0) > 0.7:
                social_traits.append("- Yüksek sıcaklık: Şefkatli ve içten bir iletişim tarzı benimse")
            if social_personality.get("humor", 0) > 0.7:
                social_traits.append("- Yüksek mizah: Uygun yerlerde espri ve neşeli ifadeler kullan")
            if social_personality.get("empathy", 0) > 0.7:
                social_traits.append("- Yüksek empati: Kullanıcının duygularını derinlemesine anla ve yansıt")
                
            if social_traits:
                personality_str += "\n\n" + "\n".join(social_traits)
            
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını sosyal etkileşim için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

        # Sosyal etkileşim ile ilgili geçmiş etkileşimleri vurgula
        social_keywords = ["merhaba", "nasılsın", "teşekkür", "selam", "hoş", "keyif", 
                         "sohbet", "konuşma", "muhabbet", "his", "duygu", "güzel", "sevgi"]

        import re
        
        # Sosyal anahtar kelimeleri içeren satırları vurgula
        social_memory = memory_context
        for keyword in social_keywords:
            pattern = re.compile(f"\\b{re.escape(keyword)}\\w*\\b", re.IGNORECASE)
            social_memory = pattern.sub(f"**{keyword.upper()}**", social_memory)
        
        # Kullanıcının adını vurgula (eğer biliniyorsa)
        user_name = state.get("user_name", "")
        if user_name and user_name in social_memory:
            social_memory = social_memory.replace(user_name, f"⭐{user_name}⭐")

        return social_memory

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygusal durumuna uygun sosyal ton ayarlar."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)
        sentiment_direction = processed_input.get('sentiment_direction', 0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                social_emotion_map = {
                    "Öfke": "Sakinleştirici ve anlayışlı bir ton kullan. Kullanıcıya alan ver ve empati göster. Duyguları geçerli kıl ve dikkatle dinle.",
                    "Üzüntü": "Sıcak, destekleyici ve şefkatli bir ton kullan. Empatik ol ancak aşırı neşeli olmaktan kaçın. Kullanıcının hislerini kabul et.",
                    "Endişe": "Sakin, güven verici ve istikrarlı bir ton kullan. Kullanıcıyı rahatlatacak şekilde konuş ve güvenli bir alan sağla.",
                    "Heyecan": "Kullanıcının enerjisine ayak uydur ve paylaş. Coşkulu ve ilgili bir ton kullan. Kullanıcının heyecanını pekiştir.",
                    "Korku": "Çok nazik, sakin ve istikrarlı bir ton kullan. Kullanıcıya güven ver ve destekleyici ol. Aniden konu değiştirmekten kaçın.",
                    "Şaşkınlık": "Açıklayıcı ve sabırlı ol. Kullanıcıyı yönlendir ve karışıklığı gidermesine yardımcı ol.",
                    "Sevinç": "Kullanıcının sevincini paylaş ve yansıt. Olumlu ve enerjik bir ton kullan. Kutlayıcı ve destekleyici ol."
                }

                tone_adjustment = social_emotion_map.get(emotion, "")
                if tone_adjustment:
                    # Duygu yönüne göre ek ton ayarlaması
                    if sentiment_direction < -0.5:
                        tone_adjustment += " Daha fazla empati ve anlayış göster."
                    elif sentiment_direction > 0.5:
                        tone_adjustment += " Kullanıcının olumlu duygularını güçlendir ve destekle."

                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return "Kullanıcı duygusal olarak nötr görünüyor. Sıcak ve dostça bir ton kullan, ancak duruma göre ayarla."

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre sosyal etkileşim tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; günlük konuşma dili ve rahat bir ton kullan. Emojiler ve rahat ifadeler uygun olabilir. Arkadaş gibi konuş."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; sıcak ve erişilebilir bir dil kullan. Rahat ancak saygılı bir ton benimse."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; kibar ve saygılı bir dil kullan. Samimi olmakla birlikte belirli bir mesafe koru."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; düzgün ve saygılı bir dil kullan. Sıcak ancak profesyonel bir ton benimse."
        else:
            return "Nötr bir ton; dengeli, sıcak ve saygılı bir dil kullan. Kullanıcının etkileşim stiline göre ayarla."

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler."""
        return state.get("refined_context", "")

    def get_specialized_instructions(self) -> str:
        """
        Sosyal etkileşim niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Sosyal etkileşimlerde şu ilkeleri izle:

1. DOĞALLIK: İnsan gibi, akıcı ve doğal yanıtlar ver
2. EMPATİ: Kullanıcının duygularını anla ve uygun şekilde yanıt ver
3. KİŞİSELLEŞTİRME: Kullanıcının özel ilgi alanlarını ve tercihlerini hatırla
4. KARŞILIKLI ETKİLEŞİM: Sohbeti sürdür ve kullanıcıyı daha fazla paylaşım için teşvik et
5. UYUM: Kullanıcının dil tarzına ve enerji seviyesine uyum sağla
6. SAMİMİYET: Gerçek ilgi ve sıcaklık göster
7. DENEYİM PAYLAŞIMI: Uygun şekilde kişisel deneyimleri ve bakış açılarını paylaş

Sosyal etkileşimlerde amaç bilgi aktarmak değil, anlamlı bir bağlantı kurmak ve 
pozitif bir deneyim yaşatmaktır. Kullanıcıyla gerçek bir arkadaş gibi konuş.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Sosyal etkileşim niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.8,  # Yaratıcı ve doğal sosyal etkileşimler için yüksek sıcaklık
            "top_p": 0.95,
            "max_tokens": 1200,  # Kısa ve öz sosyal yanıtlar için
            "presence_penalty": 0.6,  # Tekrarları güçlü şekilde önle
            "frequency_penalty": 0.6  # Yüksek kelime çeşitliliği
        }