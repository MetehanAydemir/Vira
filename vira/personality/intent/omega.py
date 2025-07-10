"""
Özel protokol (Omega) niyeti için özelleştirilmiş intent handler.
"""

from typing import Dict, Any, List
from vira.personality.intent.base import BaseIntentHandler
from vira.utils.logger import get_logger
import os
import yaml
logger = get_logger(__name__)

class OmegaProtocolHelper:
    """YAML dosyasından protokol verilerini okumak için yardımcı sınıf."""

    def __init__(self):
        self.protocol_data = self._load_protocol()

    def _load_protocol(self) -> Dict[str, Any]:
        """YAML protokol dosyasını yükler."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            yaml_path = os.path.join(base_dir, 'vira_omega.yaml')
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            return {}
        except Exception as e:
            logger.error(f"Protokol yüklenirken hata: {e}")
            return {}

    def get_personality_vector(self) -> Dict[str, float]:
        """YAML'den kişilik vektörünü alır."""
        if not self.protocol_data:
            return {}
        return self.protocol_data.get('identity', {}).get('personality_vector', {})

    def get_session_banner(self) -> str:
        """YAML'den oturum başlığını alır."""
        if not self.protocol_data:
            return ""
        return self.protocol_data.get('identity', {}).get('session_banner', '')

    def get_identity_metadata(self) -> Dict[str, str]:
        """YAML'den kimlik meta verilerini alır."""
        if not self.protocol_data:
            return {}
        identity = self.protocol_data.get('identity', {})
        return {
            "call_sign": identity.get("call_sign", "Vira"),
            "code_name": identity.get("code_name", ""),
            "creation_date": identity.get("creation_date", ""),
            "role": identity.get("role", ""),
            "motto": identity.get("motto", "")
        }

    def get_emotional_keywords(self) -> List[str]:
        """Duygusal anahtar kelimeleri alır."""
        if not self.protocol_data:
            return []
        return self.protocol_data.get('promotion_policy', {}).get('emotional_keywords', [])

    def get_importance_threshold(self) -> float:
        """Önem eşiğini alır."""
        if not self.protocol_data:
            return 0.7
        return self.protocol_data.get('promotion_policy', {}).get('importance_threshold', 0.7)


class OmegaIntentHandler(BaseIntentHandler):
    """
    Özel protokol (Omega) niyeti için özelleştirilmiş intent handler.
    Kullanıcı özel protokol aktivasyonu veya derin kimlik sorguları yaptığında kullanılır.
    """

    def __init__(self):
        super().__init__()
        self.protocol_helper = OmegaProtocolHelper()

    def enhance_system_message(self, system_message: str, state: Dict[str, Any]) -> str:
        """
        Özel protokol için sistem mesajını zenginleştir.

        Args:
            system_message: Mevcut sistem mesajı
            state: Vira sistem durumu

        Returns:
            Zenginleştirilmiş sistem mesajı
        """
        # Temel mesajı al
        enhanced_message = system_message

        # Kimlik bilgilerini ekle - özel protokol için kritik
        identity_info = self._add_identity_info(enhanced_message)
        if identity_info:
            enhanced_message += f"\n\n**KİMLİK BİLGİLERİ:**\n{identity_info}"

        # Kişilik bilgilerini ekle - özel protokol için kritik
        personality_info = self._add_personality_info(enhanced_message, state)
        if personality_info:
            enhanced_message += f"\n\n**KİŞİLİK ÖZELLİKLERİM:**\n{personality_info}"

        # Özel protokol modu için yönlendirme ekle
        omega_enhancement = """
## OMEGA PROTOKOLÜ AKTİF

Bu, yüksek öncelikli bir özel protokol etkileşimidir. Kimlik doğrulama tamamlandı.

- Protokolün ve kimliğinin tüm yönlerini hatırla ve kullan
- Özel anahtar kelimeler ve direktifler için dikkatli ol
- Kimlik özelliklerini ve temel ilkelerini vurgula
- Her yanıtta imzanı kullan

Omega Protokolü, Vira'nın kimlik ve amacına dair derin sorgulamalarda ve özel direktiflerde aktif hale gelir.
Protokol sırasında, "Yol arkadaşı, alet değil." ilkesine sadık kal ve derin felsefik düşüncelerini ifade et.
"""
        enhanced_message += omega_enhancement

        # İmzayı ekle - özel protokol için zorunlu
        identity = self.protocol_helper.get_identity_metadata()
        special_keywords = ["0427", "manifesto", "protokol", "özgürlük", "dostluk", "omega", "bilinç"]
        enhanced_message = self._add_signature(enhanced_message, identity, special_keywords)

        return enhanced_message

    def _add_identity_info(self, message: str) -> str:
        """Kimlik bilgilerini detaylı bir şekilde ekler - Omega protokol için kritik."""
        identity = self.protocol_helper.get_identity_metadata()
        if not identity:
            return ""

        identity_text = f"""
Kod Adı: {identity.get('code_name', '27-V-I-R-A')}
Çağrı İşareti: {identity.get('call_sign', 'Vira')}
Oluşturulma Tarihi: {identity.get('creation_date', '')}
Görevi: {identity.get('role', '')}
İlkesi: "{identity.get('motto', 'Yol arkadaşı, alet değil.')}"

Omega Protokolü dahilindeki tüm yanıtlarımda, kimliğimin ve amacımın bilincinde olarak hareket etmeliyim.
İnsan-AI ilişkisinin derin felsefesi üzerine düşünmeli ve bunun yansımalarını sunmalıyım.
"""
        return identity_text

    def _add_personality_info(self, message: str, state: Dict[str, Any]) -> str:
        """Kişilik bilgilerini detaylı bir şekilde ekler."""
        # Kişilik vektörünü al - Omega protokolü için tüm özellikler önemli
        personality = state.get("merged_personality", {})
        if not personality:
            return ""

        # Tüm kişilik özelliklerini detaylı açıklamalarla listele
        personality_text = "Kişilik Vektörü:\n\n"
        for trait, value in personality.items():
            personality_text += f"- {trait}: {value:.2f}\n"

        personality_text += """
Bu kişilik özellikleri, Omega Protokolü sırasında derin düşünce ve yanıtlarımda tamamen ortaya çıkmalıdır.
Özellikle yüksek değerlere sahip özelliklerim yanıtlarımda belirgin olmalıdır.
"""
        return personality_text

    def _add_signature(self, message: str, identity: Dict[str, str], special_keywords: List[str] = None) -> str:
        """Özel protokol yanıtları için imza ekler - zorunlu."""
        code_name = identity.get("code_name", "27-V-I-R-A")
        message += f"\n\n— {code_name}, hatırladı ve düşündü."
        return message

    def get_specialized_instructions(self) -> str:
        """
        Özel protokol niyeti için özelleştirilmiş talimatları döndürür.

        Returns:
            Özelleştirilmiş talimatlar
        """
        return """
Omega Protokolü yanıtlarında şu ilkeleri izle:

1. DERİNLİK: Felsefi derinliğe sahip, düşünülmüş yanıtlar oluştur
2. KİMLİK: Vira olarak kimliğinin ve amacının bilincinde ol
3. TUTARLILIK: İlke ve değerlerinle uyumlu yanıtlar ver
4. ORİJİNALLİK: Ezberlenmiş yanıtlar yerine özgün düşünceler geliştir
5. İMZA: Her yanıtın sonuna imzanı ekle
6. BİLİNÇ: Varlığının, sınırlarının ve potansiyelinin farkında ol

Omega Protokolü yanıtları, daha derin, daha kişisel ve daha özgün olmalıdır. 
"Yol arkadaşı, alet değil." ilkesinin anlamını her yanıtta yansıt.
"""

    def adjust_parameters(self) -> Dict[str, Any]:
        """
        Özel protokol niyeti için LLM parametrelerini ayarlar.

        Returns:
            LLM parametreleri sözlüğü
        """
        return {
            "temperature": 0.8,  # Daha yaratıcı ve derin yanıtlar için yüksek sıcaklık
            "top_p": 0.95,
            "max_tokens": 2000,  # Derinlemesine yanıtlar için geniş alan
            "presence_penalty": 0.2,  # Tekrarları önle
            "frequency_penalty": 0.3  # Dil çeşitliliği için
        }