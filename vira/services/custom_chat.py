import requests
import json
from vira.config import settings
from vira.utils.logger import get_logger
from openai import OpenAI
logger = get_logger(__name__)


class CustomChatService:
    """Service to interact with OpenRouter API or other custom chat APIs."""

    def __init__(self):
        """Initialize the custom chat API client."""
        self.api_key = settings.CUSTOM_CHAT_API_KEY
        self.base_url = settings.CUSTOM_CHAT_API_ENDPOINT
        self.model_name = settings.CUSTOM_CHAT_MODEL_NAME
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        # Geriye dönük uyumluluk için
        self.api_version = settings.CUSTOM_CHAT_API_VERSION
        self.payload = {}  # Boş bir payload tanımlayalım

        logger.info("Custom Chat API service initialized")

    def generate_chat_response(self, messages, model=None, temperature=None, max_tokens=None, response_format=None):
        """Generate a response using the OpenRouter API via OpenAI SDK.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model name override (e.g. "openai/gpt-4o", "anthropic/claude-3-opus")
            temperature: Temperature parameter for response generation (default: 0.5)
            max_tokens: Maximum tokens in the response (default: 3000)
            response_format: Optional response format specification

        Returns:
            Generated response text
        """
        try:
            # Değerleri ayarla
            model_to_use = model or self.model_name
            temp_to_use = temperature or 0.5
            tokens_to_use = max_tokens or 3000

            # Debug için log ekle
            logger.info(f"Calling API with model: {model_to_use}, temp: {temp_to_use}, tokens: {tokens_to_use}")
            logger.info(f"Message count: {len(messages)}")

            # Yanıt formatını hazırla
            resp_format = None
            if response_format:
                resp_format = response_format

            # API çağrısını yap
            completion = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,  # Doğru format: liste içinde mesaj dict'leri
                temperature=temp_to_use,
                max_tokens=tokens_to_use,
                response_format=resp_format
            )

            # Yanıtı al
            if completion and completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content
            else:
                logger.error("API response missing expected structure")
                logger.error(f"API response: {completion}")
                return "API yanıtında beklenen yapı bulunamadı."

        except Exception as e:
            logger.error(f"Error generating custom chat response: {e}")
            # Detaylı hata bilgisi
            import traceback
            logger.error(f"Detailed error: {traceback.format_exc()}")
            return f"API yanıtı alınırken hata oluştu: {str(e)}"