"""
Core configuration module for TalentScout Enterprise.
Handles all environment variables and application settings.
"""
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    PROJECT_NAME: str = "TalentScout Multi-Agent API"
    VERSION: str = "1.0.0"
    
    # API Keys
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # AI Gateway Settings
    PRIMARY_EXTRACTION_PROVIDER: str = "gemini"
    PRIMARY_GENERATION_PROVIDER: str = "gemini"
    PRIMARY_ASSISTANT_PROVIDER: str = "gemini"
    MAX_CONCURRENT_REQUESTS: int = 3
    MAX_RETRIES: int = 2
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

    # Security & CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        """Returns parsed list of allowed CORS origins."""
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return origins if origins else ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
            ".env",
            "talent_scout_enterprise/backend/.env"
        ),
        case_sensitive=True,
        extra="allow"
    )

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
    
    if stage in ["assistant_ask", "copilot_assistant"]:
        task_type = "assistant"
    elif stage in ["interview_generation", "feedback_generation", "summary_generation"]:
        task_type = "generation"
    else:
        task_type = "extraction"

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
