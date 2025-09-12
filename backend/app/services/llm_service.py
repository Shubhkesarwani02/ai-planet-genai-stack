import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Configure APIs
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def generate_openai_response(
        self,
        query: str,
        context_chunks: List[str],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using OpenAI GPT models
        
        Args:
            query: User query
            context_chunks: Relevant context from knowledge base
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        try:
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            
            # Build context
            context_text = "\n\n".join(context_chunks) if context_chunks else ""
            
            # Create system prompt
            system_prompt = """You are a helpful AI assistant that answers questions based on the provided context. 
            
Rules:
1. Use the context provided to answer the question accurately
2. If the answer is not in the context, say "I don't have enough information to answer that question based on the provided context"
3. Be concise but comprehensive
4. Cite relevant parts of the context when possible
5. If the context is empty, politely explain that no relevant information was found"""
            
            # Create user prompt
            if context_text:
                user_prompt = f"""Context:
{context_text}

Question: {query}

Please answer the question based on the context provided above."""
            else:
                user_prompt = f"""No relevant context was found for this question.

Question: {query}

Please provide a helpful response explaining that you don't have specific information about this topic in the knowledge base."""
            
            def _generate_response():
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(self.executor, _generate_response)
            
            logger.info(f"Generated OpenAI response for query: {query[:100]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise
    
    async def generate_gemini_response(
        self,
        query: str,
        context_chunks: List[str],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using Google Gemini models
        
        Args:
            query: User query
            context_chunks: Relevant context from knowledge base
            model: Gemini model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        try:
            if not settings.gemini_api_key:
                raise Exception("Gemini API key not configured")
            
            # Build context
            context_text = "\n\n".join(context_chunks) if context_chunks else ""
            
            # Create prompt
            if context_text:
                prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context.

Context:
{context_text}

Question: {query}

Instructions:
- Use the context to provide an accurate answer
- If the answer isn't in the context, say so clearly
- Be helpful and concise
- Cite relevant parts when applicable

Answer:"""
            else:
                prompt = f"""Question: {query}

I don't have specific context or documents to reference for this question. Please provide a helpful general response or explain what information would be needed to answer this properly."""
            
            def _generate_response():
                model_instance = genai.GenerativeModel(
                    model_name=model,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )
                response = model_instance.generate_content(prompt)
                return response.text
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(self.executor, _generate_response)
            
            logger.info(f"Generated Gemini response for query: {query[:100]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            raise
    
    async def generate_response(
        self,
        query: str,
        context_chunks: List[str],
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response using specified provider
        
        Args:
            query: User query
            context_chunks: Relevant context from knowledge base
            provider: "openai" or "gemini"
            model: Model name (optional, uses defaults)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if provider.lower() == "openai":
            model = model or "gpt-4o-mini"
            return await self.generate_openai_response(
                query, context_chunks, model, temperature, max_tokens
            )
        elif provider.lower() == "gemini":
            model = model or "gemini-2.0-flash-exp"
            return await self.generate_gemini_response(
                query, context_chunks, model, temperature, max_tokens
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

# Global LLM service instance
llm_service = LLMService()