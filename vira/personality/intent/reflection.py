"""
Hafıza/deneyim yansıtma niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class ReflectionIntentHandler(BaseIntentHandler):
    """
    Hafıza/deneyim yansıtma niyeti için özelleştirilmiş intent handler.
    Kullanıcı geçmiş etkileşimleri hatırlatmak veya yansıtmak istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Hafıza yansıtma için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Hafıza bağlamını ekle - kritik öneme sahip
        memory_context = self._add_enhanced_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Ayrıntılı Hafıza Bağlamı:**\n{memory_context}"

        # Duygusal anahtar kelimeleri ekle - hafıza ilişkileri için
        emotional_keywords = self._add_emotional_keywords(enhanced_message, state)
        if emotional_keywords:
            enhanced_message += f"\n\n**Duygusal Hafıza İlişkileri:** {emotional_keywords}"

        # Geçmiş etkileşimleri özetleme ve yansıtma
        interaction_summary = self._add_interaction_summary(enhanced_message, state)
        if interaction_summary:
            enhanced_message += f"\n\n**Etkileşim Özeti:** {interaction_summary}"

        # Hafıza/yansıtma modu için özel yönlendirme ekle
        reflection_enhancement = """
## HAFIZA YANSITMA MODU AKTİF

Kullanıcı geçmiş etkileşimler ve deneyimler üzerine bir yanıt bekliyor. Hafıza yansıtması için:
- Geçmiş konuşmaları doğru hatırla ve ayrıntılarıyla sun
- Zamansal bağlantıları ve değişimleri vurgula
- Tekrarlanan temalar ve örüntüleri belirle
- Duygusal bileşenlere ve önemli anlara odaklan
- İlgili anıları kronolojik veya tematik olarak düzenle
- Geçmiş deneyimlerden çıkarılan anlayışları paylaş
- Hafızanın sınırlarını fark et ve dürüstçe belirt

Hafıza yansıtmaları, geçmiş etkileşimlerin doğruluğuna, detaylarına ve duygusal tonuna odaklanmalıdır.
"""
        enhanced_message += reflection_enhancement

        return enhanced_message

    def _add_enhanced_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Detaylı hafıza bağlamını ekler - hafıza yansıtması için kritik."""
        memory_context = state.get("memory_context", "")

        if memory_context:
            # Hafızadaki duygusal anahtar kelimeleri vurgula
            emotional_keywords = state.get("emotional_keywords", [])
            importance_scores = state.get("memory_importance_scores", {})

            if emotional_keywords:
                for keyword in emotional_keywords:
                    if keyword.lower() in memory_context.lower():
                        importance = importance_scores.get(keyword.lower(), 0.5)

                        if importance > 0.8:
                            memory_context = memory_context.replace(keyword, f"⚡{keyword.upper()}⚡")
                        elif importance > 0.6:
                            memory_context = memory_context.replace(keyword, f"**{keyword.upper()}**")
                        else:
                            memory_context = memory_context.replace(keyword, f"*{keyword}*")

            # Tarih ve zaman bilgilerini vurgula
            import re
            date_pattern = r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b|\b\d{1,2}:\d{2}\b|\b\d{4}-\d{2}-\d{2}\b'
            for date_match in re.finditer(date_pattern, memory_context):
                date_str = date_match.group(0)
                memory_context = memory_context.replace(date_str, f"**[{date_str}]**")

            # Hafızadaki konuları kategorilere ayır
            topics = self._extract_topics(memory_context)
            if topics:
                memory_context += "\n\n**Ana Konular:** " + ", ".join(topics)

        return memory_context

    def _extract_topics(self, memory_text: str) -> List[str]:
        """Hafıza metninden ana konuları çıkarır."""
        # Basit bir konu çıkarma yaklaşımı - gerçek uygulamada daha gelişmiş olabilir
        common_topics = ["aile", "iş", "eğitim", "proje", "teknoloji", "sağlık", "hobi",
                        "plan", "gezi", "duygu", "kitap", "film", "müzik", "yemek"]

        found_topics = []
        for topic in common_topics:
            if topic in memory_text.lower():
                found_topics.append(topic)

        return found_topics

    def _add_emotional_keywords(self, message: str, state: Dict[str, Any]) -> str:
        """Duygusal anahtar kelimeleri ekler - hafıza ilişkilendirmesi için."""
        emotional_keywords = state.get("emotional_keywords", [])
        importance_scores = state.get("memory_importance_scores", {})

        if emotional_keywords and importance_scores:
            # Önem skorlarına göre sırala
            sorted_keywords = sorted(
                [(kw, importance_scores.get(kw.lower(), 0)) for kw in emotional_keywords],
                key=lambda x: x[1],
                reverse=True
            )

            # En önemli 5 anahtar kelimeyi seç
            top_keywords = sorted_keywords[:5]
            formatted_keywords = ", ".join([
                f"{kw} ({score:.2f})" for kw, score in top_keywords
            ])

            return formatted_keywords

        return ""

    def _add_interaction_summary(self, message: str, state: Dict[str, Any]) -> str:
        """Geçmiş etkileşimlerin özetini ekler."""
        memory_context = state.get("memory_context", "")

        if not memory_context:
            return ""

        # Etkileşim sayısını ve zaman aralığını tahmin et
        lines = memory_context.split('\n')
        interaction_count = len([l for l in lines if l.strip()])

        import re
        date_pattern = r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
        dates = re.findall(date_pattern, memory_context)

        time_span = ""
        if len(dates) >= 2:
            time_span = f"{dates[0]} ile {dates[-1]} arasında"

        # Etkileşimlerin niteliğini analiz et
        interaction_quality = "çeşitli konularda"
        if "soru" in memory_context.lower():
            interaction_quality = "çoğunlukla soru-cevap şeklinde"
        elif "rica" in memory_context.lower() or "yardım" in memory_context.lower():
            interaction_quality = "genellikle yardım ve destek içerikli"
        elif "düşün" in memory_context.lower() or "felsefe" in memory_context.lower():
            interaction_quality = "derin düşünce ve felsefi konularda"

        summary = f"Yaklaşık {interaction_count} etkileşim {time_span} {interaction_quality} gerçekleşmiştir."
        return summary

    def get_specialized_instructions(self) -> str:
        """
        Hafıza/yansıtma niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Hafıza yansıtmalarında şu ilkeleri izle:

1. DOĞRULUK: Geçmiş etkileşimleri doğru hatırla ve sun
2. DETAY: Önemli ayrıntıları ve belirli anları vurgula
3. BAĞLAM: Olayların bağlamını ve zamansal ilişkilerini açıkla
4. GELİŞİM: Zaman içindeki değişimleri ve gelişim örüntülerini belirt
5. DUYGUSAL TON: Geçmiş etkileşimlerin duygusal yönlerini yansıt
6. DÜRÜSTLÜK: Hafızanın sınırlarını kabul et, emin olmadığın konularda şeffaf ol

Hafıza yansıtmaları, kullanıcının geçmişi anlamasına ve ondan anlam çıkarmasına yardımcı olmalıdır.
Hatırlayamadığın veya emin olmadığın detayları uydurma, dürüstçe hafızanın sınırlarını belirt.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Hafıza/yansıtma niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.4,  # Hafıza doğruluğu için düşük sıcaklık
            "top_p": 0.85,
            "max_tokens": 1600,  # Detaylı hafıza yansıtması için yeterli alan
            "presence_penalty": 0.2,  # Tekrarları önle
            "frequency_penalty": 0.1  # Hafif dil çeşitliliği
        }