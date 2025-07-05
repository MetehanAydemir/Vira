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


def retrieve_memory_node(state: ViraState) -> Dict[str, Any]:
    """
    Kullanıcının mesajına benzer anıları pgvector veritabanından alır ve
    hem formatlanmış bir bağlam hem de ham veri olarak döndürür.

    Returns:
        Dict[str, Any]: {
            "memory_context": str,
            "retrieved_memories": List[Tuple[str, float]]
        }
    """
    logger.info("--- Düğüm: retrieve_memory_node ---")

    user_id = state.get("user_id")
    query_text = state.get("original_message")

    # Girdi kontrolü
    if not user_id or not query_text:
        logger.warning("Hafıza almak için user_id veya original_message eksik.")
        return {"memory_context": "", "retrieved_memories": []}

    try:
        repo = MemoryRepository()
        client = get_openai_client()

        query_embedding = np.array(create_embedding(query_text, client))
        logger.debug("Sorgu embedding'i oluşturuldu.")

        relevant_memories = repo.retrieve_similar_memories(
            user_id=user_id,
            embedding=query_embedding,
            top_k=5
        )

        memory_context = ""
        # Yapılandırılabilir benzerlik eşiği
        threshold = getattr(settings, "MEMORY_SIMILARITY_THRESHOLD", 0.7)

        if relevant_memories:
            logger.info(f"{len(relevant_memories)} adet ilgili anı bulundu.")
            # Zengin ve "chat-temelli" formatlama
            memory_context = "🧠 Geçmişten hatırladıklarım:\n\n"

            sorted_memories = sorted(relevant_memories, key=lambda x: x[1], reverse=True)

            for i, (content, similarity, created_date) in enumerate(sorted_memories, 1):
                if similarity >= threshold:
                    formatted_date = created_date.strftime("%d/%m/%Y %H:%M")
                    memory_context += f'{i}. "{content.strip()}" (Benzerlik: {similarity * 100:.1f}%, Tarih: {formatted_date})\n '
        else:
            logger.info("İlgili anı bulunamadı.")

        # Zenginleştirilmiş çıktı döndür
        return {
            "memory_context": memory_context.strip(),
            "retrieved_memories": relevant_memories
        }

    except Exception as e:
        logger.error(f"Hafıza alınırken hata oluştu: {e}", exc_info=True)
        return {"memory_context": "", "retrieved_memories": []}