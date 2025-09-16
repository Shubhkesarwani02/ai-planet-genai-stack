import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import random

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
    
    def _retry_with_backoff(self, func, max_retries=5, base_delay=2):
        """
        Retry function with exponential backoff for rate limiting
        Enhanced for aggressive quota management
        """
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ['429', 'quota', 'rate limit', 'resource_exhausted', 'too many requests']):
                    if attempt < max_retries - 1:
                        # More aggressive exponential backoff
                        delay = base_delay * (3 ** attempt) + random.uniform(0, 2)
                        logger.warning(f"Rate limit hit, retrying in {delay:.2f} seconds (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        # Final attempt failed
                        logger.error(f"Rate limit exceeded after {max_retries} attempts")
                        raise Exception(f"API quota exceeded after {max_retries} retries. Please try again later.")
                else:
                    # Non-rate-limit error, don't retry
                    raise e
        return None
    
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
                    
                    try:
                        response = self.openai_client.embeddings.create(
                            input=text,
                            model=model
                        )
                        embeddings.append(response.data[0].embedding)
                        
                        # Rate limiting
                        time.sleep(0.1)
                    except Exception as e:
                        # Check for specific rate limit errors
                        if '429' in str(e) or 'rate limit' in str(e).lower():
                            logger.warning(f"Rate limit hit during OpenAI embedding generation: {e}")
                            raise
                        else:
                            logger.error(f"Error generating embedding for text chunk: {e}")
                            raise
                
                return embeddings
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(self.executor, _get_embeddings)
            
            logger.info(f"Generated {len(embeddings)} OpenAI embeddings")
            return embeddings
            
        except Exception as e:
            # Check if it's specifically a rate limit error for better logging
            if '429' in str(e) or 'rate limit' in str(e).lower():
                logger.warning(f"OpenAI rate limit exceeded: {e}")
            else:
                logger.error(f"Error generating OpenAI embeddings: {e}")
            raise
    
    async def get_gemini_embeddings(
        self, 
        texts: List[str],
        model: str = None
    ) -> List[List[float]]:
        """
        Generate embeddings using Google Gemini API with aggressive rate limiting
        
        Args:
            texts: List of text strings to embed
            model: Gemini embedding model to use (defaults to configured default)
            
        Returns:
            List of embedding vectors
        """
        try:
            if not settings.gemini_api_key:
                raise Exception("Gemini API key not configured")
            
            # Use configured default if no model specified
            if model is None:
                model = settings.default_gemini_embedding_model
                
            # Use configurable batch size
            batch_size = settings.embedding_batch_size
            all_embeddings = []
            
            def _get_embeddings_batch(text_batch):
                embeddings = []
                for i, text in enumerate(text_batch):
                    if not text.strip():
                        continue
                    
                    try:
                        def make_request():
                            return genai.embed_content(
                                model=model,
                                content=text,
                                task_type="retrieval_document"
                            )
                        
                        response = self._retry_with_backoff(make_request, max_retries=5, base_delay=2)
                        embeddings.append(response['embedding'])
                        
                        # Use configurable delay between requests
                        if i < len(text_batch) - 1:  # Don't sleep after the last item
                            time.sleep(settings.embedding_delay_seconds)
                            
                    except Exception as e:
                        # Check for specific rate limit errors
                        if any(keyword in str(e).lower() for keyword in ['429', 'quota', 'rate limit', 'resource_exhausted', 'too many requests']):
                            logger.warning(f"Rate limit hit during Gemini embedding generation: {e}")
                            # Longer backoff for rate limits
                            time.sleep(5)
                            raise
                        else:
                            logger.error(f"Error generating embedding for text chunk: {e}")
                            raise
                
                return embeddings
            
            # Process texts in very small batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size} (texts {i+1}-{min(i+batch_size, len(texts))} of {len(texts)})")
                
                try:
                    # Run batch in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    batch_embeddings = await loop.run_in_executor(self.executor, _get_embeddings_batch, batch)
                    all_embeddings.extend(batch_embeddings)
                    
                    # Configurable delay between batches
                    if i + batch_size < len(texts):
                        await asyncio.sleep(settings.embedding_delay_seconds + 1)  # Slightly longer delay between batches
                        
                except Exception as batch_error:
                    # If we hit rate limits even with aggressive throttling, fail gracefully
                    if any(keyword in str(batch_error).lower() for keyword in ['429', 'quota', 'rate limit', 'resource_exhausted']):
                        logger.error(f"Rate limit exceeded even with aggressive throttling at batch {i//batch_size + 1}. Processed {len(all_embeddings)} embeddings before hitting limit.")
                        raise Exception(f"Embedding quota exceeded. Please try again later or reduce document size. Processed {len(all_embeddings)}/{len(texts)} chunks.")
                    else:
                        raise batch_error
            
            logger.info(f"Generated {len(all_embeddings)} Gemini embeddings")
            return all_embeddings
            
        except Exception as e:
            # Check if it's specifically a rate limit error for better logging
            if any(keyword in str(e).lower() for keyword in ['429', 'quota', 'rate limit', 'resource_exhausted']):
                logger.warning(f"Gemini rate limit exceeded: {e}")
            else:
                logger.error(f"Error generating Gemini embeddings: {e}")
            raise
    
    async def get_embeddings(
        self, 
        texts: List[str], 
        provider: str = "gemini",
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings using specified provider with automatic fallback
        
        Args:
            texts: List of text strings to embed
            provider: "openai" or "gemini"
            model: Model name (optional, uses defaults)
            
        Returns:
            List of embedding vectors
        """
        # Try primary provider first
        try:
            if provider.lower() == "openai":
                model = model or "text-embedding-3-small"
                return await self.get_openai_embeddings(texts, model)
            elif provider.lower() == "gemini":
                model = model or "models/embedding-001"
                return await self.get_gemini_embeddings(texts, model)
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a rate limit or quota error
            if any(keyword in error_msg for keyword in ['rate limit', 'quota', '429', 'exceeded']):
                logger.warning(f"Rate limit hit for {provider}, attempting fallback...")
                
                # Try fallback provider only if it's properly configured
                if provider.lower() == "gemini":
                    if self.openai_client and settings.openai_api_key and not settings.openai_api_key.startswith('sk-test-'):
                        logger.info("Falling back to OpenAI for embeddings")
                        try:
                            return await self.get_openai_embeddings(texts, "text-embedding-3-small")
                        except Exception as fallback_error:
                            logger.error(f"Fallback to OpenAI failed: {fallback_error}")
                    else:
                        logger.warning("OpenAI not properly configured for fallback")
                    
                    # If we reach here, we can't generate embeddings
                    raise Exception(f"Gemini quota exceeded and no valid fallback available. Please wait for quota reset or configure OpenAI API key. Original error: {e}")
                    
                elif provider.lower() == "openai":
                    if settings.gemini_api_key:
                        logger.info("Falling back to Gemini for embeddings")
                        try:
                            return await self.get_gemini_embeddings(texts, "models/embedding-001")
                        except Exception as fallback_error:
                            logger.error(f"Fallback to Gemini failed: {fallback_error}")
                            raise Exception(f"Both OpenAI and Gemini embedding providers failed. OpenAI error: {e}, Gemini error: {fallback_error}")
                    else:
                        raise Exception(f"OpenAI rate limit exceeded and no Gemini API key configured. Original error: {e}")
            
            # Re-raise original error if not a rate limit issue
            raise

    async def get_query_embedding(
        self, 
        query: str, 
        provider: str = "gemini",
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding for a single query with automatic fallback
        
        Args:
            query: Query text
            provider: "openai" or "gemini"
            model: Model name (optional)
            
        Returns:
            Single embedding vector
        """
        embeddings = await self.get_embeddings([query], provider, model)
        return embeddings[0] if embeddings else []

    def check_provider_availability(self, provider: str = "gemini") -> Dict[str, Any]:
        """
        Check if embedding provider is available and configured
        
        Args:
            provider: Provider to check ("openai" or "gemini")
            
        Returns:
            Dict with availability status and details
        """
        if provider.lower() == "gemini":
            if not settings.gemini_api_key:
                return {
                    "available": False,
                    "reason": "Gemini API key not configured",
                    "suggestion": "Please set GEMINI_API_KEY environment variable"
                }
            else:
                return {
                    "available": True,
                    "provider": "gemini",
                    "note": "Gemini API is configured"
                }
        elif provider.lower() == "openai":
            if not self.openai_client or not settings.openai_api_key or settings.openai_api_key.startswith('sk-test-'):
                return {
                    "available": False,
                    "reason": "OpenAI API key not configured or invalid",
                    "suggestion": "Please set a valid OPENAI_API_KEY environment variable"
                }
            else:
                return {
                    "available": True,
                    "provider": "openai",
                    "note": "OpenAI API is configured"
                }
        else:
            return {
                "available": False,
                "reason": f"Unsupported provider: {provider}",
                "suggestion": "Use 'openai' or 'gemini'"
            }

# Global embedding service instance
embedding_service = EmbeddingService()