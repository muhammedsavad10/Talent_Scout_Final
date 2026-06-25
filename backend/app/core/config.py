"""
Core configuration module for TalentScout Enterprise.
Handles all environment variables and application settings.
"""
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    PROJECT_NAME: str = "TalentScout Multi-Agent API"
    VERSION: str = "1.0.0"
    
    # API Keys
    GROQ_API_KEY: str
    
    # Relational Database (Supabase / PostgreSQL)
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Vector Database (Qdrant)
    QDRANT_URL: str
    QDRANT_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
try:
    settings = Settings()
except Exception as e:
    logging.critical(f"Failed to load environment variables: {e}")
    raise

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("talentscout_core")
