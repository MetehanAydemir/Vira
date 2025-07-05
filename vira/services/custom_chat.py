import requests
import json
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class CustomChatService:
    """Service to interact with custom chat API."""
    
    def __init__(self):
        """Initialize the custom chat API client."""
        self.api_key = settings.CUSTOM_CHAT_API_KEY
        self.endpoint = settings.CUSTOM_CHAT_API_ENDPOINT
        self.api_version = settings.CUSTOM_CHAT_API_VERSION
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info("Custom Chat API service initialized")
    
    def generate_chat_response(self, messages):
        """Generate a response using the custom chat API."""
        try:
            payload = {
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800,
                "api_version": self.api_version
            }
            
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Error generating custom chat response: {e}")
            raise