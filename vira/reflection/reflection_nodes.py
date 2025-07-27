"""
Yansıtma sistemi için graf düğümleri.
Mevcut graf yapısına entegre edilecek düğümleri tanımlar.
"""

import json
import logging
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime, timedelta
import uuid

from ..db.repository import DatabaseRepository
from ..graph.state import ViraState
from ..utils.logger import get_logger

from .data_gatherer import ReflectionDataGatherer
from .pattern_analyzers import TemporalPatternAnalyzer, BehavioralPatternAnalyzer
from .insight_generator import InsightGenerator
from .goal_generator import EmergentGoalGenerator
from .action_executor import ActionExecutor

# LLM istemcisini import et
from ..utils.llm_client import LLMClient

# Logger ayarla
logger = get_logger(__name__)

def reflection_trigger_node(state: ViraState) -> ViraState:
    """
    Yansıtma tetikleyici düğüm.
    Belirli koşulların sağlanıp sağlanmadığını kontrol ederek
    self-reflection sürecinin başlatılması gerekip gerekmediğine karar verir.
    
    Args:
        state: VIRA durum nesnesi

    Returns:
        Güncellenmiş VIRA durum nesnesi
    """
    try:
        user_id = state.get("user_id")
        if not user_id:
            logger.warning("reflection_trigger_node: user_id not found in state")
            return {
                **state,
                "should_reflect": False,
                "reflection_ready": False,
                "reflection_error": "Missing user_id"
            }

        # Yansıtma yapılmalı mı kontrol et
        should_reflect = check_reflection_triggers(user_id)

        logger.info(f"Reflection triggered for user {user_id}: {should_reflect}")

        return {
            **state,
            "should_reflect": should_reflect,
            "reflection_ready": True,
            "reflection_start_time": datetime.now().isoformat() if should_reflect else None
        }
    except Exception as e:
        logger.error(f"Error in reflection_trigger_node: {str(e)}", exc_info=True)
        return {
            **state,
            "should_reflect": False,
            "reflection_ready": False,
            "reflection_error": str(e)
        }

def autonomous_reflection_node(state: ViraState) -> ViraState:
    """
    Otonom yansıtma düğümü.
    Kullanıcı verilerini analiz ederek içgörüler ve hedefler oluşturur.
    
    Args:
        state: VIRA durum nesnesi

    Returns:
        İçgörüler ve hedefler ile güncellenmiş VIRA durum nesnesi
    """
    if not state.get("should_reflect", False):
        return {**state, "reflection_skipped": True}

    try:
        user_id = state.get("user_id")
        if not user_id:
            logger.warning("autonomous_reflection_node: user_id not found in state")
            return {**state, "reflection_completed": False, "reflection_error": "Missing user_id"}

        db_repository = DatabaseRepository()
        llm_client = LLMClient()

        # Başlangıç zamanını kaydet
        start_time = datetime.now()

        # 1. Veri topla
        logger.info(f"Gathering data for user {user_id}")
        data_gatherer = ReflectionDataGatherer(db_repository)
        conversation_patterns = data_gatherer.gather_conversation_patterns(user_id)
        memory_patterns = data_gatherer.gather_memory_patterns(user_id)

        # 2. Desenleri analiz et
        logger.info(f"Analyzing patterns for user {user_id}")
        temporal_analyzer = TemporalPatternAnalyzer()
        behavioral_analyzer = BehavioralPatternAnalyzer()

        temporal_insights = temporal_analyzer.analyze_conversation_timing(
            conversation_patterns.get("conversations", [])
        )

        behavioral_insights = behavioral_analyzer.analyze_communication_style(
            conversation_patterns.get("conversations", [])
        )

        # 3. İçgörüler üret
        logger.info(f"Generating insights for user {user_id}")
        insight_generator = InsightGenerator(llm_client)
        insights = []
        insights.extend(insight_generator.generate_temporal_insights(temporal_insights))
        insights.extend(insight_generator.generate_behavioral_insights(behavioral_insights))

        # 4. Hedefler oluştur
        logger.info(f"Generating goals for user {user_id}")
        goal_generator = EmergentGoalGenerator()
        goals = goal_generator.generate_goals_from_insights(insights, user_id)

        # 5. Veritabanına kaydet
        logger.info(f"Saving reflection session for user {user_id}")
        duration = (datetime.now() - start_time).total_seconds()

        reflection_data = {
            "insights": insights,
            "goals": goals,
            "patterns_analyzed": {
                "temporal": temporal_insights,
                "behavioral": behavioral_insights
            }
        }

        session_id = save_reflection_session(user_id, db_repository, reflection_data, duration)

        return {
            **state,
            "reflection_completed": True,
            "reflection_session_id": session_id,
            "reflection_insights": insights,
            "reflection_goals": goals,
            "insights_generated": len(insights),
            "goals_created": len(goals),
            "reflection_duration": duration
        }
    except Exception as e:
        logger.error(f"Error in autonomous_reflection_node: {str(e)}", exc_info=True)
        return {
            **state,
            "reflection_completed": False,
            "reflection_error": str(e)
        }

def action_planning_node(state: ViraState) -> ViraState:
    """
    Aksiyon planlama düğümü.
    Oluşturulan hedefler için aksiyonları planlar.

    Args:
        state: VIRA durum nesnesi

    Returns:
        Planlanan aksiyonlarla güncellenmiş VIRA durum nesnesi
    """
    if not state.get("reflection_completed", False):
        return state

    try:
        user_id = state.get("user_id")
        goals = state.get("reflection_goals", [])

        if not goals:
            logger.info(f"No goals to plan actions for user {user_id}")
            return {**state, "action_planning_completed": True, "actions_planned": 0}

        logger.info(f"Planning actions for {len(goals)} goals for user {user_id}")

        # Aksiyonları planla
        action_plans = []
        for goal in goals:
            action_plan = {
                "goal_id": goal.get("id", str(uuid.uuid4())),
                "goal_text": goal.get("goal_text", ""),
                "goal_type": goal.get("goal_type", ""),
                "scheduled_execution": calculate_execution_time(goal),
                "action_status": "planned"
            }
            action_plans.append(action_plan)

        # Veritabanına kaydet
        db_repository = DatabaseRepository()
        for plan in action_plans:
            db_repository.save_action_plan(plan)

        return {
            **state,
            "action_planning_completed": True,
            "action_plans": action_plans,
            "actions_planned": len(action_plans)
        }
    except Exception as e:
        logger.error(f"Error in action_planning_node: {str(e)}", exc_info=True)
        return {
            **state,
            "action_planning_completed": False,
            "action_planning_error": str(e)
        }

def execute_action_node(state: ViraState) -> ViraState:
    """
    Aksiyon uygulama düğümü.
    Belirlenen bir aksiyonu uygular.

    Args:
        state: VIRA durum nesnesi (goal_id içerir)

    Returns:
        Aksiyon sonucuyla güncellenmiş VIRA durum nesnesi
    """
    goal_id = state.get("goal_id")
    if not goal_id:
        logger.warning("execute_action_node: goal_id not found in state")
        return {**state, "action_executed": False, "action_error": "Missing goal_id"}

    try:
        # Aksiyon uygulayıcısını başlat
        db_repository = DatabaseRepository()
        action_executor = ActionExecutor(db_repository)

        # Aksiyonu uygula
        logger.info(f"Executing action for goal {goal_id}")
        result = action_executor.execute_action(goal_id)

        return {
            **state,
            "action_executed": True,
            "action_result": result,
            "action_success": result.get("status") not in ["error", "insufficient_data"]
        }
    except Exception as e:
        logger.error(f"Error in execute_action_node: {str(e)}", exc_info=True)
        return {
            **state,
            "action_executed": False,
            "action_error": str(e)
        }

def check_reflection_triggers(user_id: str) -> bool:
    """
    Yansıtma tetiklenmeli mi kontrol et

    Args:
        user_id: Kullanıcı ID'si

    Returns:
        Yansıtma yapılmalı mı (bool)
    """
    # Kullanıcı için son yansıtma zamanını kontrol et
    db_repository = DatabaseRepository()
    last_reflection = db_repository.get_last_reflection_session(user_id)
    
    # Eğer son 24 saat içinde yansıtma yapıldıysa, tekrar yapma
    if last_reflection:
        last_time = last_reflection.get("created_at")
        if last_time and (datetime.now() - last_time).total_seconds() < 86400:  # 24 saat
            return False
    
    # Yeterli veri var mı kontrol et (minimum 5 etkileşim)
    interaction_count = db_repository.count_user_interactions(user_id, days=7)
    if interaction_count < 5:
        return False
    
    # Varsayılan olarak 24 saatte bir yansıtma yap
    return True

def calculate_execution_time(goal: Dict[str, Any]) -> datetime:
    """
    Hedef için uygun uygulama zamanını hesapla

    Args:
        goal: Hedef bilgileri

    Returns:
        Planlanan uygulama zamanı
    """
    now = datetime.now()
    goal_type = goal.get("goal_type", "")

    if goal_type == "proactive_engagement":
        # Proaktif etkileşim için 1 saat sonra
        return now + timedelta(hours=1)
    elif goal_type == "emotional_support":
        # Duygusal destek için aynı gün içinde
        return now + timedelta(hours=3)
    elif goal_type == "communication_optimization":
        # İletişim optimizasyonu için hemen
        return now
    else:
        # Varsayılan olarak 2 saat sonra
        return now + timedelta(hours=2)

def save_reflection_session(
    user_id: str,
    db_repository: DatabaseRepository,
    reflection_data: Dict[str, Any],
    duration_seconds: float = 0
) -> str:
    """
    Yansıtma oturumunu veritabanına kaydet

    Args:
        user_id: Kullanıcı ID'si
        db_repository: Veritabanı repository nesnesi
        reflection_data: Yansıtma verileri
        duration_seconds: İşlem süresi

    Returns:
        Oluşturulan yansıtma oturumu ID'si
    """
    session_data = {
        "user_id": user_id,
        "reflection_type": "daily",
        "trigger_reasons": ["time_based", "sufficient_data"],
        "analysis_results": json.dumps(reflection_data.get("patterns_analyzed", {})),
        "insights_generated": len(reflection_data.get("insights", [])),
        "goals_created": len(reflection_data.get("goals", [])),
        "reflection_depth": 0.7,  # Varsayılan derinlik
        "created_at": datetime.now(),
        "duration_seconds": duration_seconds
    }
    
    # Yansıtma oturumunu kaydet
    reflection_id = db_repository.save_reflection_session(session_data)
    
    # İçgörüleri kaydet
    for insight in reflection_data.get("insights", []):
        insight_data = {
            "user_id": user_id,
            "insight_text": insight.get("text", ""),
            "insight_type": insight.get("type", "unknown"),
            "confidence_score": insight.get("confidence", 0.5),
            "source_memory_ids": json.dumps([]),  # Gerekirse hafıza ID'leri eklenebilir
            "created_at": datetime.now()
        }
        db_repository.save_insight(insight_data)
    
    # Hedefleri kaydet
    goal_ids = []
    for goal in reflection_data.get("goals", []):
        goal_data = {
            "user_id": goal.get("user_id", user_id),
            "goal_text": goal.get("goal_text", ""),
            "goal_type": goal.get("goal_type", "unknown"),
            "priority": goal.get("priority", 5),
            "status": goal.get("status", "active"),
            "created_at": datetime.now()
        }
        goal_id = db_repository.save_goal(goal_data)
        goal_ids.append(goal_id)

    return reflection_id