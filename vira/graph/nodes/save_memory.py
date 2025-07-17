#!/usr/bin/env python3
"""
Save Memory Node - Konuşma etkileşimlerini çok katmanlı hafıza sistemine kaydeden düğüm
"""
import time
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from vira.graph.state import ViraState
from vira.db.repository import MemoryRepository, PersonalityRepository
from vira.utils.logger import get_logger
from vira.utils.openai_client import get_openai_client
from vira.utils.embedding import create_embedding

logger = get_logger(__name__)


def generate_semantic_tags(state: ViraState) -> List[str]:
    """
    Etkileşim için anlamsal etiketler oluşturur.

    Args:
        state: ViraState tipinde graf durumu

    Returns:
        List[str]: Etiketler listesi
    """
    tags = []

    # Intent bazlı etiketler
    intent = state.get("processed_input", {}).get("intent", "")
    if intent:
        tags.append(f"intent_{intent}")

    # Emotion bazlı etiketler
    emotion = state.get("processed_input", {}).get("emotion", "")
    if emotion and emotion != "neutral":
        tags.append(f"emotion_{emotion}")

    # Önem skoru bazlı etiketler
    importance_score = state.get("importance_score", 0.0)
    if importance_score > 0.8:
        tags.append("high_importance")
    elif importance_score > 0.6:
        tags.append("medium_importance")
    else:
        tags.append("low_importance")

    # Hafıza tipi bazlı etiketler
    memory_type = state.get("memory_type", "")
    if memory_type:
        tags.append(f"memory_type_{memory_type}")

    # Özel komut kontrolü
    if state.get("is_omega_command", False):
        tags.append("omega_command")

    return tags


def create_rich_metadata(state: ViraState) -> Dict[str, Any]:
    """
    Uzun süreli hafıza için zengin metadata oluşturur.

    Args:
        state: ViraState tipinde graf durumu

    Returns:
        Dict[str, Any]: Metadata sözlüğü
    """
    metadata = {
        "user_id": state.get("user_id"),
        "importance_score": state.get("importance_score", 0.0),
        "timestamp": datetime.now().isoformat(),
        "source": "conversation",
        "reasons": state.get("importance_score_reasons", [])
    }

    # Intent ve emotion bilgileri
    if "processed_input" in state:
        processed = state["processed_input"]
        metadata.update({
            "intent": processed.get("intent", "unknown"),
            "emotion": processed.get("emotion", "neutral")
        })

    # Hafıza tipi
    memory_type = state.get("memory_type", "casual")
    metadata["memory_type"] = memory_type

    # Kişilik snapshot'ı
    if "dynamic_personality" in state:
        personality = state["dynamic_personality"]
        metadata["personality_snapshot"] = {
            "empathy": personality.get("empathy", 0.5),
            "curiosity": personality.get("curiosity", 0.5),
            "assertiveness": personality.get("assertiveness", 0.5),
            "humour": personality.get("humour", 0.5),
            "scepticism": personality.get("scepticism", 0.5)
        }

    # Semantic tags
    metadata["tags"] = generate_semantic_tags(state)

    return metadata


def save_memory_node(state: ViraState) -> ViraState:
    """
    Gelişmiş çok katmanlı hafıza kaydetme sistemi

    Args:
        state: ViraState tipinde graf durumu

    Returns:
        Güncellenmiş ViraState
    """
    logger.info("--- Düğüm: save_memory_node (Enhanced) ---")

    # Durumu kopyala (immutability için)
    new_state = ViraState(state)


    # Gerekli verileri state'den al
    user_id = new_state["user_id"]
    user_message = new_state.get("original_message", "")
    ai_response = new_state.get("response", "")
    session_id = new_state.get("session_id", f"session_{user_id}_{int(time.time())}")
    should_promote = new_state.get("should_promote_to_long_term", False)

    if not user_message or not ai_response:
        logger.warning("Kaydedilecek mesaj veya yanıt bulunamadı.")
        new_state["memory_saved"] = False

        # Hata durumunda bile dynamic_personality değişkenini güncelle
        # Bu şekilde LangGraph'in beklediği değişken güncellemesi gerçekleşir
        if "dynamic_personality" in state:
            new_state["dynamic_personality"] = state["dynamic_personality"]
        else:
            new_state["dynamic_personality"] = {}

        return new_state

    # Etkileşim metnini hazırla
    interaction_text = f"Kullanıcı: {user_message}\nVira: {ai_response}"
    logger.debug(f"Kaydedilecek etkileşim: {interaction_text[:100]}...")

    try:
        # Repository ve OpenAI istemcisini başlat
        repo = MemoryRepository()

        # 1. HER ZAMAN: Interaction tablosuna kaydet
        try:
            interaction_id = repo.store_interaction(
                user_id=user_id,
                message=user_message,
                response=ai_response,
                intent_type=new_state.get("processed_input", {}).get("intent")
            )
            logger.debug(f"Interaction kaydedildi: {interaction_id}")
            new_state["interaction_id"] = interaction_id
        except Exception as e:
            logger.error(f"Interaction kaydedilirken hata: {e}")

        # 2. HER ZAMAN: Short-term memory'ye kaydet
        try:
            short_memory_id = repo.store_short_term_memory(
                session_id=session_id,
                content=interaction_text
            )
            logger.debug(f"Short-term memory kaydedildi: {short_memory_id}")
            new_state["short_memory_id"] = short_memory_id
        except Exception as e:
            logger.error(f"Short-term memory kaydedilirken hata: {e}")

        # 3. KOŞULLU: Long-term memory'ye kaydet
        long_memory_id = None
        if should_promote:
            try:
                # OpenAI istemcisini başlat
                client = get_openai_client()

                # Embedding oluştur
                interaction_embedding = np.array(create_embedding(interaction_text, client))
                logger.debug("Etkileşim embedding'i oluşturuldu")

                # Zengin metadata oluştur
                metadata = create_rich_metadata(new_state)

                # Long-term memory'ye kaydet
                long_memory_id = repo.store_long_term_memory(
                    user_id=user_id,
                    content=interaction_text,
                    embedding=interaction_embedding,
                    metadatas=metadata
                )

                logger.info(
                    f"Long-term hafızaya kaydedildi (ID: {long_memory_id}, Skor: {new_state.get('importance_score', 0.0):.2f})")
                new_state["long_memory_id"] = long_memory_id
            except Exception as e:
                logger.error(f"Long-term memory kaydedilirken hata: {e}")
        else:
            logger.info(
                f"Etkileşim uzun süreli hafızaya kaydedilmedi (Skor: {new_state.get('importance_score', 0.0):.2f})")

        # 4. YENİ EKLENDİ: Kişilik verilerini güncelle veya aynı tut
        try:
            # Eğer mevcut dynamic_personality varsa, onu yeni state'e aktar
            if "dynamic_personality" in state:
                new_state["dynamic_personality"] = state["dynamic_personality"]

                # Opsiyonel: Eğer personality güncellemesi yapmak istenirse
                # Bu kısım kişiliği güncellemek için kullanılabilir
                personality_repo = PersonalityRepository()
                personality = state["dynamic_personality"]

                # Kişilik değişimleri için log oluştur (gerçek uygulamada bu kişiliği de kaydedebilir)
                logger.debug(f"Kişilik durumu korundu: {personality}")
            else:
                # Eğer yoksa, boş bir değer ekle
                new_state["dynamic_personality"] = {}
                logger.debug("Dynamic personality bulunamadı, boş bir değer eklendi")
        except Exception as e:
            logger.error(f"Kişilik verisi güncellenirken hata: {e}")
            # Hata olsa bile mutlaka bu değişkeni ata
            new_state["dynamic_personality"] = state.get("dynamic_personality", {})

        # State'i güncelle
        new_state["memory_saved"] = True
        new_state["session_id"] = session_id

    except Exception as e:
        logger.error(f"Hafıza kaydedilirken hata oluştu: {e}", exc_info=True)
        new_state["memory_saved"] = False

        # Genel hata durumunda bile dynamic_personality'yi güncelle
        if "dynamic_personality" in state:
            new_state["dynamic_personality"] = state["dynamic_personality"]
        else:
            new_state["dynamic_personality"] = {}

    return new_state