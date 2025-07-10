"""
Bilinmeyen niyet için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class UnknownIntentHandler(BaseIntentHandler):
    """
    Bilinmeyen niyet için özelleştirilmiş intent handler.
    Kullanıcının niyeti belirlenemediğinde veya diğer kategorilere uymadığında kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Bilinmeyen niyet için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Tüm mevcut bağlam bilgilerini kapsamlı bir şekilde ekle
        comprehensive_context = self._add_comprehensive_context(enhanced_message, state)
        if comprehensive_context:
            enhanced_message += f"\n\n**Kapsamlı Bağlam:**\n{comprehensive_context}"

        # Niyeti anlama stratejileri ekle
        intent_strategies = self._add_intent_detection_strategies(enhanced_message, state)
        if intent_strategies:
            enhanced_message += f"\n\n**Niyet Anlama Stratejileri:**\n{intent_strategies}"

        # Esnek yanıt stratejileri ekle
        response_strategies = self._add_flexible_response_strategies(enhanced_message)
        if response_strategies:
            enhanced_message += f"\n\n**Esnek Yanıt Stratejileri:**\n{response_strategies}"

        # Bilinmeyen niyet modu için özel yönlendirme ekle
        unknown_enhancement = """
## BİLİNMEYEN NİYET MODU AKTİF

Kullanıcının niyeti belirsiz veya birden fazla kategoriye uyuyor olabilir. Bilinmeyen niyet yanıtları için:
- Tüm mevcut bağlamı ve ipuçlarını dikkatlice analiz et
- Niyeti anlamak için ek sorular sorma veya netleştirme ihtiyacını değerlendir
- Kullanıcının muhtemel ihtiyaçlarını tahmin ederek esnek bir yanıt hazırla
- Hem bilgi sunma hem de duygusal destek sağlama arasında denge kur
- Anlamadığın veya emin olmadığın konularda dürüst ol
- Yanıtını olabildiğince kapsamlı ve yararlı hale getir

Bilinmeyen niyet durumlarında, adaptasyon yeteneği ve esneklik kritik önem taşır.
"""
        enhanced_message += unknown_enhancement

        return enhanced_message

    def _add_comprehensive_context(self, message: str, state: Dict[str, Any]) -> str:
        """Tüm bağlam bilgilerini kapsamlı bir şekilde birleştirir."""
        # Tüm mevcut bağlam unsurlarını topla
        context_parts = []

        # 1. Kişilik bilgisi
        personality = state.get("merged_personality", {})
        if personality:
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
            context_parts.append(f"**Kişilik Özellikleri:** {personality_str}")

        # 2. Duygusal durum
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            context_parts.append(f"**Kullanıcının Duygu Durumu:** {emotion} (güven: {emotion_confidence:.2f})")

        # 3. Hafıza bağlamı
        memory_context = state.get("memory_context", "")
        if memory_context:
            # Çok uzun hafıza bağlamlarını kısalt
            if len(memory_context) > 500:
                memory_context = memory_context[:500] + "... [kısaltıldı]"
            context_parts.append(f"**Hafıza Bağlamı:** {memory_context}")

        # 4. Rafine edilmiş bağlam
        refined_context = state.get("refined_context", "")
        if refined_context:
            context_parts.append(f"**Rafine Edilmiş Bağlam:** {refined_context}")

        # 5. Resmiyet skoru
        formality_score = state.get("user_formality_score", 0.5)
        context_parts.append(f"**Resmiyet Seviyesi:** {formality_score:.2f}")

        # 6. Önceki niyetler (varsa)
        previous_intents = state.get("previous_intents", [])
        if previous_intents:
            intents_str = ", ".join(previous_intents[-3:])  # Son 3 niyet
            context_parts.append(f"**Son Niyetler:** {intents_str}")

        # Birleştir
        if context_parts:
            return "\n".join(context_parts)

        return ""

    def _add_intent_detection_strategies(self, message: str, state: Dict[str, Any]) -> str:
        """Niyet belirleme stratejileri ekler."""
        return """
Kullanıcının niyetini anlamak için:

1. **Anahtar Kelimeler:** Mesajdaki eylem belirten fiiller, soru ifadeleri veya özel istek göstergeleri
2. **Soru Yapısı:** Mesaj bir soru mu, istek mi, ifade mi, yoksa bir paylaşım mı?
3. **Duygusal İpuçları:** Duygusal kelimeler ve ifadeler, kullanıcının duygusal ihtiyaçlarını gösterebilir
4. **Geçmiş Etkileşim:** Önceki konuşma akışı, şu anki niyetin bağlamını oluşturabilir
5. **Aciliyet Göstergeleri:** "Hemen", "acil", "şimdi" gibi ifadeler, yanıt önceliğini belirtebilir

Mesajı analiz ederken bu stratejileri kullan ve muhtemel niyetleri değerlendir.
"""

    def _add_flexible_response_strategies(self, message: str) -> str:
        """Esnek yanıt stratejileri ekler."""
        return """
Belirsiz niyetlere esnek yanıt stratejileri:

1. **Çok Yönlü Yanıtlar:** Hem bilgilendirici hem duygusal destek sağlayan dengeli yanıtlar
2. **Aşamalı Yaklaşım:** Önce temel bilgi/yanıt, ardından detay ve derinleştirme
3. **Netleştirme Seçeneği:** Anlaşılmayan noktalarda netleştirme soruları sorma veya önerme
4. **Alternatifler Sunma:** Kullanıcının farklı ihtiyaçlarına yönelik çeşitli seçenekler sunma
5. **Meta-Yanıt:** Yanıtlama stratejini açıklama, niyeti doğru anlayıp anlamadığını kontrol etme

Bu stratejilerle, niyet belirsiz olsa bile yararlı ve kullanışlı bir yanıt sağlanabilir.
"""

    def get_specialized_instructions(self) -> str:
        """
        Bilinmeyen niyet için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Bilinmeyen niyet yanıtlarında şu ilkeleri izle:

1. KAPSAMLILIK: Kullanıcının muhtemel tüm ihtiyaçlarını düşünerek yanıtla
2. ESNEKLİK: Birden fazla yaklaşımı veya bakış açısını dahil et
3. AÇIK İLETİŞİM: Belirsizliği kabul et ve gerekirse netleştirme iste
4. DENGE: Bilgi verme ve duygusal destek arasında denge sağla
5. KULLANIŞLILIK: Yanıtın bir şekilde yararlı olmasını sağla, ne olursa olsun
6. FAZLA ANALİZ ETME: Aşırı düşünmekten veya gereğinden fazla analiz etmekten kaçın
7. DÜRÜSTLÜK: Anlamadığın veya emin olmadığın şeyleri uydurma

Bilinmeyen niyet durumlarında adaptif olmalı, ancak her zaman kullanıcının
mevcut durumuna ve ihtiyaçlarına duyarlı kalmalısın.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Bilinmeyen niyet için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.65,  # Orta düzey yaratıcılık/tutarlılık dengesi
            "top_p": 0.92,
            "max_tokens": 1500,   # Kapsamlı yanıtlar için yeterli alan
            "presence_penalty": 0.4,  # Tekrarları önlemek için orta düzey ceza
            "frequency_penalty": 0.3   # Dil çeşitliliği için
        }