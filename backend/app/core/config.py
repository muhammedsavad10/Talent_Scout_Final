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

import time
from groq import Groq

# Telemetry and LLM for ingestion.py
def add_timing(*args, **kwargs):
    pass

def call_llm(messages, temperature=0.0, response_format=None, max_tokens=800, stage="parsing"):
    if not getattr(settings, "GROQ_API_KEY", None):
        raise RuntimeError("GROQ_API_KEY not configured")
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    kwargs = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        kwargs["response_format"] = response_format
        
    start = time.time()
    try:
        response = client.chat.completions.create(**kwargs)
        result = response.choices[0].message.content
        record_llm_call(stage, time.time() - start)
        return result
    except Exception as e:
        logger.error(f"LLM Call Failed in {stage}: {e}")
        raise

def record_llm_call(*args, **kwargs):
    pass
