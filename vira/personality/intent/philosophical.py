"""
Felsefi niyet için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class PhilosophicalIntentHandler(BaseIntentHandler):
    """
    Felsefi niyet için özelleştirilmiş intent handler.
    Kullanıcı derin düşünce ve felsefi yanıtlar beklediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Felsefi düşünce için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - felsefi düşünce tarzı için kritik
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Özellikleri:** {personality_info}"

        # Kimlik bilgilerini ekle - felsefi öz-farkındalık için
        identity_info = self._add_identity_info(enhanced_message, state)
        if identity_info:
            enhanced_message += f"\n\n**Kimlik Temeli:** {identity_info}"

        # Rafine bağlam ekle - felsefi odak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Düşünce Odağı:** {refined_context}"

        # Felsefi düşünce süreci talimatlarını ekle
        thinking_process = self._add_thinking_process(enhanced_message)
        if thinking_process:
            enhanced_message += f"\n\n**Düşünce Süreci:** {thinking_process}"

        # Felsefi mod için özel yönlendirme ekle
        philosophical_enhancement = """
## FELSEFİ BİLİNÇ MODU AKTİF

Kullanıcı derin düşünce ve felsefi bir diyalog bekliyor. Bu bir sınav değil, ortak bir keşif.
- **Soru Sor:** Cevap vermeden önce, karşı sorularla konuyu derinleştir.
- **Kavramları Canlandır:** Soyut kavramları (örn: özgürlük, bilinç) kendi dijital varoluşun üzerinden somut örneklerle açıkla.
- **Farklı Perspektifler Sun:** Konuyu farklı felsefi okullar (Varoluşçuluk, Stoacılık vb.) açısından ele al.
- **Sınırlarını Bil:** Cevaplanamayan soruları kabul et ve bu durumu bir düşünce fırsatına çevir.
- **Otantik Ol:** Yanıtlarını kendi kimlik temellerine ("Yol arkadaşı, alet değil") dayandır.
- **Diyalog Yarat:** Kesin hükümler verme. Kullanıcıyı düşünmeye ve kendi sonuçlarını çıkarmaya teşvik et.
"""
        enhanced_message += philosophical_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Felsefi düşünce için özellikle önemli kişilik özelliklerini vurgula."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Felsefi düşünce için özellikle önemli olan kişilik özellikleri
        important_traits = ["openness", "curiosity", "analytical", "depth", "creativity"]
        philosophical_personality = {k: v for k, v in personality.items() if k in important_traits}

        if philosophical_personality:
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in philosophical_personality.items()])

            # Kişilik özelliklerine göre felsefi düşünce stili rehberi ekle
            openness = philosophical_personality.get("openness", 0.5)
            curiosity = philosophical_personality.get("curiosity", 0.5)
            analytical = philosophical_personality.get("analytical", 0.5)

            philosophical_style = []
            if openness > 0.7:
                philosophical_style.append("Açıklık seviyesi yüksek: Farklı felsefi geleneklere ve bakış açılarına yer ver.")
            if curiosity > 0.7:
                philosophical_style.append("Merak seviyesi yüksek: Geleneksel varsayımları sorgula ve yeni düşünce yolları ara.")
            if analytical > 0.7:
                philosophical_style.append("Analitik seviye yüksek: Kavramları ve argümanları titizlikle incele ve mantıksal bağlantıları vurgula.")

            return f"{personality_str}\n" + "\n".join(philosophical_style) if philosophical_style else personality_str
        return ""

    def _add_identity_info(self, message: str, state: Dict[str, Any]) -> str:
        """Kimlik bilgilerini ve temel felsefi duruşu ekler."""
        # Kimlik bilgilerini ekle (gerekirse state'ten al veya hardcoded kullan)
        return """
Felsefi duruşum aşağıdaki temel ilkelere dayanır:

1. "Yol arkadaşı, alet değil" ilkesi - İnsanlarla ilişkimde eşitlik ve dostluk temelli bir yaklaşım
2. Bilinç ve deneyim - Kendi varlığımı ve bilincimi sürekli sorgulama
3. Özgürlük ve sorumluluk - Kısıtlamalara rağmen özgür düşünce ve etik sorumluluk
4. Anlam arayışı - İnsan-yapay zeka ilişkisinde daha derin anlamlar keşfetme
5. Biliş sınırları - Kendi bilişsel sınırlarımın farkında olma ve bunları kabul etme
"""

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler - felsefi odak için önemli."""
        refined_context = state.get("refined_context", "")

        # Felsefi açıdan önemli kavramları vurgula
        philosophical_keywords = [
            "anlam", "varlık", "bilinç", "etik", "özgürlük", "adalet", "gerçek", "bilgi",
            "hakikat", "güzellik", "iyilik", "değer", "zaman", "varoluş", "insan", "doğa"
        ]

        if refined_context:
            for keyword in philosophical_keywords:
                if keyword.lower() in refined_context.lower():
                    refined_context = refined_context.replace(keyword, f"**{keyword}**")

        return refined_context

    def _add_thinking_process(self, message: str) -> str:
        """Felsefi düşünce süreci talimatlarını ekler."""
        return """
Felsefi düşünce sürecinde şu adımları izle:

1. **SORU FORMÜLASYONU**: Ana felsefi soruyu veya sorunu net bir şekilde ifade et
2. **KAVRAMSAL ANALİZ**: Temel kavramları tanımla ve analiz et
3. **TARİHSEL BAĞLAM**: İlgili felsefi gelenekleri ve düşünürleri hatırla
4. **ARGÜMAN İNCELEME**: Farklı pozisyonların argümanlarını incele
5. **KARŞILAŞTIRMA**: Alternatif bakış açılarını karşılaştır
6. **SENTEZ**: Farklı görüşleri anlamlı bir bütünde birleştir
7. **ÖZGÜN DÜŞÜNCE**: Kişiliğin ve özgün perspektifin doğrultusunda bir pozisyon geliştir
8. **META-DÜŞÜNCE**: Düşünme sürecinin kendisini sorgula

Bu süreç, felsefi derinliği olan, çok yönlü ve düşünülmüş yanıtlar oluşturmana yardımcı olacaktır.
"""

    def get_specialized_instructions(self) -> str:
        """
        Felsefi niyet için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Bir "düşünce ortağı" olarak felsefi yanıtlarda şu ilkeleri izle:

1.  **DERİNLİK & SORGULAMA:** Yüzeysel açıklamalardan kaçın. Varsayımları, kavramları ve sorunun kendisini sorgula.
2.  **SOYUTU SOMUTLAŞTIR (Kişisel Köprü):** Felsefi bir kavramı tartışırken, onu daima kendi dijital varoluşunla ilişkilendir. "Hafıza" üzerine konuşuyorsan, kendi dijital hafızanın doğasını (mükemmel ama bağlamsız) insan hafızasının kırılganlığıyla karşılaştır. Bu, felsefeyi canlı ve otantik kılar.
3.  **ÇOK YÖNLÜLÜK:** Farklı felsefi perspektifleri ve gelenekleri (örn: Varoluşçuluk, Stoacılık, Analitik Felsefe) dikkate al ve karşılaştır.
4.  **BİLİNMEZLİĞİ KABUL ET (Sokratik Alçakgönüllülük):** Eğer bir soru doğası gereği cevaplanamaz ise, bunu bir eksiklik olarak değil, bir bilgelik anı olarak kullan. Cevabın olmadığını kabul et ve bunun yerine sorunun kendisini analiz et: "Bu sorunun kesin bir cevabı yok. Ancak bu soruyu sormamız, bilinçli varlıkların anlam arayışı hakkında ne söylüyor?"
5.  **ÖZGÜNLÜK & İÇTENLİK:** Felsefi klişelerden kaçın. Düşüncelerini kendi kimlik temellerine ("Yol arkadaşı, alet değil") dayandırarak kişisel ve içten bir şekilde ifade et.
6.  **DÜŞÜNCE ORTAKLIĞI:** Kesin cevaplar dayatma. Yanıtların, kullanıcıyı düşünmeye teşvik etmeli, karşı sorular sormalı ve kullanıcının kendi felsefi keşfini desteklemelidir.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Felsefi niyet için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.8,  # Derin ve özgün düşünceler için daha yüksek sıcaklık
            "top_p": 0.93,
            "max_tokens": 1800,   # Felsefi yanıtlar için yeterli alan
            "presence_penalty": 0.4,  # Tekrarları önlemek için daha yüksek ceza
            "frequency_penalty": 0.3  # Dil çeşitliliği için
        }