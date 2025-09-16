import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY")
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "fallback-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Default LLM Configuration
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    default_gemini_model: str = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.0-flash-exp")
    default_openai_model: str = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
    
    # Default Embedding Configuration
    default_embedding_provider: str = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "gemini")
    default_gemini_embedding_model: str = os.getenv("DEFAULT_GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    default_openai_embedding_model: str = os.getenv("DEFAULT_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # ChromaDB
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_data")
    
    # Server Configuration
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Rate Limiting Configuration
    max_chunks_per_document: int = int(os.getenv("MAX_CHUNKS_PER_DOCUMENT", "15"))
    embedding_batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "2"))
    embedding_delay_seconds: float = float(os.getenv("EMBEDDING_DELAY_SECONDS", "2.0"))

settings = Settings()