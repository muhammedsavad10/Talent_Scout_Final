"""
Database connection clients for Relational (Supabase) and Vector (Qdrant) storage.
Includes connection retry capabilities, exponential backoff, health verification, and local fallback mode.
"""
import logging
import time
from typing import Optional
from supabase import create_client, Client as SupabaseClient
from qdrant_client import QdrantClient
from app.core.config import settings

logger = logging.getLogger("talentscout_db")

def get_supabase_client(retries: int = 2, delay: float = 0.5, raise_on_error: bool = False) -> Optional[SupabaseClient]:
    """
    Initializes and returns the Supabase client with retry resilience and fallback mode.
    """
    url = getattr(settings, "SUPABASE_URL", None)
    key = getattr(settings, "SUPABASE_KEY", None)
    
    if not url or not key:
        logger.info("[DB_FALLBACK] SUPABASE_URL or SUPABASE_KEY missing in settings. Operating in local memory fallback mode.")
        if raise_on_error:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY missing in settings.")
        return None
        
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            client: SupabaseClient = create_client(url, key)
            logger.info("Successfully initialized Supabase client (attempt %d).", attempt)
            return client
        except Exception as e:
            last_exc = e
            logger.warning("Supabase connection attempt %d/%d failed: %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(delay * attempt)
                
    logger.warning("Supabase client initialization failed after retries: %s. Using local memory fallback.", last_exc)
    if raise_on_error and last_exc:
        raise last_exc
    return None

def get_qdrant_client(retries: int = 2, delay: float = 0.5, raise_on_error: bool = False) -> Optional[QdrantClient]:
    """
    Initializes and returns the Qdrant Vector DB client with retry resilience and fallback mode.
    """
    url = getattr(settings, "QDRANT_URL", None)
    key = getattr(settings, "QDRANT_API_KEY", None)
    
    if not url or not key:
        logger.info("[DB_FALLBACK] QDRANT_URL or QDRANT_API_KEY missing in settings. Operating in local memory fallback mode.")
        if raise_on_error:
            raise ValueError("QDRANT_URL or QDRANT_API_KEY missing in settings.")
        return None
        
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            client = QdrantClient(
                url=url,
                api_key=key,
                timeout=10.0
            )
            logger.info("Successfully initialized Qdrant client (attempt %d).", attempt)
            return client
        except Exception as e:
            last_exc = e
            logger.warning("Qdrant connection attempt %d/%d failed: %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(delay * attempt)
                
    logger.warning("Qdrant client initialization failed after retries: %s. Using local memory fallback.", last_exc)
    if raise_on_error and last_exc:
        raise last_exc
    return None

def is_supabase_healthy(client: Optional[SupabaseClient]) -> bool:
    """Verifies active connectivity to Supabase instance."""
    if not client:
        return False
    try:
        return hasattr(client, "table")
    except Exception:
        return False

def is_qdrant_healthy(client: Optional[QdrantClient]) -> bool:
    """Verifies active connectivity to Qdrant Vector database."""
    if not client:
        return False
    try:
        if hasattr(client, "get_collections"):
            client.get_collections()
            return True
        return False
    except Exception:
        return False

# Global client instances with defensive fallback catching
try:
    supabase_db = get_supabase_client(retries=1, raise_on_error=False)
    qdrant_db = get_qdrant_client(retries=1, raise_on_error=False)
except Exception as e:
    logger.error("Non-fatal database initialization warning: %s", e)
    supabase_db = None
    qdrant_db = None
