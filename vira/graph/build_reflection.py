"""
Self-reflection sistemi için graf düğümlerini mevcut workflow'a entegre eder.
"""

from typing import Dict, Any, List, Optional
import langchain
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from datetime import datetime, timedelta
import json
import logging
from vira.graph.state import ViraState
from vira.db.repository import UserRepository, MemoryRepository
from vira.db.reflection_repository import ReflectionRepository
from vira.utils.logger import get_logger

# Temel workflow için gereken düğümleri import edelim
from vira.graph.nodes.process_input import process_input_node
from vira.graph.nodes.handle_omega import handle_omega_node
from vira.graph.nodes.intent_classifier import intent_classifier_node
from vira.graph.nodes.retrieve_memory import retrieve_memory_node
from vira.graph.nodes.context_refiner_node import context_refiner_node
from vira.graph.nodes.prepare_prompt import prepare_prompt_node
from vira.graph.nodes.generate_response import generate_response_node
from vira.graph.nodes.memory_relevance import memory_relevance_node
from vira.graph.nodes.save_memory import save_memory_node
from vira.graph.nodes.build_mental_model import build_mental_model_node

logger = get_logger(__name__)

# Repository örneklerini oluştur
user_repository = UserRepository()
memory_repository = MemoryRepository()

reflection_repository = ReflectionRepository()

def create_reflection_enhanced_workflow() -> StateGraph:
    """
    LangGraph tabanlı VIRA akışına self-reflection yetenekleri eklenmiş enhanced workflow oluşturur

    Returns:
        StateGraph: Enhanced workflow grafiği
    """
    # Temel grafiği yeniden oluşturuyoruz (build.py'dan kopyalandı)
    workflow = StateGraph(ViraState)

    # --- Kenar Karar Fonksiyonları ---
    def should_continue(state: ViraState):
        """
        Akışın omega komutuna mı yoksa standart sohbet akışına mı devam edeceğine karar verir.
        """
        if state["is_omega_command"]:
            return "handle_omega"
        else:
            return "retrieve_memory"

    # 1. Düğümleri Tanımla
    workflow.add_node("process_input", process_input_node)
    workflow.add_node("build_mental_model", build_mental_model_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("handle_omega", handle_omega_node)
    workflow.add_node("retrieve_memory", retrieve_memory_node)
    workflow.add_node("context_refiner", context_refiner_node)
    workflow.add_node("prepare_prompt", prepare_prompt_node)
    workflow.add_node("generate_response", generate_response_node)
    workflow.add_node("memory_relevance", memory_relevance_node)
    workflow.add_node("save_memory", save_memory_node)

    # 2. Graf Akışını (Kenarları) Tanımla
    # Giriş noktası
    workflow.set_entry_point("process_input")

    # Yeni akış: process_input -> build_mental_model -> intent_classifier
    workflow.add_edge("process_input", "build_mental_model")
    workflow.add_edge("build_mental_model", "intent_classifier")

    # Koşullu kenar: intent_classifier'dan sonra Omega kontrolü
    workflow.add_conditional_edges(
        "intent_classifier",
        should_continue,
        {
            "handle_omega": "handle_omega",
            "retrieve_memory": "retrieve_memory",
        },
    )

    # Self-reflection koşullarını kontrol et
    def should_trigger_reflection(state: ViraState) -> str:
        """
        Self-reflection tetiklenecek mi kontrol et

        Args:
            state: Mevcut durum

        Returns:
            str: "trigger_reflection" veya "continue"
        """
        # Burada tetikleme koşullarını kontrol et:
        # 1. Duygusal bir tepki var mı?
        # 2. Özel bir konudan bahsediliyor mu?
        # 3. Kullanıcı çok aktif mi?

        # Örnek basit bir koşul (gerçek implementasyonda daha karmaşık mantık kullanılabilir)
        if "processed_input" in state and state["processed_input"].get("emotion_score", 0) > 0.8:
            return "trigger_reflection"

        # Şimdilik varsayılan olarak reflection'ı tetikleme
        return "continue"

    # Self-reflection node'u
    def process_reflection(state: ViraState) -> ViraState:
        """
        Self-reflection işlemini gerçekleştir

        Args:
            state: Mevcut durum

        Returns:
            ViraState: Güncellenen durum
        """
        try:
            user_id = state["user_id"]

            # Kullanıcının geçmiş etkileşimlerini getir
            # Burada daha kapsamlı bir analiz yapabilirsiniz

            # Reflection verileri oluştur
            reflection_data = {
                "timestamp": datetime.now().isoformat(),
                "trigger_type": "emotion_based",
                "user_id": user_id,
                "interaction_count": 10,  # Örnek değer
                "analysis": {
                    "patterns": ["Kullanıcı genellikle akşam saatlerinde aktif"],
                    "topics": ["iş", "proje", "zaman yönetimi"],
                    "emotions": ["stres", "endişe"]
                }
            }

            # State'i güncelle
            state["reflection_triggered"] = True
            state["reflection_data"] = reflection_data

            # Reflection repository ile veritabanına kaydet
            reflection_repository.create_reflection_session(
                user_id=user_id,
                reflection_type="realtime",
                trigger_reasons=["emotion_based"],
                analysis_results=reflection_data["analysis"]
            )

            # Log
            logger.info(f"Self-reflection triggered for user {user_id}")

            return state
        except Exception as e:
            logger.error(f"Self-reflection processing error: {str(e)}", exc_info=True)
            # Hata durumunda orijinal state'i döndür
            return state

    # Grafiğe self-reflection düğümünü ekle
    workflow.add_node("reflection", process_reflection)

    # Koşullu geçişi tanımla - build_mental_model'den sonra, intent_classifier'dan önce
    workflow.add_conditional_edges(
        "build_mental_model",  # Önceki: process_input
        should_trigger_reflection,
        {
            "trigger_reflection": "reflection",  # Self-reflection tetiklenirse reflection node'una git
            "continue": "intent_classifier"  # Değilse normal akışa devam et
        }
    )

    # Reflection node'undan sonra normal akışa dön
    workflow.add_edge("reflection", "intent_classifier")

    # Standart sohbet akışı
    workflow.add_edge("retrieve_memory", "context_refiner")
    workflow.add_edge("context_refiner", "prepare_prompt")
    workflow.add_edge("prepare_prompt", "generate_response")
    workflow.add_edge("generate_response", "memory_relevance")
    workflow.add_edge("memory_relevance", "save_memory")

    # Bitiş noktaları
    workflow.add_edge("handle_omega", END)
    workflow.add_edge("save_memory", END)

    # Grafiği derle ve döndür
    return workflow.compile()

def schedule_actions(user_id: Optional[str] = None, force: bool = False, reflection_type: str = "scheduled") -> Dict[str, Any]:
    """
    Zamanlanmış reflection aksiyonlarını çalıştır

    Args:
        user_id: Belirli bir kullanıcı için çalıştırmak istiyorsanız kullanıcı ID'si
        force: True ise her durumda çalıştır, False ise zamanlamaya göre çalıştır
        reflection_type: Yansıtma türü (scheduled, manual, event_triggered)

    Returns:
        Dict: Çalıştırma sonuçları
    """
    try:
        logger.info(f"Scheduled reflection action başlatılıyor. User ID: {user_id}, Force: {force}, Type: {reflection_type}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "processed_users": 0,
            "insights_generated": 0,
            "goals_created": 0,
            "actions_planned": 0,
            "errors": []
        }

        # Belirli bir kullanıcı belirtilmişse sadece o kullanıcı için çalıştır
        if user_id:
            try:
                user_result = process_user_reflection(user_id, reflection_type)
                if "error" not in user_result:
                    results["processed_users"] = 1
                    results["insights_generated"] = user_result.get("insights_generated", 0)
                    results["goals_created"] = user_result.get("goals_created", 0)
                else:
                    results["errors"].append(f"User {user_id}: {user_result['error']}")
                return results
            except Exception as e:
                logger.error(f"Error processing reflection for user {user_id}: {str(e)}", exc_info=True)
                results["errors"].append(f"User {user_id}: {str(e)}")
                return results

        # Tüm aktif kullanıcıları getir
        try:
            # UserRepository'de get_active_users metodu yoksa alternatif yaklaşım
            users = []
            try:
                users = user_repository.get_active_users(days=7)  # Son 7 günde aktif kullanıcılar
            except AttributeError:
                # get_active_users metodu yoksa, tüm kullanıcıları getir
                logger.warning("get_active_users metodu bulunamadı, alternatif yaklaşım kullanılıyor")
                # Bu durumda manuel olarak aktif kullanıcıları bulabiliriz
                users = []  # Şimdilik boş bırak
            
            if not users:
                logger.info("Aktif kullanıcı bulunamadı veya get_active_users metodu mevcut değil")
                return results

            for user in users:
                try:
                    user_id_str = str(user.get("id", user.get("user_id", "")))
                    if user_id_str:
                        user_result = process_user_reflection(user_id_str, reflection_type)
                        if "error" not in user_result:
                            results["processed_users"] += 1
                            results["insights_generated"] += user_result.get("insights_generated", 0)
                            results["goals_created"] += user_result.get("goals_created", 0)
                        else:
                            results["errors"].append(f"User {user_id_str}: {user_result['error']}")
                except Exception as e:
                    logger.error(f"Error processing user {user}: {str(e)}", exc_info=True)
                    results["errors"].append(f"User processing error: {str(e)}")

        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}", exc_info=True)
            results["errors"].append(f"Failed to get active users: {str(e)}")

        logger.info(f"Scheduled reflection tamamlandı. Results: {results}")
        return results

    except Exception as e:
        error_msg = f"Scheduled reflection action critical error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "processed_users": 0,
            "critical_error": True
        }

def process_user_reflection(user_id: str, reflection_type: str) -> Dict[str, Any]:
    """
    Belirli bir kullanıcı için yansıtma işlemi gerçekleştir

    Args:
        user_id: Kullanıcı ID'si
        reflection_type: Yansıtma türü

    Returns:
        Dict: İşlem sonuçları
    """
    try:
        logger.info(f"Kullanıcı {user_id} için yansıtma işlemi başlatılıyor, tür: {reflection_type}")

        # Kullanıcının var olup olmadığını kontrol et
        try:
            user = user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Kullanıcı bulunamadı: {user_id}")
                return {"error": f"User not found: {user_id}"}
        except Exception as e:
            logger.error(f"Kullanıcı kontrolü sırasında hata: {str(e)}")
            return {"error": f"User validation error: {str(e)}"}

        # Kullanıcının geçmiş etkileşimlerini getir
        try:
            memories = memory_repository.get_user_memories(user_id, limit=50)
            logger.debug(f"Kullanıcı {user_id} için {len(memories) if memories else 0} hafıza kaydı bulundu")
        except Exception as e:
            logger.error(f"Hafıza kayıtları alınırken hata: {str(e)}")
            memories = []  # Hafıza yoksa boş liste ile devam et

        # Yansıtma oturumu oluştur
        try:
            session_id = reflection_repository.create_reflection_session(
                user_id=user_id,
                reflection_type=reflection_type,
                trigger_reasons=["scheduled"] if reflection_type == "scheduled" else ["manual"]
            )

            if not session_id:
                logger.error(f"Kullanıcı {user_id} için yansıtma oturumu oluşturulamadı")
                return {"error": "Failed to create reflection session"}
                
            logger.info(f"Yansıtma oturumu oluşturuldu: {session_id}")
        except Exception as e:
            logger.error(f"Yansıtma oturumu oluşturulurken hata: {str(e)}")
            return {"error": f"Session creation error: {str(e)}"}

        # Hafıza verilerine dayalı analiz yap
        memory_count = len(memories) if memories else 0
        
        # Örnek içgörüler oluştur (gerçek uygulamada LLM ile analiz yapılır)
        insights = []
        if memory_count > 0:
            insights = [
                {
                    "user_id": user_id,
                    "insight_text": f"Kullanıcı {memory_count} etkileşim geçmişine sahip ve düzenli olarak sistem kullanıyor",
                    "insight_type": "behavioral_pattern",
                    "confidence_score": 0.85
                },
                {
                    "user_id": user_id,
                    "insight_text": "Kullanıcı çeşitli konularda yardım talep ediyor, proaktif destek faydalı olabilir",
                    "insight_type": "need_recognition",
                    "confidence_score": 0.75
                }
            ]
        else:
            insights = [
                {
                    "user_id": user_id,
                    "insight_text": "Yeni kullanıcı, onboarding ve rehberlik desteği gerekebilir",
                    "insight_type": "new_user_pattern",
                    "confidence_score": 0.90
                }
            ]

        # İçgörüleri kaydet
        insight_ids = []
        for insight in insights:
            try:
                insight_id = reflection_repository.create_insight(
                    user_id=user_id,
                    insight_text=insight["insight_text"],
                    insight_type=insight["insight_type"],
                    confidence_score=insight["confidence_score"]
                )
                if insight_id:
                    insight_ids.append(insight_id)
                    logger.debug(f"İçgörü kaydedildi: {insight_id}")
            except Exception as e:
                logger.error(f"İçgörü kaydedilirken hata: {str(e)}")

        # Hedefler oluştur
        goals = []
        if memory_count > 0:
            goals = [
                {
                    "user_id": user_id,
                    "goal_text": "Kullanıcıya proaktif yardım ve öneriler sunmak",
                    "goal_type": "proactive_assistance",
                    "priority": 7,
                    "source_insight_id": insight_ids[1] if len(insight_ids) > 1 else None
                }
            ]
        else:
            goals = [
                {
                    "user_id": user_id,
                    "goal_text": "Yeni kullanıcıya rehberlik ve onboarding desteği sağlamak",
                    "goal_type": "onboarding_support",
                    "priority": 9,
                    "source_insight_id": insight_ids[0] if insight_ids else None
                }
            ]

        # Hedefleri kaydet
        goal_ids = []
        for goal in goals:
            try:
                goal_id = reflection_repository.create_goal(
                    user_id=user_id,
                    goal_text=goal["goal_text"],
                    goal_type=goal["goal_type"],
                    priority=goal["priority"],
                    source_insight_id=goal.get("source_insight_id")
                )
                if goal_id:
                    goal_ids.append(goal_id)
                    logger.debug(f"Hedef kaydedildi: {goal_id}")
            except Exception as e:
                logger.error(f"Hedef kaydedilirken hata: {str(e)}")

        # Yansıtma oturumunu güncelle
        try:
            reflection_repository.update_reflection_session(
                session_id=session_id,
                insights_generated=len(insight_ids),
                goals_created=len(goal_ids)
            )
            logger.info(f"Yansıtma oturumu güncellendi: {session_id}")
        except Exception as e:
            logger.error(f"Yansıtma oturumu güncellenirken hata: {str(e)}")

        result = {
            "user_id": user_id,
            "session_id": session_id,
            "insights_generated": len(insight_ids),
            "goals_created": len(goal_ids),
            "reflection_type": reflection_type,
            "memory_count": memory_count,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Kullanıcı {user_id} için yansıtma işlemi tamamlandı: {result}")
        return result

    except Exception as e:
        error_msg = f"process_user_reflection kritik hatası: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": str(e), "user_id": user_id, "timestamp": datetime.now().isoformat()}