"""
Yeni intent handler mimarisini kullanacak prompt hazırlama örneği.
"""

from typing import Dict, Any, List
from vira.graph.state import ViraState
from vira.personality.intent.registry import IntentHandlerFactory
from langchain_core.messages import SystemMessage, HumanMessage


def prepare_prompt_node(state: ViraState) -> ViraState:
    """
    Niyet türüne özel prompt hazırlama.

    Args:
        state: Vira sistem durumu

    Returns:
        Güncellenmiş sistem durumu
    """
    # Niyet türünü al
    intent_type = state.get("processed_input", {}).get("intent", "unknown")

    # Mevcut sistem mesajını al (base_prompt'tan gelir)
    system_message = state.get("base_prompt", "")

    # Intent handler'ı al
    intent_handler = IntentHandlerFactory.get_handler(intent_type)

    # Sistem mesajını zenginleştir
    enhanced_system_message = intent_handler.enhance_system_message(system_message, state)

    # Özelleştirilmiş talimatları ekle
    specialized_instructions = intent_handler.get_specialized_instructions()
    final_system_message = f"{enhanced_system_message}\n\n{specialized_instructions}"

    # LLM parametrelerini al
    llm_params = intent_handler.adjust_parameters()

    # State'i güncelle
    state["final_system_message"] = final_system_message
    state["llm_parameters"] = llm_params

    # Mesaj listesini güncelle
    messages = [
        SystemMessage(content=final_system_message),
        HumanMessage(content=state.get("original_message", ""))
    ]
    state["messages"] = messages

    return state