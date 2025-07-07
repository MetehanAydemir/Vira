#!/usr/bin/env python3
"""
Embedding oluşturma yardımcı fonksiyonları
"""
from typing import List
from openai import AzureOpenAI
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

def create_embedding(text: str, client: AzureOpenAI) -> List[float]:
    """
    Verilen metin için bir embedding oluşturur.
    
    Args:
        text: Embedding oluşturulacak metin
        client: OpenAI istemcisi
        
    Returns:
        List[float]: Oluşturulan embedding vektörü
    """
    embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    response = client.embeddings.create(input=text, model=embedding_model)
    return response.data[0].embedding