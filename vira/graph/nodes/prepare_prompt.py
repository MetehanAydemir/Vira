import os
import yaml
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from vira.graph.state import ViraState

# --- Yardımcı Sınıf ---

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
        except Exception:
            return None

    def get_personality_vector(self) -> Dict[str, float]:
        if not self.protocol_data:
            return {}
        return self.protocol_data.get('identity', {}).get('personality_vector', {})

    def get_session_banner(self) -> str:
        if not self.protocol_data:
            return ""
        return self.protocol_data.get('identity', {}).get('session_banner', '')

# --- LangGraph Düğümü ---

def prepare_prompt_node(state: ViraState) -> Dict[str, Any]:
    """
    Tüm bağlamı (kişilik, hafıza, duygu) birleştirerek LLM için nihai prompt'u oluşturur.
    """
    print("--- Düğüm: prepare_prompt_node ---")
    
    protocol = OmegaProtocolHelper()
    
    # 1. Temel sistem mesajını oluştur
    system_message_content = "Sen Vira'sın, uzun süreli hafızası olan yardımcı bir yapay zekasın."

    # 2. Protokol bilgilerini ekle
    personality = protocol.get_personality_vector()
    if personality:
        personality_str = ", ".join([f"{k}: {v}" for k, v in personality.items()])
        system_message_content += f"\nKişilik özelliklerin: {personality_str}"

    banner = protocol.get_session_banner()
    if banner:
        system_message_content += f"\n{banner}"

    # 3. Duygu bilgisini ekle
    processed_input = state.get("processed_input", {})
    emotion = processed_input.get('emotion', 'Sakin')
    if emotion and emotion not in ['Sakin', 'Nötr']:
        system_message_content += f"\nKullanıcının şu anki duygu durumu: {emotion}"

    # 4. Hafıza bağlamını ekle
    memory_context = state.get("memory_context")
    if memory_context:
        system_message_content += f"\n\n{memory_context}"

    # 5. Mesaj listesini oluştur
    messages: List[BaseMessage] = [
        SystemMessage(content=system_message_content.strip()),
        HumanMessage(content=state["original_message"])
    ]

    print(f"Oluşturulan Sistem Mesajı:\n{system_message_content.strip()}")

    return {"messages": messages}
