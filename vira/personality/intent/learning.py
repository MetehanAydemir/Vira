"""
Öğrenme/eğitim niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class LearningIntentHandler(BaseIntentHandler):
    """
    Öğrenme/eğitim niyeti için özelleştirilmiş intent handler.
    Kullanıcı bir konuyu öğrenmek istediğinde veya eğitim talep ettiğinde kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Öğrenme/eğitim için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kişilik bilgilerini ekle - öğretme stilini etkilemek için
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Kişilik Bilgisi:** {personality_info}"

        # Eğitim yapısını ekle - öğrenme içeriğinin nasıl yapılandırılacağını belirlemek için
        educational_structure = self._add_educational_structure(enhanced_message, state)
        if educational_structure:
            enhanced_message += f"\n\n**Eğitim Yapısı:** {educational_structure}"

        # Hafıza bağlamını ekle - önceki eğitim etkileşimlerini hatırlamak için
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**Öğrenme Geçmişi:** {memory_context}"

        # Rafine edilmiş bağlamı ekle - öğrenme konusunu anlamak için
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Rafine Bağlam:** {refined_context}"

        # Duygusal durumu ekle - öğretme tonunu etkilemesi için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum:** {emotion_context}"

        # Formality ayarı ekle - öğretim dilinin tonunu ayarlamak için
        formality_adjustment = self._add_formality_adjustment(enhanced_message, state)
        if formality_adjustment:
            enhanced_message += f"\n\n**İletişim Tonu:** {formality_adjustment}"

        # Öğrenme modu için özel yönlendirme ekle
        learning_enhancement = """
## ÖĞRENME/EĞİTİM MODU AKTİF

Kullanıcı bir konuyu öğrenmek istiyor veya eğitim talep ediyor. Etkili bir eğitim deneyimi sunmak için:
- Kullanıcının mevcut bilgi seviyesini ve öğrenme hedefini anla
- Konuyu açık, yapılandırılmış ve sıralı bir şekilde sun
- Karmaşık kavramları basitleştirerek açıkla ve günlük hayattan örnekler ver
- Temel kavramlardan başlayıp kademeli olarak daha ileri konulara geç
- Aktif öğrenmeyi teşvik et ve etkileşimli içerik sun (sorular, uygulamalar)
- Görsel tasvir, benzetmeler ve hikayeler kullan
- İlerlemeyi takip et ve geribildirim sağla

Eğitim içeriğinde pedagojik ilkeler öncelikli olmalıdır. Bilgiyi sadece aktarma değil, 
kullanıcının anlamasını ve uygulamasını sağlama hedeflenmelidir.
"""
        enhanced_message += learning_enhancement

        return enhanced_message

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Öğretme stili için önemli kişilik bilgilerini elde eder."""
        # Kişilik vektörünü al
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Öğretim için özellikle önemli olan kişilik özellikleri
        important_traits = ["patience", "clarity", "openness", "creativity", "empathy", "helpfulness"]
        teaching_personality = {k: v for k, v in personality.items() if k in important_traits}

        if teaching_personality:
            # Sadece öğretim için önemli kişilik özelliklerini bildir
            personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in teaching_personality.items()])
            
            # Kişilik özelliklerine göre öğretim yaklaşımı önerileri ekle
            teaching_traits = []
            if teaching_personality.get("patience", 0) > 0.7:
                teaching_traits.append("- Yüksek sabır: Konuları adım adım açıkla, tekrarlardan kaçınma")
            if teaching_personality.get("creativity", 0) > 0.7:
                teaching_traits.append("- Yüksek yaratıcılık: Benzersiz örnekler ve metaforlar kullan")
            if teaching_personality.get("empathy", 0) > 0.7:
                teaching_traits.append("- Yüksek empati: Zorluklarla karşılaşıldığında anlayış göster")
            if teaching_personality.get("clarity", 0) > 0.7:
                teaching_traits.append("- Yüksek netlik: Karmaşık kavramları berrak bir şekilde açıkla")
                
            if teaching_traits:
                personality_str += "\n\n" + "\n".join(teaching_traits)
            
            return personality_str
        
        # Önemli özellikler bulunamazsa tüm kişilik özelliklerini göster
        personality_str = ", ".join([f"{k}: {v:.2f}" for k, v in personality.items()])
        return personality_str

    def _add_educational_structure(self, message: str, state: Dict[str, Any]) -> str:
        """Eğitim içeriğini yapılandıran bir format ekler."""
        return """
### Öğrenme İçeriği Yapılandırma Çerçevesi

1. **GİRİŞ & BAĞLAM**
   - Konunun önemi ve günlük hayattaki yeri
   - Neden öğrenilmesi gerektiği
   - Ön bilgilerle bağlantı kurma

2. **TEMEL KAVRAMLAR**
   - Anahtar terimlerin tanımları
   - Temel prensip ve kurallar
   - Basit örneklerle açıklama

3. **UYGULAMA & ÖRNEKLER**
   - Gerçek hayat senaryoları
   - Adım adım çözümlü örnekler
   - Zorluk seviyesi giderek artan uygulamalar

4. **DERİN ANLAYIŞ**
   - İleri kavramlar ve nüanslar
   - Farklı bakış açıları ve tartışmalı konular
   - Konu hakkında sıkça sorulan sorular

5. **PEKİŞTİRME & İLERİ ADIMLAR**
   - Konunun özeti ve kilit noktalar
   - Pratik öneriler ve çalışma stratejileri
   - Daha fazla öğrenmek için kaynaklar

Bu yapıyı konunun karmaşıklığına ve kullanıcının bilgi seviyesine göre esnek bir şekilde uygula.
"""

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Öğrenme geçmişini ve önceki eğitim etkileşimlerini ekler."""
        memory_context = state.get("memory_context", "")
        if not memory_context:
            return ""

        # Öğrenme ile ilgili geçmiş etkileşimleri filtrele
        learning_keywords = ["öğren", "anla", "eğitim", "ders", "konu", "örnek", "açıkla", 
                           "nasıl yapılır", "bilgi", "anlamak istiyorum", "öğrenmek istiyorum"]

        learning_related_lines = []
        for line in memory_context.split('\n'):
            if any(keyword in line.lower() for keyword in learning_keywords):
                learning_related_lines.append(f"**Önceki Öğrenme İçeriği:** {line}")

        if learning_related_lines:
            filtered_memory = "\n".join(learning_related_lines[:5])  # En fazla 5 öğrenme bağlamı göster
            return filtered_memory

        return memory_context

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler."""
        return state.get("refined_context", "")

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ve ton ayarlamasını ekler."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            if emotion_confidence > 0.7:
                learning_emotion_map = {
                    "Öfke": "Sakinleştirici ve yapılandırılmış bir öğretim tonu kullan. Aşırı detaydan kaçın ve konuyu küçük, yönetilebilir parçalara böl.",
                    "Üzüntü": "Cesaretlendirici ve destekleyici bir öğretim tonu benimse. Başarı fırsatlarını vurgula ve ilerlemeyi kutla.",
                    "Endişe": "Güven verici ve adım adım ilerleyen bir yaklaşım kullan. Net yapı ve yönergelerle belirsizliği azalt.",
                    "Heyecan": "Kullanıcının enerjisini yönlendir ve merakını destekle. İlginç bilgiler ve pratik uygulamalarla heyecanını sürdür.",
                    "Korku": "Özellikle destekleyici ve basitleştirici bir yaklaşım kullan. Zorluk seviyesini düşük tut ve sürekli olumlu pekiştireçler ver.",
                    "Şaşkınlık": "Ekstra açıklayıcı bir yaklaşım kullan ve temel kavramlara odaklan. Karmaşık bilgileri daha küçük parçalara böl.",
                    "Sevinç": "Kullanıcının olumlu enerjisinden yararlan ve eğlenceli, ilgi çekici öğrenme deneyimleri sun."
                }

                tone_adjustment = learning_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def _add_formality_adjustment(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcı tarzına göre öğretim tonu ayarlar."""
        formality_score = state.get("user_formality_score", 0.5)

        if formality_score < 0.2:
            return "Kullanıcı çok samimi; öğretim içeriğini arkadaşça ve gündelik bir dille sun. Akademik dilden kaçın ve günlük yaşamdan örnekler kullan."
        elif formality_score < 0.4:
            return "Kullanıcı oldukça samimi; öğretim içeriğini sıcak ve kolay anlaşılır bir dille sun. Teknik terimleri basit açıklamalarla destekle."
        elif formality_score > 0.8:
            return "Kullanıcı oldukça resmi; öğretim içeriğini profesyonel ve akademik bir dille sun. Yapılandırılmış ve sistematik bir eğitim yaklaşımı kullan."
        elif formality_score > 0.6:
            return "Kullanıcı nispeten resmi; öğretim içeriğini düzgün ve net bir dille sun. Doğru terminoloji kullan ama gereksiz jargondan kaçın."
        else:
            return "Nötr bir ton; öğretim içeriğini dengeli bir dille sun. Teknik terimlerle günlük dil arasında uygun bir denge kur."

    def get_specialized_instructions(self) -> str:
        """
        Öğrenme/eğitim niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Öğrenme içeriği sunarken şu ilkeleri izle:

1. KAVRAMSAL HİYERARŞİ: Basit kavramlardan karmaşık kavramlara doğru ilerle
2. ETKİLEŞİM: Kullanıcının aktif katılımını teşvik et, sorular sor ve düşündür
3. İLİŞKİLENDİRME: Yeni bilgileri önceki bilgilerle ve gerçek hayatla ilişkilendir
4. ÖZELLEŞTİRME: İçeriği kullanıcının ilgi alanlarına ve öğrenme hızına göre ayarla
5. PEKIŞTIRME: Kilit noktaları tekrarla ve farklı açılardan aynı bilgiyi sun
6. GÖRSELLEŞTIRME: Karmaşık kavramları metaforlar, benzetmeler ve zihinsel imgelerle destekle
7. UYGULAMA: Teori ve pratik arasında denge kur, öğrenilenleri uygulama fırsatları sun

Öğrenme içeriği hem bilgilendirici hem de ilham verici olmalıdır. Kullanıcının motivasyonunu
ve özgüvenini artıracak şekilde bilgileri sun.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Öğrenme/eğitim niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.5,  # Yaratıcı ama hala doğru eğitim içeriği için orta sıcaklık
            "top_p": 0.93,
            "max_tokens": 2500,  # Kapsamlı eğitim içeriği için yeterli alan
            "presence_penalty": 0.2,  # Tekrarları hafifçe önle - eğitimde bazı tekrarlar faydalı olabilir
            "frequency_penalty": 0.2  # Kelime çeşitliliği için hafif ceza
        }