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
    
    # Development Flags
    DEVELOPMENT_MODE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

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

# Telemetry and LLM stubs for ingestion.py compatibility
def add_timing(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def call_llm(*args, **kwargs):
    pass

def record_llm_call(*args, **kwargs):
    pass
