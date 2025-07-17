#!/usr/bin/env python3
"""
Retrieve Memory Node - Kullanıcının mesajına uygun hafızaları getiren düğüm
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from vira.graph.state import ViraState
from vira.db.repository import MemoryRepository
from vira.config import settings
from vira.utils.logger import get_logger
from vira.utils.openai_client import get_openai_client
from vira.utils.embedding import create_embedding

logger = get_logger(__name__)


def format_memory_results(memories: List[Tuple[str, float, datetime, Dict[str, Any]]], threshold: float = 0.7) -> str:
    """
    Uzun süreli hafıza sonuçlarını formatlar.

    Args:
        memories: (içerik, benzerlik, tarih, metadata) dörtlülerinden oluşan liste
        threshold: Minimum benzerlik eşiği

    Returns:
        str: Formatlanmış hafıza metni
    """
    if not memories:
        return ""

    memory_text = "🧠 Geçmişten hatırladıklarım:\n\n"

    # Benzerliğe göre sırala (en yüksekten en düşüğe)
    sorted_memories = sorted(memories, key=lambda x: x[1], reverse=True)

    for i, (content, similarity, created_date, metadata) in enumerate(sorted_memories, 1):
        if similarity >= threshold:
            # Tarih formatını ayarla
            formatted_date = created_date.strftime("%d/%m/%Y %H:%M")

            # Metadata'dan ekstra bilgiler
            memory_type = metadata.get("memory_type", "casual")
            importance_score = metadata.get("importance_score", 0.0)

            # Bellek türüne göre emoji ekle
            memory_emoji = "💡" if memory_type == "factual" else "💭" if memory_type == "casual" else "⭐" if memory_type == "important" else "🔍"

            # Metni formatla
            memory_text += f'{i}. {memory_emoji} "{content.strip()}" (Benzerlik: {similarity * 100:.1f}%, Önem: {importance_score * 100:.0f}%, Tarih: {formatted_date})\n\n'

            # Log
            logger.debug(f"Memory #{i}:")
            logger.debug(f"  İçerik: {content.strip()[:100]}...")
            logger.debug(f"  Benzerlik: {similarity * 100:.2f}%")
            logger.debug(f"  Hafıza Türü: {memory_type}")
            logger.debug(f"  Tarih: {formatted_date}")

    return memory_text.strip()


def format_recent_conversations(conversations: List[Tuple[str, str, datetime]]) -> str:
    """
    Son konuşmaları formatlar.

    Args:
        conversations: (kullanıcı_mesajı, sistem_yanıtı, tarih) üçlülerinden oluşan liste

    Returns:
        str: Formatlanmış konuşma metni
    """
    if not conversations:
        return ""

    conversation_text = "💬 Son konuşmalarımız:\n\n"

    for i, (message, response, created_at) in enumerate(conversations, 1):
        formatted_date = created_at.strftime("%d/%m/%Y %H:%M")
        conversation_text += f"{i}. Sen: {message.strip()}\n   Ben: {response.strip()}\n   ({formatted_date})\n\n"

    return conversation_text.strip()


def retrieve_memory_node(state: ViraState) -> ViraState:
    """
    Kullanıcının mesajına benzer anıları ve son konuşmaları veritabanından alır.

    Çok katmanlı hafıza sisteminden şu bilgileri getirir:
    1. Uzun Süreli Hafıza: Vektör benzerlik araması ile bulunan semantik olarak benzer anılar
    2. Kısa Süreli Hafıza: Mevcut oturumdaki son konuşmalar
    3. Kronolojik Hafıza: Genel olarak kullanıcının son etkileşimleri

    Args:
        state: ViraState tipinde graf durumu

    Returns:
        Güncellenmiş ViraState
    """
    logger.info("--- Düğüm: retrieve_memory_node (Enhanced) ---")

    # Durumu kopyala (immutability için)
    new_state = ViraState(state)

    # Gerekli verileri state'den al
    user_id = new_state.get("user_id")
    query_text = new_state.get("original_message")
    session_id = new_state.get("session_id", "default_session")

    # [YENİ] Kullanıcı birleşik modelini al (varsa)
    unified_model = None
    if hasattr(new_state, "has_unified_user_model") and new_state.has_unified_user_model():
        unified_model = new_state.get_unified_user_model()
        logger.info(f"Kullanıcı {user_id} için birleşik model bulundu, hafıza erişimi zenginleştirilecek")

    # Başlangıç değerlerini ayarla
    new_state["memory_context"] = ""
    new_state["retrieved_memories"] = []
    new_state["recent_conversations"] = []
    new_state["memory_types_found"] = []

    # Girdi kontrolü
    if not user_id or not query_text:
        logger.warning("Hafıza almak için user_id veya original_message eksik.")
        return new_state

    try:
        repo = MemoryRepository()
        client = get_openai_client()

        # 1. UZUN SÜRELİ HAFIZA: Semantik benzerlik araması
        try:
            # Sorgu embedding'i oluştur
            query_embedding = np.array(create_embedding(query_text, client))
            logger.debug("Sorgu embedding'i oluşturuldu.")

            # Benzer anıları metadata ile al
            relevant_memories = repo.retrieve_similar_memories_with_metadata(
                user_id=user_id,
                embedding=query_embedding,
                top_k=5
            )

            # [YENİ] MetaCognitive ile hafıza erişimini zenginleştir
            if unified_model and hasattr(repo, "enhance_memory_retrieval"):
                try:
                    # MetaCognitive Engine oluştur
                    from vira.metacognition.engine import MetaCognitiveEngine
                    engine = MetaCognitiveEngine(repo)

                    # Hafızaları kullanıcı modeline göre zenginleştir
                    enhanced_memories = engine.enhance_memory_retrieval(
                        query=query_text,
                        model=unified_model,
                        memories=relevant_memories
                    )

                    relevant_memories = enhanced_memories
                    logger.info("Hafıza erişimi MetaCognitive Engine ile zenginleştirildi")
                except Exception as e:
                    logger.error(f"MetaCognitive hafıza zenginleştirme sırasında hata: {e}")

            new_state["retrieved_memories"] = relevant_memories
            logger.info(f"{len(relevant_memories)} adet ilgili anı bulundu.")

            # Metadata analizi (hafıza türleri)
            memory_types = set()
            for memory in relevant_memories:
                memory_metadata = memory[3]  # Metadata kısmı
                memory_type = memory_metadata.get("memory_type", "casual")
                memory_types.add(memory_type)

            new_state["memory_types_found"] = list(memory_types)
        except Exception as e:
            logger.error(f"Uzun süreli hafıza alınırken hata: {e}")

        # 2. KISA SÜRELİ HAFIZA: Mevcut oturumdaki son konuşmalar
        try:
            # Önce session_id ile kısa süreli hafızadan konuşmaları al
            recent_conversations = repo.get_recent_conversations(
                user_id=user_id,
                session_id=session_id,
                limit=5
            )

            if unified_model:
                # Kullanıcının tercih ettiği konulara göre son konuşmaları filtrele
                preferred_topics = unified_model.conversation_patterns.get("preferred_topics", [])
                if preferred_topics:
                    # Tercih edilen konularla ilgili son konuşmaları vurgula
                    for i, conv in enumerate(recent_conversations):
                        user_msg, sys_msg, date = conv
                        for topic in preferred_topics:
                            if topic.lower() in user_msg.lower() or topic.lower() in sys_msg.lower():
                                # Bu konuşmayı önemli olarak işaretle (listeyi tuple'dan liste yapısına çevirmek gerekebilir)
                                # Bu örnekte sadece logluyoruz
                                logger.debug(f"Tercih edilen konu bulundu: '{topic}' - Konuşma vurgulandı")

            new_state["recent_conversations"] = recent_conversations
            logger.info(f"{len(recent_conversations)} adet son konuşma bulundu.")
        except Exception as e:
            logger.error(f"Kısa süreli hafıza alınırken hata: {e}")

        # [YENİ] MetaCognitive önerilerine göre hafıza bağlamını şekillendirme
        metacognitive_insights = {}
        if unified_model:
            # MetaCognitive engine'in kullanıcı anlayışından faydalanarak ek bağlam öner
            metacognitive_insights = {
                "preferred_interaction_style": unified_model.current_state.get("interaction_mode", ""),
                "emotional_tone": unified_model.current_state.get("emotional_state", {}).get("primary", ""),
                "recurring_themes": unified_model.memory_themes.get("dominant_topics", [])[:3],
                "response_style_preference": unified_model.conversation_patterns.get("response_styles", {})
            }
            new_state["metacognitive_insights"] = metacognitive_insights
            logger.debug(f"MetaCognitive insights eklendi: {metacognitive_insights}")

        # 3. Hafıza bağlamını oluştur
        memory_context = ""

        # 3.1 Uzun süreli hafıza formatlaması
        if relevant_memories:
            # Yapılandırılabilir benzerlik eşiği
            threshold = getattr(settings, "MEMORY_SIMILARITY_THRESHOLD", 0.7)
            memory_text = format_memory_results(relevant_memories, threshold)
            if memory_text:
                memory_context += memory_text

        # 3.2 Kısa süreli hafıza formatlaması
        if recent_conversations:
            conversation_text = format_recent_conversations(recent_conversations)
            if conversation_text:
                if memory_context:
                    memory_context += "\n\n"
                memory_context += conversation_text

        # [YENİ] 3.3 MetaCognitive Engine önerileri varsa ekle
        if metacognitive_insights and any(metacognitive_insights.values()):
            if memory_context:
                memory_context += "\n\n"

            # Anlamlı önerileri formatla
            meta_context = "🧠 MetaCognitive İçgörüler:\n"
            if metacognitive_insights.get("preferred_interaction_style"):
                meta_context += f"- Tercih edilen etkileşim stili: {metacognitive_insights['preferred_interaction_style']}\n"
            if metacognitive_insights.get("emotional_tone"):
                meta_context += f"- Mevcut duygusal ton: {metacognitive_insights['emotional_tone']}\n"
            if metacognitive_insights.get("recurring_themes"):
                themes = ", ".join(metacognitive_insights["recurring_themes"])
                meta_context += f"- Tekrarlayan temalar: {themes}\n"

            memory_context += meta_context

        # 4. Formatlanmış bağlamı state'e ekle
        new_state["memory_context"] = memory_context.strip()

        # 5. Hafıza aramasının başarılı olduğunu işaretle
        new_state["memory_retrieved"] = True

        return new_state

    except Exception as e:
        logger.error(f"Hafıza alınırken hata oluştu: {e}", exc_info=True)
        # Hata durumunda bile tutarlı bir state döndür
        new_state["memory_retrieved"] = False
        return new_state