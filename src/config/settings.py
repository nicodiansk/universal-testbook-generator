"""
Configuration settings for the Universal Testbook Generator.
"""

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    default_llm: str = os.getenv("DEFAULT_LLM", "gpt-4o-mini")
    default_embedding_model: str = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Pinecone Configuration
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp-free")
    
    # Application Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    max_conversation_history: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
    
    # Streamlit Configuration
    streamlit_server_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    streamlit_server_address: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    max_upload_size: str = os.getenv("MAX_UPLOAD_SIZE", "200MB")
    
    def validate_api_keys(self) -> bool:
        """Validate that required API keys are set."""
        return bool(self.openai_api_key and self.pinecone_api_key)

# Create global settings instance
settings = Settings()