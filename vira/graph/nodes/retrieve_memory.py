import numpy as np
from openai import AzureOpenAI
from typing import Dict, Any, List

from vira.graph.state import ViraState
from vira.db.repository import MemoryRepository
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

def get_openai_client():
    """Azure OpenAI istemcisini başlatır."""
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
    )

def create_embedding(text: str, client: AzureOpenAI) -> List[float]:
    """Verilen metin için bir embedding oluşturur."""
    embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    response = client.embeddings.create(input=text, model=embedding_model)
    return response.data[0].embedding

def retrieve_memory_node(state: ViraState) -> Dict[str, Any]:
    """
    Kullanıcının mesajına benzer anıları pgvector veritabanından alır.
    """
    user_id = state["user_id"]
    query_text = state["original_message"]

    logger.info(f"--- Düğüm: retrieve_memory_node ---")
    logger.debug(f"Kullanıcı: {user_id}, Sorgu: {query_text[:30]}...")

    try:
        # Repository ve OpenAI istemcisini başlat
        repo = MemoryRepository()
        client = get_openai_client()

        # 1. Sorgu metni için embedding oluştur
        query_embedding = np.array(create_embedding(query_text, client))
        logger.debug("Sorgu embedding'i oluşturuldu")

        # 2. Benzer anıları almak için repository metodunu çağır
        relevant_memories = repo.retrieve_similar_memories(
            user_id=user_id,
            embedding=query_embedding,
            top_k=5
        )

        # 3. Anıları LLM için bir bağlam dizesi olarak biçimlendir
        memory_context = ""
        if relevant_memories:
            logger.info(f"{len(relevant_memories)} adet ilgili anı bulundu.")
            memory_context = "İşte hatırladığım bazı ilgili anılar:\n"
            for i, (content, similarity) in enumerate(relevant_memories, 1):
                if similarity > 0.7:  # Benzerlik eşiği
                    memory_context += f"{i}. {content} (ilgililik: {similarity:.2f})\n"
        else:
            logger.info("İlgili anı bulunamadı.")

        return {"memory_context": memory_context.strip()}

    except Exception as e:
        logger.error(f"Hafıza alınırken hata oluştu: {e}", exc_info=True)
        # Hata durumunda boş bağlam döndür, böylece akış devam edebilir
        return {"memory_context": ""}