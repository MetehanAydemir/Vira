#!/usr/bin/env python3
"""
OpenAI istemcisi oluşturma yardımcı fonksiyonları
"""
from openai import AzureOpenAI
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

def get_openai_client():
    """
    Azure OpenAI istemcisini başlatır.
    
    Returns:
        AzureOpenAI: OpenAI istemcisi
    """
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
    )