"""
Configuration settings for the RAG application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Vector Database Settings
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Document Processing Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Application Settings
    APP_TITLE = os.getenv("APP_TITLE", "RAG AI Application")
    APP_PORT = int(os.getenv("APP_PORT", "8501"))
    
    # Supported File Types
    SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]
    
    # UI Settings
    MAX_FILE_SIZE_MB = 10
    RETRIEVAL_TOP_K = 3


# Create config instance
config = Config()
