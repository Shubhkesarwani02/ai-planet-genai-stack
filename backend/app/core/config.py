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
    
    # ChromaDB
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_data")
    
    # CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

settings = Settings()