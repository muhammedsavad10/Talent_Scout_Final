"""
Core configuration module for TalentScout Enterprise.
Handles all environment variables and application settings.
"""
import logging
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    PROJECT_NAME: str = "TalentScout Multi-Agent API"
    VERSION: str = "1.0.0"
    
    # API Keys
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # AI Gateway Settings
    PRIMARY_EXTRACTION_PROVIDER: str = "gemini"
    PRIMARY_GENERATION_PROVIDER: str = "groq"
    MAX_CONCURRENT_REQUESTS: int = 3
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: float = 30.0
    ENABLE_PROVIDER_FALLBACK: bool = True
    
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

# Telemetry and LLM for ingestion.py
def add_timing(*args, **kwargs):
    pass

def call_llm(messages, temperature=0.0, response_format=None, max_tokens=800, stage="parsing"):
    """
    Backward-compatibility wrapper delegating all calls through the central AIGateway.
    """
    from app.services.ai_gateway import ai_gateway
    
    task_type = "generation" if stage in ["interview_generation", "feedback_generation", "summary_generation", "copilot_assistant"] else "extraction"
    return ai_gateway.execute_request(
        messages=messages,
        temperature=temperature,
        response_format=response_format,
        max_tokens=max_tokens,
        stage=stage,
        task_type=task_type
    )

def record_llm_call(*args, **kwargs):
    pass
