#!/usr/bin/env python3
"""
LangGraph tabanlı Vira AI iş akışı
"""
from langgraph.graph import StateGraph, END

from vira.graph.state import ViraState
from vira.graph.nodes.process_input import process_input_node
from vira.graph.nodes.handle_omega import handle_omega_node
from vira.graph.nodes.intent_classifier import intent_classifier_node
from vira.graph.nodes.retrieve_memory import retrieve_memory_node
from vira.graph.nodes.prepare_prompt import prepare_prompt_node
from vira.graph.nodes.generate_response import generate_response_node
from vira.graph.nodes.save_memory import save_memory_node

# --- Kenar Karar Fonksiyonları ---
def should_continue(state: ViraState):
    """
    Akışın omega komutuna mı yoksa standart sohbet akışına mı devam edeceğine karar verir.
    """
    if state["is_omega_command"]:
        return "handle_omega"
    else:
        return "retrieve_memory"

# --- Graf Oluşturma ---
workflow = StateGraph(ViraState)

# 1. Düğümleri Tanımla
workflow.add_node("process_input", process_input_node)
workflow.add_node("intent_classifier", intent_classifier_node)
workflow.add_node("handle_omega", handle_omega_node)
workflow.add_node("retrieve_memory", retrieve_memory_node)
workflow.add_node("prepare_prompt", prepare_prompt_node)
workflow.add_node("generate_response", generate_response_node)
workflow.add_node("save_memory", save_memory_node)

# 2. Graf Akışını (Kenarları) Tanımla
# Giriş noktası
workflow.set_entry_point("process_input")

# Yeni akış: process_input -> intent_classifier
workflow.add_edge("process_input", "intent_classifier")

# Koşullu kenar: intent_classifier'dan sonra Omega kontrolü
workflow.add_conditional_edges(
    "intent_classifier",  # Değiştirilen kısım (process_input yerine)
    should_continue,
    {
        "handle_omega": "handle_omega",
        "retrieve_memory": "retrieve_memory",
    },
)

# Standart sohbet akışı
workflow.add_edge("retrieve_memory", "prepare_prompt")
workflow.add_edge("prepare_prompt", "generate_response")
workflow.add_edge("generate_response", "save_memory")

# Bitiş noktaları
workflow.add_edge("handle_omega", END)
workflow.add_edge("save_memory", END)

# 3. Grafı Derle
app = workflow.compile()

print("Vira LangGraph uygulaması başarıyla derlendi!")