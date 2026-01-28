import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # API Keys
    openai_api_key: str | None = None
    groq_api_key: str
    
    # LLM Configuration
    llm_provider: Literal["groq", "openai"] = "groq"
    llm_model: str = "llama-3.1-70b-versatile"
    
    # Whisper Configuration
    whisper_model: Literal["tiny", "base", "small", "medium", "large"] = "base"
    use_whisper_api: bool = False
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Database Paths
    chroma_path: str = "./chroma_data"
    sqlite_db_path: str = "./data/videos.db"
    
    # Chunking Configuration
    chunk_size: int = 300
    chunk_overlap: int = 50
    
    # Retrieval Configuration
    top_k_results: int = 20
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    environment: Literal["development", "production"] = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
    
    def get_database_dir(self) -> Path:
        """Ensure database directory exists"""
        db_path = Path(self.sqlite_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path.parent
    
    def get_chroma_dir(self) -> Path:
        """Ensure ChromaDB directory exists"""
        chroma_dir = Path(self.chroma_path)
        chroma_dir.mkdir(parents=True, exist_ok=True)
        return chroma_dir


# Singleton instance
settings = Settings()
