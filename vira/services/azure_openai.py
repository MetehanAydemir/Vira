import openai
import httpx
from vira.config import settings
from vira.utils.logger import get_logger

logger = get_logger(__name__)

class AzureOpenAIService:
    """Service to interact with Azure OpenAI."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        # Create a custom httpx client without proxies
        http_client = httpx.Client()

        self.client = openai.AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            http_client=http_client  # Use the custom client
            )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME

        logger.info("Azure OpenAI service initialized")

    def generate_chat_response(self, messages):
        """Generate a response using the Azure OpenAI chat model."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating Azure OpenAI chat response: {e}")
            raise
            raise