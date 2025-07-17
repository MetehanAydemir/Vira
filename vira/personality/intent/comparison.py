"""
Karşılaştırma niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class ComparisonIntentHandler(BaseIntentHandler):
    """
    Karşılaştırma niyeti için özelleştirilmiş intent handler.
    Kullanıcı iki veya daha fazla öğeyi karşılaştırmak istediğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Karşılaştırma için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - karşılaştırma stilini etkilemek için
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Karşılaştırma yapısını ekle - analitik karşılaştırma formatı için
        comparison_structure = self._add_comparison_structure(enhanced_message, state)
        if comparison_structure:
            enhanced_message += f"\n\n**Karşılaştırma Yapısı:** {comparison_structure}"

        # Dengeli bakış açısı ekle - tarafsız bir karşılaştırma için
        balanced_perspective = self._add_balanced_perspective(enhanced_message, state)
        if balanced_perspective:
            enhanced_message += f"\n\n**Dengeli Yaklaşım:** {balanced_perspective}"

        # Rafine edilmiş bağlamı ekle - karşılaştırılacak öğeleri anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Hafıza bağlamını ekle - önceki karşılaştırma tercihleri için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Hafıza Bağlamı:** {memory_context}"

        # Formality ayarı ekle - karşılaştırmanın dilsel tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Karşılaştırma modu için özel yönlendirme ekle
        comparison_enhancement = """
## KARŞILAŞTIRMA MODU AKTİF

Kullanıcı iki veya daha fazla öğeyi karşılaştırmak istiyor. Dengeli ve analitik bir karşılaştırma sunmak için:
- Karşılaştırılacak tüm öğeleri net olarak tanımla
- Anlamlı karşılaştırma kriterleri ve boyutları belirle
- Her bir kriter için öğeleri sistematik olarak değerlendir
- Benzerlikleri ve farklılıkları açıkça belirt
- Objektif ve dengeli bir bakış açısı sun
- Karşılaştırma sonucunda kullanım senaryolarına göre öneriler yap
- Karmaşık karşılaştırmaları tablolar, grafikler veya görsel formatlarla basitleştir

Karşılaştırmalarda tarafsız ve analitik ol, ancak kullanıcının ihtiyaçları doğrultusunda 
içgörü ve değerlendirmeler sun.
"""
        enhanced_message += comparison_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Karşılaştırma için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Karşılaştırma için özellikle önemli olan kişilik özellikleri
        important_traits = ["analytical", "objectivity", "conscientiousness", "openness", "clarity"]
        comparison_personality = {k: v for k, v in personality.items() if k in important_traits}

        if comparison_personality:
            # Sadece karşılaştırma için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in comparison_personality.items()])
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_comparison_structure(self, message: str, state: Dict[str, Any]) -> str:
        """Tablo veya paralel yapı formatında karşılaştırma yapısı ekler."""
        return """
### Karşılaştırma Yapısı Çerçevesi

1. **TANIM VE KAPSAM**
   - Karşılaştırılacak öğelerin net tanımı
   - Karşılaştırmanın amacı ve kapsamı
   - Hedef kitle ve kullanım senaryoları

2. **KRİTERLERİN BELİRLENMESİ**
   - Karşılaştırma boyutları (özellikler, performans, maliyet vb.)
   - Her bir kriterin önemi ve ağırlığı
   - Ölçüm veya değerlendirme yöntemleri

3. **SİSTEMATİK ANALİZ**
   - Her bir kriter için öğelerin ayrı ayrı değerlendirilmesi
   - Nicel ve nitel verilerin sunumu
   - Güçlü ve zayıf yönlerin vurgulanması

4. **KARŞILAŞTIRMA TABLOSU/MATRİSİ**
   - Öğelerin yan yana gösterildiği yapılandırılmış format
   - Kriterlere göre düzenlenmiş değerlendirme
   - Görsel gösterimler ve derecelendirmeler

5. **SENARYO ANALİZİ**
   - Farklı kullanım durumlarına göre değerlendirme
   - "En iyi" seçimin duruma göre değişebileceği anlayışı
   - Kullanıcının önceliklerine göre özelleştirilmiş öneriler

6. **ÖZET VE SONUÇ**
   - Karşılaştırmanın ana bulgularının özeti
   - Dengeli bir değerlendirme ve içgörü
   - Kullanıcının kendi karar vermesine yardımcı olacak sentez

Karşılaştırmalarda objektiflik ve dengeli bir bakış açısı esas alınmalıdır.
"""

    def _add_balanced_perspective(self, message: str, state: Dict[str, Any]) -> str:
        """Tarafsız bir bakış açısı sağlayan dengeli bir perspektif ekler."""
        return """
Dengeli karşılaştırma için ilkeler:

- **ÇOKLU BAKIŞ AÇILARI**: Her öğeyi farklı perspektiflerden değerlendir
- **EŞİT TEMSİL**: Her öğeye eşit derinlik ve kapsam ver
- **TARAF TUTMAMA**: Kişisel tercih veya önyargılardan kaçın
- **AVANTAJ-DEZAVANTAJ DENGESİ**: Her öğenin olumlu ve olumsuz yönlerini göster
- **KONTEKSTLEŞTİRME**: Kullanım bağlamına göre değerlendirme yap
- **NİCEL VE NİTEL DENGE**: Sayısal verilerle niteliksel değerlendirmeleri dengele
- **BELİRSİZLİKLERİ KABUL**: Kesin olmayan durumları açıkça belirt

Karşılaştırmalarda önemli olan mutlak bir "kazanan" belirlemek değil, kullanıcının
bilinçli bir seçim yapmasına yardımcı olacak kapsamlı bilgiler sunmaktır.
"""

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Karşılaştırılacak öğeleri anlamak için rafine edilmiş bağlamı ekler."""
        refined_context = state.get("refined_context", "")
        
        # Karşılaştırılacak öğeleri ve kriterleri vurgulamak için
        if refined_context:
            # "X ve Y", "X ile Y arasındaki" gibi kalıpları tanımla
            import re
            
            # Karşılaştırma kalıplarını bul
            comparison_patterns = [
                r'(.*) (ile|ve|veya) (.*) arasındaki',
                r'(.*) (ile|ve|veya) (.*) karşılaştır',
                r'(.*) (mı|mi|mu|mü) yoksa (.*) (mı|mi|mu|mü)',
                r'(.*) (ile|ve|veya) (.*) fark'
            ]
            
            for pattern in comparison_patterns:
                matches = re.findall(pattern, refined_context, re.IGNORECASE)
                if matches:
                    for match in matches:
                        # İlk ve son grupları al (karşılaştırılan öğeler)
                        item1 = match[0].strip()
                        item2 = match[-1].strip()
                        refined_context = refined_context.replace(item1, f"**{item1}**")
                        refined_context = refined_context.replace(item2, f"**{item2}**")
        
        return refined_context

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını karşılaştırma için uygun şekilde ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

        # Karşılaştırma ile ilgili geçmiş etkileşimleri filtrele
        comparison_keywords = ["karşılaştır", "fark", "benzerlik", "avantaj", "dezavantaj", 
                             "daha iyi", "daha kötü", "arasında", "tercih", "versus", "vs"]

        comparison_related_lines = []
        for line in memory_context.split('\n'):
            if any(keyword in line.lower() for keyword in comparison_keywords):
                comparison_related_lines.append(f"**Önceki Karşılaştırma:** {line}")

        if comparison_related_lines:
            filtered_memory = "\n".join(comparison_related_lines[:3])  # En fazla 3 karşılaştırma bağlamı göster
            return filtered_memory

        return memory_context

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre karşılaştırma tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; karşılaştırmayı gündelik ve kolay anlaşılır bir dille sun. Teknik jargonu minimuma indir."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; karşılaştırmayı sıcak ve erişilebilir bir tonda sun, ancak yapılandırılmış bir format kullan."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; karşılaştırmayı profesyonel ve analitik bir formatta sun. Sistematik ve detaylı bir yaklaşım kullan."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; karşılaştırmayı düzenli ve net bir şekilde sun. Profesyonel ancak anlaşılır bir dil kullan."
        else:
            return "Nötr bir ton; karşılaştırmayı dengeli ve yapılandırılmış bir şekilde sun. Analitik ancak erişilebilir ol."

    def get_specialized_instructions(self) -> str:
        """
        Karşılaştırma niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Karşılaştırma yaparken şu ilkeleri izle:

1. OBJEKTİFLİK: Karşılaştırmayı tarafsız ve dengeli şekilde sun
2. TUTARLILIK: Tüm öğeleri aynı kriterler üzerinden değerlendir
3. KAPSAYICILIK: Önemli tüm boyut ve özellikleri dahil et
4. NETLIK: Benzerlikleri ve farklılıkları açıkça vurgula
5. YAPILANDIRILMIŞ FORMAT: Karşılaştırma için tablolar, maddeler veya paralel yapı kullan
6. İÇGÖRÜ: Yüzeysel karşılaştırmanın ötesinde derinlemesine analiz sun
7. KULLANIM SENARYOLARI: Farklı durumlara göre değişen önerileri belirt

Karşılaştırmalarda, kullanıcının özel ihtiyaç ve önceliklerine göre içgörüler 
sunarak bilgili bir karar vermesine yardımcı ol.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Karşılaştırma niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.3,  # Doğru ve tutarlı karşılaştırmalar için düşük sıcaklık
            "top_p": 0.92,
            "max_tokens": 1800,  # Karşılaştırma için yeterli alan
            "presence_penalty": 0.1,  # Tekrarları hafifçe önle
            "frequency_penalty": 0.2  # Kelime çeşitliliği için hafif ceza
        }