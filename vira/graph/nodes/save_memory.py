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

def save_memory_node(state: ViraState) -> None:
    """
    Konuşma etkileşimini (kullanıcı mesajı + Vira yanıtı) veritabanına kaydeder.
    """
    user_id = state["user_id"]
    user_message = state["original_message"]
    ai_response = state["response"]

    logger.info("--- Düğüm: save_memory_node ---")

    if not user_message or not ai_response:
        logger.warning("Kaydedilecek mesaj veya yanıt bulunamadı.")
        return None

    # Tüm etkileşimi tek bir metin olarak birleştir
    interaction_text = f"Kullanıcı: {user_message}\nVira: {ai_response}"
    logger.debug(f"Kaydedilecek etkileşim: {interaction_text[:100]}...")

    try:
        # Repository ve OpenAI istemcisini başlat
        repo = MemoryRepository()
        client = get_openai_client()

        # Etkileşim metni için embedding oluştur
        interaction_embedding = np.array(create_embedding(interaction_text, client))
        logger.debug("Etkileşim embedding'i oluşturuldu")

        # Veritabanına kaydet
        memory_id = repo.store_memory(
            user_id=user_id,
            content=interaction_text,
            embedding=interaction_embedding
        )
        
        logger.info(f"Etkileşim, '{user_id}' kullanıcısı için hafızaya kaydedildi (ID: {memory_id}).")

    except Exception as e:
        logger.error(f"Hafıza kaydedilirken hata oluştu: {e}", exc_info=True)
        # Hata durumunda bile akışın devam etmesi için None döndür

    return None  # Bu düğüm state'i güncellemez