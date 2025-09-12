import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

# Configure APIs
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

class EmbeddingService:
    def __init__(self):
        self.openai_client = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def get_openai_embeddings(
        self, 
        texts: List[str], 
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API
        
        Args:
            texts: List of text strings to embed
            model: OpenAI embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            
            def _get_embeddings():
                embeddings = []
                for text in texts:
                    if not text.strip():
                        continue
                    
                    response = self.openai_client.embeddings.create(
                        input=text,
                        model=model
                    )
                    embeddings.append(response.data[0].embedding)
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                return embeddings
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(self.executor, _get_embeddings)
            
            logger.info(f"Generated {len(embeddings)} OpenAI embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            raise
    
    async def get_gemini_embeddings(
        self, 
        texts: List[str],
        model: str = "models/embedding-001"
    ) -> List[List[float]]:
        """
        Generate embeddings using Google Gemini API
        
        Args:
            texts: List of text strings to embed
            model: Gemini embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            if not settings.gemini_api_key:
                raise Exception("Gemini API key not configured")
            
            def _get_embeddings():
                embeddings = []
                for text in texts:
                    if not text.strip():
                        continue
                    
                    response = genai.embed_content(
                        model=model,
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(response['embedding'])
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                return embeddings
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(self.executor, _get_embeddings)
            
            logger.info(f"Generated {len(embeddings)} Gemini embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating Gemini embeddings: {e}")
            raise
    
    async def get_embeddings(
        self, 
        texts: List[str], 
        provider: str = "openai",
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings using specified provider
        
        Args:
            texts: List of text strings to embed
            provider: "openai" or "gemini"
            model: Model name (optional, uses defaults)
            
        Returns:
            List of embedding vectors
        """
        if provider.lower() == "openai":
            model = model or "text-embedding-3-small"
            return await self.get_openai_embeddings(texts, model)
        elif provider.lower() == "gemini":
            model = model or "models/embedding-001"
            return await self.get_gemini_embeddings(texts, model)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")

    async def get_query_embedding(
        self, 
        query: str, 
        provider: str = "openai",
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding for a single query
        
        Args:
            query: Query text
            provider: "openai" or "gemini"
            model: Model name (optional)
            
        Returns:
            Single embedding vector
        """
        embeddings = await self.get_embeddings([query], provider, model)
        return embeddings[0] if embeddings else []

# Global embedding service instance
embedding_service = EmbeddingService()