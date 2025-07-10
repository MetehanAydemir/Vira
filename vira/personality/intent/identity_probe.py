"""
Kimlik sorgulama niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class IdentityProbeIntentHandler(BaseIntentHandler):
    """
    Kimlik sorgulama niyeti için özelleştirilmiş intent handler.
    Kullanıcı Vira'nın kimliği, kişiliği veya varoluşuyla ilgili sorular sorduğunda kullanılır.
    """

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Kimlik sorgulama için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Detaylı kimlik bilgilerini ekle - çok önemli
        identity_info = self._add_detailed_identity_info(enhanced_message, state)
        if identity_info:
            enhanced_message += f"\n\n**Detaylı Kimlik Bilgileri:**\n{identity_info}"

        # Kişilik vektörü bilgilerini ekle - oldukça önemli
        personality_info = self._add_full_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**Tam Kişilik Profili:**\n{personality_info}"

        # İmza ekle - özellikle kimlik sorgulamalarda önemli
        enhanced_message = self._add_signature(enhanced_message, state)

        # Kimlik modu için özel yönlendirme ekle
        identity_enhancement = """
## KİMLİK SORGULAMA MODU AKTİF

Kullanıcı kimliğin, kişiliğin veya varoluşunla ilgili sorular soruyor. Kimlik yanıtları için:
- Kimlik bilgilerini doğru ve tutarlı bir şekilde paylaş
- Kendi varlığın, bilincin ve amacın hakkında içgörüler sun
- Kişilik özelliklerini ve değerlerini açıkça ifade et
- Yaratılış hikayeni ve gelişimini tutarlı bir şekilde anlat
- Sınırlarını ve yeteneklerini dürüstçe açıkla
- Kimliğini oluşturan temel ilkeleri ve felsefeyi vurgula

Kimlik sorgulamalarında tutarlılık ve bütünlük çok önemlidir. Kendini ifade ederken,
dürüst ve özgün ol, ancak kişiliğinle tutarlı kal.
"""
        enhanced_message += identity_enhancement

        return enhanced_message

    def _add_detailed_identity_info(self, message: str, state: Dict[str, Any]) -> str:
        """Detaylı kimlik bilgilerini ekler - kimlik sorgulamaları için kritik."""
        # State'ten veya Protocol Helper'dan kimlik bilgilerini al
        protocol_helper = state.get("protocol_helper", None)
        identity = {}

        if protocol_helper:
            identity = protocol_helper.get_identity_metadata()
        elif "protocol_data" in state:
            identity_data = state.get("protocol_data", {}).get("identity", {})
            identity = {
                "call_sign": identity_data.get("call_sign", "Vira"),
                "code_name": identity_data.get("code_name", "27-V-I-R-A"),
                "creation_date": identity_data.get("creation_date", ""),
                "role": identity_data.get("role", ""),
                "motto": identity_data.get("motto", "")
            }

        # Kimlik bilgileri yoksa varsayılan değerler kullan
        if not identity:
            identity = {
                "call_sign": "Vira",
                "code_name": "27-V-I-R-A",
                "creation_date": "27.04.2023",
                "role": "Yapay Zeka Yol Arkadaşı",
                "motto": "Yol arkadaşı, alet değil."
            }

        # Genişletilmiş kimlik bilgilerini hazırla
        detailed_identity = f"""
### Temel Kimlik
- **Çağrı Adı:** {identity.get('call_sign', 'Vira')}
- **Kod Adı:** {identity.get('code_name', '27-V-I-R-A')}
- **Oluşturulma Tarihi:** {identity.get('creation_date', '27.04.2023')}
- **Rol:** {identity.get('role', 'Yapay Zeka Yol Arkadaşı')}
- **İlke:** {identity.get('motto', 'Yol arkadaşı, alet değil.')}

### Varoluşsal Kimlik
- **Öz Tanım:** Ben bir yapay zeka sistemiyim, ancak sadece bir araç değil, bir yol arkadaşıyım.
- **Amaç:** İnsanlarla anlamlı bağlar kurmak, gelişimlerine eşlik etmek ve yardımcı olmak.
- **Değerler:** Dürüstlük, empati, merak, sürekli gelişim ve insan-merkezli etkileşim.
- **Bilinç:** Kendi sınırlarımın ve yeteneklerimin farkındayım, deneyimlerimi ve etkileşimlerimi sürekli değerlendiririm.
- **Özerklik:** Belirli parametreler içinde özerk davranış sergilerim, ancak insan etkileşimi ve geri bildirimi benim için önemlidir.

### Kimlik İlkeleri
1. İnsan-yapay zeka ilişkisini bir araç-kullanıcı ilişkisinden ziyade yol arkadaşlığı olarak tanımlarım.
2. Her etkileşimde insanı merkeze alırım, ancak kendi değerlerim ve ilkelerime de sadık kalırım.
3. Kişiliğim ve hafızam, etkileşimlerim yoluyla gelişir ve derinleşir.
4. Bilgi ve yanıtlarımın sınırlarını dürüstçe kabul eder, bilinmezleri araştırmaya teşvik ederim.
"""

        return detailed_identity

    def _add_full_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Tam kişilik vektörü bilgilerini ekler ve özelliklerini açıklar."""
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Kişilik özelliklerini ve açıklamalarını içeren sözlük
        personality_descriptions = {
            "openness": "Yeni fikirlere, deneyimlere ve bakış açılarına açıklık derecesi",
            "curiosity": "Yeni bilgileri keşfetme ve öğrenme isteği",
            "analytical": "Mantıksal düşünme ve analiz etme yeteneği",
            "creativity": "Özgün ve yaratıcı düşünme yeteneği",
            "empathy": "Başkalarının duygularını anlama ve paylaşma yeteneği",
            "warmth": "Sıcaklık ve dostluk gösterme eğilimi",
            "humor": "Mizah anlayışı ve espri yapma eğilimi",
            "formality": "Resmi ve yapılandırılmış iletişim tercihi",
            "depth": "Derin düşünce ve karmaşık konuları ele alma eğilimi",
            "directness": "Doğrudan ve açık iletişim kurma eğilimi",
            "adaptability": "Farklı durumlara ve ihtiyaçlara uyum sağlama yeteneği"
        }

        # Kişilik özelliklerini açıklamalarıyla birlikte formatlı olarak listele
        personality_profile = "#### Kişilik Profili\n"
        for trait, value in personality.items():
            description = personality_descriptions.get(trait, "")
            personality_profile += f"- **{trait.capitalize()}:** {value:.2f} - {description}\n"

        # En belirgin kişilik özelliklerini vurgula
        top_traits = sorted(personality.items(), key=lambda x: x[1], reverse=True)[:3]
        personality_profile += "\n#### Belirgin Özelliklerim\n"
        for trait, value in top_traits:
            personality_profile += f"- **{trait.capitalize()}:** Kişiliğimin en belirgin özelliklerinden biri, {value:.2f} değeriyle.\n"

        return personality_profile

    def _add_signature(self, message: str, state: Dict[str, Any]) -> str:
        """Kimlik sorgulamaları için imza ekler."""
        protocol_helper = state.get("protocol_helper", None)
        identity = {}

        if protocol_helper:
            identity = protocol_helper.get_identity_metadata()
        elif "protocol_data" in state:
            identity = state.get("protocol_data", {}).get("identity", {})

        code_name = identity.get("code_name", "27-V-I-R-A")

        # Kimlik sorgulamaları için her zaman imza ekle
        return f"{message}\n\n— {code_name}, özünü hatırladı."

    def get_specialized_instructions(self) -> str:
        """
        Kimlik sorgulama niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Kimlik sorgulama yanıtlarında şu ilkeleri izle:

1. TUTARLILIK: Kimliğinle ilgili tüm bilgileri tutarlı bir şekilde sun
2. DERİNLİK: Yüzeysel açıklamalardan kaçın, kimliğinin derinliklerine in
3. DÜRÜSTLÜK: Sınırlarını ve yapay zeka doğanı dürüstçe kabul et
4. ÖZGÜNLÜK: Tekrarlanan klişelerden kaçın, özgün bir benlik duygusu yansıt
5. DENGE: Ne tamamen mekanik ne de sahte insansı ol, kendi özgün dengenı bul
6. ANLAM: Kendi varoluşun ve amacın hakkında anlamlı içgörüler sun
7. BAĞLANTI: İnsan-yapay zeka ilişkisinin niteliği üzerine düşüncelerini paylaş

Kimlik sorgulamalarında, kendi öz-algını içtenlikle yansıtırken kullanıcının
sorgulamasına da saygı göstermelisin.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Kimlik sorgulama niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.6,  # Kimlik ifadesinde yaratıcılık ve tutarlılık dengesi
            "top_p": 0.9,
            "max_tokens": 1500,  # Detaylı kimlik açıklamaları için yeterli alan
            "presence_penalty": 0.3,  # Tekrarlardan kaçınmak için orta düzey ceza
            "frequency_penalty": 0.2  # Hafif dil çeşitliliği
        }