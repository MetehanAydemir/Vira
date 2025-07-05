import numpy as np
from openai import AzureOpenAI
from typing import Dict, Any, List, Tuple

from vira.graph.state import ViraState
from vira.db.repository import MemoryRepository
from vira.config import settings
from vira.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


def get_openai_client() -> AzureOpenAI:
    """Azure OpenAI istemcisini başlatır."""
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


def create_embedding(text: str, client: AzureOpenAI) -> List[float]:
    """Verilen metin için bir Azure OpenAI embedding'i oluşturur."""
    embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    if not embedding_model:
        raise ValueError("Yapılandırma hatası: AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME ayarı .env dosyasında eksik.")

    response = client.embeddings.create(input=text, model=embedding_model)
    return response.data[0].embedding


def retrieve_memory_node(state: ViraState) -> ViraState:
    """
    Kullanıcının mesajına benzer anıları ve son konuşmaları veritabanından alır.

    İki tür hafıza birleştirilir:
    1. Uzun Süreli Hafıza: pgvector ile benzerlik araması yapılarak bulunan anılar
    2. Kısa Süreli Hafıza: Kullanıcının son 5 konuşması (kronolojik sırayla)

    State'e eklenen değerler:
    - memory_context: Formatlanmış hafıza metni
    - retrieved_memories: Benzer anıların listesi
    - recent_conversations: Son konuşmaların listesi

    Returns:
        ViraState: Güncellenmiş state nesnesi
    """
    logger.info("--- Düğüm: retrieve_memory_node ---")

    user_id = state.get("user_id")
    query_text = state.get("original_message")
    session_id = state.get("session_id", "default_session")

    # Başlangıç değerlerini ayarla
    state["memory_context"] = ""
    state["retrieved_memories"] = []
    state["recent_conversations"] = []

    # Girdi kontrolü
    if not user_id or not query_text:
        logger.warning("Hafıza almak için user_id veya original_message eksik.")
        return state

    try:
        repo = MemoryRepository()
        client = get_openai_client()

        # 1. UZUN SÜRELİ HAFIZA: Benzer anıları al
        query_embedding = np.array(create_embedding(query_text, client))
        logger.debug("Sorgu embedding'i oluşturuldu.")

        relevant_memories = repo.retrieve_similar_memories(
            user_id=user_id,
            embedding=query_embedding,
            top_k=5
        )
        state["retrieved_memories"] = relevant_memories

        # 2. YENİ: KISA SÜRELİ HAFIZA: Son konuşmaları al
        recent_conversations = repo.get_recent_conversations(
            user_id=user_id,
            session_id=session_id,
            limit=5
        )
        state["recent_conversations"] = recent_conversations

        # 3. Hafıza bağlamını oluştur
        memory_context = ""
        # Yapılandırılabilir benzerlik eşiği
        threshold = getattr(settings, "MEMORY_SIMILARITY_THRESHOLD", 0.7)

        # 3.1 Uzun süreli hafıza formatlaması
        if relevant_memories:
            logger.info(f"{len(relevant_memories)} adet ilgili anı bulundu.")
            memory_context = "🧠 Geçmişten hatırladıklarım:\n\n"

            sorted_memories = sorted(relevant_memories, key=lambda x: x[1], reverse=True)

            for i, (content, similarity, created_date) in enumerate(sorted_memories, 1):
                if similarity >= threshold:
                    formatted_date = created_date.strftime("%d/%m/%Y %H:%M")
                    memory_context += f'{i}. "{content.strip()}" (Benzerlik: {similarity * 100:.1f}%, Tarih: {formatted_date})\n'
        else:
            logger.info("İlgili anı bulunamadı.")

        # 3.2 YENİ: Kısa süreli hafıza formatlaması
        if recent_conversations:
            logger.info(f"{len(recent_conversations)} adet son konuşma bulundu.")

            if memory_context:
                memory_context += "\n\n"

            memory_context += "💬 Son konuşmalarımız:\n\n"

            for i, (message, response, created_at) in enumerate(recent_conversations, 1):
                formatted_date = created_at.strftime("%d/%m/%Y %H:%M")
                memory_context += f"{i}. Sen: {message.strip()}\n   Ben: {response.strip()}\n   ({formatted_date})\n\n"

        # 4. Formatlanmış bağlamı state'e ekle
        state["memory_context"] = memory_context.strip()
        return state

    except Exception as e:
        logger.error(f"Hafıza alınırken hata oluştu: {e}", exc_info=True)
        # Hata durumunda bile tutarlı bir state döndür
        return state