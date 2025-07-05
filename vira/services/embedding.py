import numpy as np
from vira.config import settings
from vira.utils.logger import get_logger
import openai
import httpx

logger = get_logger(__name__)

class EmbeddingService:
    """Service to generate embeddings using Azure OpenAI."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client for embeddings."""
        # Create a custom httpx client without proxies
        http_client = httpx.Client()

        self.client = openai.AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            http_client=http_client  # Use the custom client
            )
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME

        logger.info("Embedding service initialized")

    def create_embedding(self, text):
        """Create an embedding vector for the given text."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            # Extract the embedding vector from the response
            embedding_vector = response.data[0].embedding
            return np.array(embedding_vector)
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise