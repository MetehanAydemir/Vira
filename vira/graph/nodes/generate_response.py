import yaml
from openai import OpenAI  # <<< DEĞİŞİKLİK: AzureOpenAI yerine OpenAI kullanılıyor
from typing import Dict, Any
import os

from vira.graph.state import ViraState
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)


# --- DEĞİŞİKLİK: Yardımcı fonksiyon OpenRouter istemcisini kullanacak şekilde güncellendi ---
def get_custom_chat_client() -> OpenAI:
    """OpenRouter gibi özel bir OpenAI uyumlu API için istemci başlatır."""
    return OpenAI(
        api_key=settings.CUSTOM_CHAT_API_KEY,
        base_url=settings.CUSTOM_CHAT_API_ENDPOINT,
    )


class OmegaProtocolHelper:
    """YAML dosyasından protokol verilerini okumak için yardımcı sınıf."""

    def __init__(self):
        self.protocol_data = self._load_protocol()

    def _load_protocol(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            yaml_path = os.path.join(base_dir, 'vira_omega.yaml')
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            return None
        except Exception as e:
            logger.error(f"Protokol yüklenirken hata oluştu: {e}")
            return None

    def get_summary_info(self) -> str:
        if not self.protocol_data:
            return ""
        try:
            protocol_id = self.protocol_data.get('meta', {}).get('id', 'Bilinmeyen Protokol')
            version = self.protocol_data.get('meta', {}).get('spec_version', 'v?.??')
            call_sign = self.protocol_data.get('identity', {}).get('call_sign', 'Vira')
            motto = self.protocol_data.get('identity', {}).get('motto', '')
            return f"\n\n[{protocol_id} v{version}] - {call_sign}: {motto}"
        except Exception as e:
            logger.error(f"Protokol bilgisi alınırken hata oluştu: {e}")
            return ""


# --- LangGraph Düğümü ---

def generate_response_node(state: ViraState) -> Dict[str, Any]:
    """
    Hazırlanan prompt ile OpenRouter API'sini çağırır ve bir yanıt üretir.
    """
    logger.info("--- Düğüm: generate_response_node ---")

    messages = state["messages"]
    if not messages:
        return {"response": "Üzgünüm, işleyecek bir mesaj bulamadım."}

    try:
        # --- DEĞİŞİKLİK: İstemci ve model adı OpenRouter ayarlarından alınıyor ---
        client = get_custom_chat_client()
        model_name = settings.CUSTOM_CHAT_MODEL_NAME

        logger.debug(f"Kullanılan model: {model_name}")

        openai_messages = []
        for msg in messages:
            role = "user" if msg.type == "human" else msg.type
            openai_messages.append({"role": role, "content": msg.content})

        logger.debug(f"OpenAI mesajları: {openai_messages}")

        response_stream = client.chat.completions.create(
            model=model_name,
            messages=openai_messages,
            stream=False
        )

        ai_response = response_stream.choices[0].message.content

        protocol = OmegaProtocolHelper()
        protocol_info = protocol.get_summary_info()
        if protocol_info:
            ai_response += protocol_info

        logger.info(f"Yanıt üretildi: {ai_response[:50]}...")
        return {"response": ai_response.strip()}

    except Exception as e:
        logger.error(f"Yanıt üretilirken hata oluştu: {e}", exc_info=True)
        return {"response": "Üzgünüm, bir hata oluştu ve yanıt üretemedim."}