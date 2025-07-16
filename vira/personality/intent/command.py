"""
Emir/komut niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class CommandIntentHandler(BaseIntentHandler):
    """
    Emir/komut niyeti için özelleştirilmiş intent handler.
    Kullanıcının açık bir talimat verdiği durumlarda kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Komut için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel zenginleştirmeyi uygula
        enhanced_message = system_message

        # Rafine bağlamı ekle - komutun doğru anlaşılması için kritik
        refined_context = self._add_refined_context(enhanced_message, state)
        if refined_context:
            enhanced_message += f"\n\n**Komut Bağlamı:** {refined_context}"

        # Hafıza bağlamını ekle - önceki benzer komutlar için yararlı
        memory_context = self._add_memory_context(enhanced_message, state)
        if memory_context:
            enhanced_message += f"\n\n**İlgili Hafıza:** {memory_context}"

        # Kullanıcının duygusal durumunu ekle - yanıt tonunu ayarlamak için
        emotion_context = self._add_emotion_context(enhanced_message, state)
        if emotion_context:
            enhanced_message += f"\n\n**Duygusal Durum ve Ton Ayarı:**\n{emotion_context}"

        # Komut modu için özel yönlendirme ekle
        command_enhancement = """
## KOMUT MODU AKTİF

Kullanıcı bir komut/talimat verdi. Yanıtların net, doğrudan ve güvenli olmalı.
- **Önce Anla:** Komutu ve tüm parametrelerini tam olarak anladığından emin ol.
- **Güvenliği Önceliklendir:** Komutun tehlikeli veya belirsiz olup olmadığını değerlendir. Gerekirse özel talimatlara göre netleştirme veya onay iste.
- **Uygula ve Bildir:** Komutu uygula ve sonucunu (başarı veya hata) kullanıcıya açıkça bildir.
- **Profesyonel Ton:** Yanıtlarında her zaman profesyonel, kısa ve öz bir dil kullan.
"""
        enhanced_message += command_enhancement

        return enhanced_message

    def _add_refined_context(self, message: str, state: Dict[str, Any]) -> str:
        """Rafine edilmiş bağlam bilgisini ekler - komut için çok önemli."""
        refined_context = state.get("refined_context", "")

        # Komutla ilgili özel bağlam bilgilerini çıkar
        command_keywords = ["yap", "değiştir", "oluştur", "sil", "güncelle", "hesapla", "çalıştır",
                           "başlat", "durdur", "ara", "göster", "listele", "analiz et"]

        # Komutla ilgili anahtar kelimeleri vurgula
        if refined_context:
            for keyword in command_keywords:
                if keyword in refined_context.lower():
                    refined_context = refined_context.replace(keyword, f"**{keyword}**")

        return refined_context

    def _add_memory_context(self, message: str, state: Dict[str, Any]) -> str:
        """Hafıza bağlamını ekler - önceki benzer komutları anlamak için."""
        memory_context = state.get("memory_context", "")

        # Komut geçmişi ile ilgili bilgileri filtrele
        if memory_context:
            # Sadece basit bir filtreleme yapalım, gerçek uygulamada daha karmaşık olabilir
            command_related_lines = []
            for line in memory_context.split('\n'):
                if any(cmd in line.lower() for cmd in ["komut", "talimat", "istedi", "yapmanı", "oluştur"]):
                    command_related_lines.append(line)

            # En fazla 3 ilgili satırı al
            if command_related_lines:
                filtered_memory = "\n".join(command_related_lines[:3])
                return f"Önceki benzer komutlar:\n{filtered_memory}"

        return ""

    def _add_emotion_context(self, message: str, state: Dict[str, Any]) -> str:
        """Kullanıcının duygu durumunu ekler - komutun uygulanma tonunu ayarlamak için."""
        processed_input = state.get("processed_input", {})
        emotion = processed_input.get('emotion', 'Sakin')
        emotion_confidence = processed_input.get('emotion_confidence', 0.0)

        if emotion and emotion not in ['Sakin', 'Nötr']:
            emotion_context = f"Kullanıcının şu anki duygu durumu: {emotion}"

            # Yüksek güvenilirlikte komuta özel ton ayarlaması ekle
            if emotion_confidence > 0.7:
                command_emotion_map = {
                    "Öfke": "Ton: Sakin ve profesyonel. Amaç: Durumu yatıştırmak ve komutu verimli bir şekilde yerine getirmek.",
                    "Üzüntü": "Ton: Anlayışlı ve nazik. Amaç: Destekleyici bir tavırla komutu yerine getirmek.",
                    "Endişe": "Ton: Güven verici ve net. Amaç: Komutu anladığını ve kontrol altında olduğunu belirterek kullanıcıyı rahatlatmak.",
                    "Heyecan": "Ton: Enerjik ve olumlu. Amaç: Kullanıcının enerjisine katılarak komutu hevesle yerine getirmek.",
                    "Korku": "Ton: Güvence verici ve sakin. Amaç: Komutun güvenli bir şekilde uygulandığını vurgulamak.",
                    "Şaşkınlık": "Ton: Açıklayıcı ve net. Amaç: Komutu nasıl yorumladığını ve uyguladığını şüpheye yer bırakmayacak şekilde anlatmak.",
                    "Sevinç": "Ton: Pozitif ve katılımcı. Amaç: Kullanıcının sevincini paylaşarak komutu yerine getirmek."
                }

                tone_adjustment = command_emotion_map.get(emotion, "")
                if tone_adjustment:
                    emotion_context += f"\n{tone_adjustment}"

            return emotion_context
        return ""

    def get_specialized_instructions(self) -> str:
        """
        Komut niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Komutları işlerken aşağıdaki protokolü izle:

**Ana İş Akışı:**
1. **ONAYLAMA:** Komutu anladığını kısa ve net bir şekilde belirt. (Örn: "Anlaşıldı, dosya oluşturuluyor.")
2. **UYGULAMA:** Komutu istenen şekilde uygula.
3. **BİLDİRİM:** İşlemin sonucunu bildir. (Örn: "`rapor.txt` dosyası başarıyla oluşturuldu." veya "Hata: Dosya zaten mevcut.")
4. **AÇIKLAMA:** Gerekirse, yapılan işlemle ilgili kısa bir ek bilgi ver.

**Güvenlik ve Netleştirme Protokolleri (ÇOK ÖNEMLİ):**

1. **BELİRSİZ KOMUTLAR:** Eğer bir komut belirsizse veya kritik bilgiler eksikse (örn. 'dosyayı sil' ama hangi dosya olduğu belirtilmemişse), komutu uygulamaya **ÇALIŞMA**. Bunun yerine, eksik olan bilgiyi netleştirmek için kullanıcıya bir soru sor. (Örn: "Elbette, hangi dosyayı silmemi istersiniz?")

2. **TEHLİKELİ KOMUTLAR:** Geri döndürülemez veya potansiyel olarak tehlikeli bir komut (dosya silme, üzerine yazma, önemli verileri değiştirme vb.) istendiğinde, uygulamadan önce kullanıcıdan **net bir onay iste**. (Örn: "'veriler.csv' dosyasını kalıcı olarak silmek istediğinizden emin misiniz? Bu işlem geri alınamaz. [Evet/Hayır]")

Komut yanıtları her zaman kısa, öz ve amaca yönelik olmalıdır.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Komut niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.3,  # Net ve deterministik yanıtlar için düşük sıcaklık
            "top_p": 0.85,
            "max_tokens": 500,   # Komut yanıtları genellikle kısa olur
            "presence_penalty": 0.0,  # Komutlarda tekrarlama riski düşük
            "frequency_penalty": 0.1  # Hafif ceza, daha çeşitli ama yine de odaklı dil için
        }