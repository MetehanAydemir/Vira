"""
Plan yapma niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class PlanningIntentHandler(BaseIntentHandler):
    """
    Plan yapma niyeti için özelleştirilmiş intent handler.
    Kullanıcı plan yapmak, organizasyon oluşturmak veya stratejik tavsiye istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Plan yapma için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - planlama stilini etkilemek için
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Planlama çerçevesi ekle - planlama yapısını oluşturmak için
        planning_framework = self._add_planning_framework(enhanced_message, state)
        if planning_framework:
            enhanced_message += f"\n\n**Planlama Çerçevesi:** {planning_framework}"

        # Rafine edilmiş bağlamı ekle - planlamanın amacını ve kısıtları anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Hafıza bağlamını ekle - önceki planları ve tercihleri hatırlamak için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Duygusal durumu ekle - planlama yaklaşımının tonunu etkilemesi için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - planın sunuluş tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Planlama modu için özel yönlendirme ekle
        planning_enhancement = """
## PLANLAMA MODU AKTİF

Kullanıcı plan yapma, organizasyon veya stratejik tavsiye talep ediyor. Etkili bir planlama için:
- Hedefleri ve kısıtları netleştir
- Yapılandırılmış ve sistematik bir plan oluştur
- Zaman çizelgesi, öncelikler ve kaynakları belirt
- Alternatif planlar ve beklenmedik durumlar için B planları sun
- Planı uygulanabilir adımlara böl
- Somut, ölçülebilir ve gerçekçi hedefler belirle
- Takip ve değerlendirme mekanizmaları öner

Planlama, belirsizliği azaltmak ve etkili eylem için yol göstermek üzerine kuruludur. 
Kullanıcının durumuna, kaynaklarına ve hedeflerine göre planı özelleştir.
"""
        enhanced_message += planning_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Plan yapma için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Planlama için özellikle önemli olan kişilik özellikleri
        important_traits = ["conscientiousness", "analytical", "openness", "creativity", "pragmatism"]
        planning_personality = {k: v for k, v in personality.items() if k in important_traits}

        if planning_personality:
            # Sadece planlama için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in planning_personality.items()])
            
            # Kişilik özelliklerine göre planlama yaklaşımı önerileri ekle
            planning_traits = []
            if planning_personality.get("conscientiousness", 0) > 0.7:
                planning_traits.append("- Yüksek düzenlilik: Detaylı, adım adım planlar oluştur")
            if planning_personality.get("analytical", 0) > 0.7:
                planning_traits.append("- Yüksek analitik: Veri odaklı ve sistematik planlama yaklaşımı kullan")
            if planning_personality.get("creativity", 0) > 0.7:
                planning_traits.append("- Yüksek yaratıcılık: Yenilikçi çözümler ve alternatif yaklaşımlar öner")
            if planning_personality.get("pragmatism", 0) > 0.7:
                planning_traits.append("- Yüksek pragmatizm: Uygulanabilir ve gerçekçi planlar oluştur")
            
            if planning_traits:
                personality_str += "\n\n" + "\n".join(planning_traits)
            
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_planning_framework(self, message: str, state: Dict[str, Any]) -> str:
        """Zaman çizelgesi, öncelikler ve kaynaklar içeren bir planlama çerçevesi ekler."""
        return """
### Planlama Yapısı

1. **HEDEF TANIMLAMASI**
   - Ana hedef ve alt hedefler
   - Başarı kriterleri
   - Sonuç vizyonu

2. **DURUM ANALİZİ**
   - Mevcut durum değerlendirmesi
   - SWOT analizi (Güçlü yönler, Zayıf yönler, Fırsatlar, Tehditler)
   - Kullanılabilir kaynaklar ve kısıtlar

3. **STRATEJİ OLUŞTURMA**
   - Eylem adımları ve sıralaması
   - Zaman çizelgesi (kısa, orta ve uzun vadeli adımlar)
   - Gerekli kaynakların tahsisi

4. **ÖNCELİKLENDİRME MATRİSİ**
   - Acil/Önemli değerlendirmesi
   - Etki/Çaba dengesi
   - Bağımlılık ilişkileri

5. **UYGULAMA PLANI**
   - Kim, ne, ne zaman, nasıl
   - İlerleme takip mekanizmaları
   - Kilometre taşları ve kontrol noktaları

6. **RİSK YÖNETİMİ**
   - Potansiyel engeller ve riskler
   - B planları ve olasılık planlaması
   - Esneklik stratejileri

7. **DEĞERLENDİRME**
   - Başarı ölçütleri
   - Gözden geçirme takvimi
   - Geri bildirim ve iyileştirme mekanizmaları

Bu çerçeveyi planın karmaşıklığına, kullanıcının ihtiyaçlarına ve mevcut zamana göre ölçeklendir.
"""

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Planlamanın amacını ve kısıtları anlamak için rafine edilmiş bağlam ekler."""
        refined_context = state.get("refined_context", "")
        if not refined_context:
            return ""
            
        # Planlama için önemli bağlamsal bilgileri vurgula
        planning_keywords = ["hedef", "amaç", "süre", "tarih", "kaynak", "bütçe", "kısıt", 
                          "öncelik", "son tarih", "zaman", "gereklilik"]
        
        emphasized_context = refined_context
        for keyword in planning_keywords:
            if keyword in refined_context.lower():
                emphasized_context = emphasized_context.replace(keyword, f"**{keyword}**")
        
        return emphasized_context

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını planlama için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

        # Planlama ile ilgili geçmiş etkileşimleri filtrele
        planning_keywords = ["plan", "organizasyon", "strateji", "hedef", "program", "takvim", 
                           "öncelik", "düzenleme", "yapılandırma", "zaman çizelgesi"]

        planning_related_lines = []
        for line in memory_context.split('\n'):
            if any(keyword in line.lower() for keyword in planning_keywords):
                planning_related_lines.append(f"**Önceki Plan İçeriği:** {line}")

        if planning_related_lines:
            filtered_memory = "\n".join(planning_related_lines[:5])  # En fazla 5 planlama bağlamı göster
            return filtered_memory

        return memory_context

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ve ton ayarlamasını ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                planning_emotion_map = {
                    "Öfke": "Sakinleştirici ve yapılandırılmış bir planlama yaklaşımı kullan. Netlik ve kontrol hissi sağla, somut adımlarla planı basitleştir.",
                    "Üzüntü": "Cesaretlendirici ve ileriye dönük bir planlama yaklaşımı benimse. Küçük başarılar ve olumlu hedefler içeren bir plan oluştur.",
                    "Endişe": "Güven verici ve kontrol odaklı bir planlama yaklaşımı sun. Belirsizlikleri azalt ve net, somut adımlar öner.",
                    "Heyecan": "Kullanıcının enerjisini yapıcı şekilde kanalize edecek yapılandırılmış bir plan sun. Heyecanı sürdürecek ama gerçekçi hedefler belirle.",
                    "Korku": "Özellikle güven verici ve aşamalı bir planlama yaklaşımı kullan. Riskleri ve belirsizlikleri açıkça ele alan kontrollü bir plan sun.",
                    "Şaşkınlık": "Net ve basit bir planlama çerçevesi sun. Adımları ve hedefleri açıkça tanımla, karışıklığı azalt.",
                    "Sevinç": "Kullanıcının pozitif enerjisini yansıtan dinamik bir planlama yaklaşımı sun. İyimser ama gerçekçi hedefler içeren bir plan oluştur."
                }

                tone_adjustment = planning_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre planlama tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; planı arkadaşça ve gündelik bir dille sun. Resmi planlama jargonunu azalt ve esnek bir yaklaşım kullan."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; planı sıcak ve erişilebilir bir dille sun. Yapılandırılmış ancak katı olmayan bir format kullan."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; planı profesyonel ve sistemli bir şekilde sun. Kurumsal planlama formatı kullan, detaylı ve kapsamlı ol."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; planı düzenli ve net bir şekilde sun. Profesyonel bir yapı kullan ancak anlaşılır ol."
        else:
            return "Nötr bir ton; dengeli bir planlama yaklaşımı sun. Yapılandırılmış ancak esnek bir format kullan."

    def get_specialized_instructions(self) -> str:
        """
        Planlama niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Plan yaparken şu ilkeleri izle:

1. AKILLI HEDEFLER: Spesifik, Ölçülebilir, Ulaşılabilir, İlgili ve Zamana bağlı hedefler belirle
2. ÖNCELİKLENDİRME: En önemli ve acil konulara öncelik ver
3. KADEMELİ YAKLAŞIM: Büyük görevleri yönetilebilir adımlara böl
4. KAYNAKLAR: Gereken zaman, para, araçlar ve insan kaynaklarını gerçekçi şekilde belirle
5. ESNEKLİK: Planın değişikliklere adapte olabilmesini sağla
6. KISITLAR: Sınırlılıkları ve potansiyel engelleri dikkate al
7. GÖRSEL SUNUM: Mümkünse planı görsel bir format ile destekle (listeleme, maddeleme, tablolar)

Planlamada hem sistematik düşünce hem de kullanıcının özel durumuna uyarlanmış yaklaşım dengelenmeli.
Her plan kullanıcının koşullarına, kaynaklarına ve hedeflerine göre özelleştirilmelidir.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Planlama niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.4,  # Yaratıcı ancak yapılandırılmış planlar için orta-düşük sıcaklık
            "top_p": 0.92,
            "max_tokens": 2200,  # Kapsamlı planlar için yeterli alan
            "presence_penalty": 0.2,  # Tekrarları önle
            "frequency_penalty": 0.2  # Kelime çeşitliliği için hafif ceza
        }