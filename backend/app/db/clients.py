"""
Database connection clients for Relational (Supabase) and Vector (Qdrant) storage.
Includes connection retry capabilities, timeout enforcement, and local fallback mode.
"""
import logging
import time
from typing import Optional
from supabase import create_client, Client as SupabaseClient
from qdrant_client import QdrantClient
from app.core.config import settings

logger = logging.getLogger("talentscout_db")

def get_supabase_client(retries: int = 1, delay: float = 0.5, raise_on_error: bool = True) -> Optional[SupabaseClient]:
    """
    Initializes and returns the Supabase client. Re-raises Exception if initialization fails.
    """
    url = getattr(settings, "SUPABASE_URL", None)
    key = getattr(settings, "SUPABASE_KEY", None)
    
    if not url or not key:
        logger.warning("SUPABASE_URL or SUPABASE_KEY missing in settings.")
        if raise_on_error:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY missing in settings.")
        return None
        
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            client: SupabaseClient = create_client(url, key)
            logger.info("Successfully initialized Supabase client.")
            return client
        except Exception as e:
            last_exc = e
            logger.warning(f"Supabase connection attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(delay * attempt)
                
    logger.error(f"Supabase client initialization failed after retries: {last_exc}")
    if raise_on_error and last_exc:
        raise last_exc
    return None

def get_qdrant_client(retries: int = 1, delay: float = 0.5, raise_on_error: bool = True) -> Optional[QdrantClient]:
    """
    Initializes and returns the Qdrant Vector DB client. Re-raises Exception if initialization fails.
    """
    url = getattr(settings, "QDRANT_URL", None)
    key = getattr(settings, "QDRANT_API_KEY", None)
    
    if not url or not key:
        logger.warning("QDRANT_URL or QDRANT_API_KEY missing in settings.")
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
            logger.info("Successfully initialized Qdrant client.")
            return client
        except Exception as e:
            last_exc = e
            logger.warning(f"Qdrant connection attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(delay * attempt)
                
    logger.error(f"Qdrant client initialization failed after retries: {last_exc}")
    if raise_on_error and last_exc:
        raise last_exc
    return None

# Global client instances with defensive error catching
try:
    supabase_db = get_supabase_client(retries=1, raise_on_error=False)
    qdrant_db = get_qdrant_client(retries=1, raise_on_error=False)
except Exception as e:
    logger.error(f"Non-fatal database initialization warning: {e}")
    supabase_db = None
    qdrant_db = None

