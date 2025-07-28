import time
import os
from typing import List, Dict, Any, Optional
import backoff
from vira.services.custom_chat import CustomChatService
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

# Hata durumunda yeniden deneme için maksimum deneme sayısı
MAX_RETRIES = 3

@backoff.on_exception(
    backoff.expo, 
    (Exception,),
    max_tries=MAX_RETRIES
)
def call_chat_model(
    messages: List,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 800,
    response_format: Optional[Dict[str, str]] = None
) -> str:
    """
    LLM'e mesajları ileterek bir yanıt alır.
    
    Args:
        messages: LLM'e gönderilecek mesaj listesi (LangChain Message nesneleri)
        model: Kullanılacak model adı (varsayılan: "gpt-4o")
        temperature: Yaratıcılık seviyesi (0-1 arası)
        max_tokens: Maksimum token sayısı
        response_format: İstenilen yanıt formatı (örn. {"type": "json_object"})
        
    Returns:
        LLM'den alınan yanıt metni
    """
    # Model seçimi: Custom chat model'i öncelikle kullan (OpenRouter için)
    if model is None:
        model = settings.CUSTOM_CHAT_MODEL_NAME or settings.AZURE_OPENAI_DEPLOYMENT_NAME or "openai/gpt-4o-mini"
    
    logger.info(f"LLM çağrısı yapılıyor. Model: {model}, Temperature: {temperature}")
    
    # Mock mod kontrolü - test ortamında gerçek API çağrısı yapmadan çalışabilmek için
    if os.environ.get("VIRA_USE_MOCK_LLM", "false").lower() == "true":
        logger.info("Mock mod aktif: Gerçek LLM çağrısı yapılmıyor")
        # Basit bir mock yanıt döndür
        if response_format and response_format.get("type") == "json_object":
            return '{"relevance": 0.8, "accuracy": 0.7, "helpfulness": 0.9}'
        return "Bu bir mock LLM yanıtıdır."
    
    try:
        # LangChain Message nesnelerini dict formatına çevir
        formatted_messages = []
        for message in messages:
            if hasattr(message, "type"):  # LangChain Message nesnesi mi?
                role = "system" if message.type == "system" else \
                       "user" if message.type == "human" else \
                       "assistant"
                formatted_messages.append({
                    "role": role,
                    "content": message.content
                })
            elif isinstance(message, dict) and "role" in message:  # Zaten dict formatında mı?
                formatted_messages.append(message)
            else:
                logger.warning(f"Bilinmeyen mesaj formatı: {type(message)}")
        
        # CustomChatService'i başlat
        chat_service = CustomChatService()
        
        # Zamanlamayı başlat
        start_time = time.time()
        
        # CustomChatService'i genişleterek parametreleri ileteceğiz
        # generate_chat_response metodunun parametrelerini güncelleyelim
        # Orijinal CustomChatService yalnızca messages kabul ettiği için, 
        # payload içine manuel olarak diğer parametreleri ekliyoruz
        
        # CustomChatService nesnesinin payload nesnesini doğrudan değiştirelim
        # Bu, mevcut kodu en az değişiklikle uyumlu hale getirecek
        response = chat_service.generate_chat_response(
            messages=formatted_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )

        # Gecikmeyi hesapla
        duration = time.time() - start_time
        logger.info(f"LLM yanıt süresi: {duration:.2f} saniye")

        return response
    except Exception as e:
        logger.error(f"LLM çağrısı sırasında hata: {str(e)}")
        
        # Fallback mekanizması: Farklı model ile tekrar dene
        if model != "gpt-3.5-turbo":
            logger.warning(f"Model {model} ile hata oluştu, fallback olarak gpt-3.5-turbo deneniyor...")
            try:
                fallback_response = chat_service.generate_chat_response(
                    messages=formatted_messages,
                    model="gpt-3.5-turbo",
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format
                )
                logger.info("Fallback model ile başarılı yanıt alındı")
                return fallback_response
            except Exception as fallback_error:
                logger.error(f"Fallback model ile de hata oluştu: {str(fallback_error)}")
        
        # Son çare: Basit bir hata mesajı döndür
        if response_format and response_format.get("type") == "json_object":
            return '{"error": "LLM service unavailable", "fallback": true}'
        
        raise