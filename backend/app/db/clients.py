"""
Database connection clients for Relational (Supabase) and Vector (Qdrant) storage.
"""
import logging
from supabase import create_client, Client as SupabaseClient
from qdrant_client import QdrantClient
from app.core.config import settings

logger = logging.getLogger("talentscout_db")

def get_supabase_client() -> SupabaseClient:
    """
    Initializes and returns the Supabase client.
    
    Returns:
        SupabaseClient: The active connection to the PostgreSQL database.
    """
    try:
        client: SupabaseClient = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Successfully initialized Supabase client.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise

def get_qdrant_client() -> QdrantClient:
    """
    Initializes and returns the Qdrant Vector DB client.
    
    Returns:
        QdrantClient: The active connection to the vector database.
    """
    try:
        client = QdrantClient(location=":memory:")
        logger.info("Successfully initialized Qdrant client in memory.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {e}")
        raise

# Instantiate globally for the application lifespan
try:
    supabase_db = get_supabase_client()
    qdrant_db = get_qdrant_client()
except Exception as e:
    logger.critical("Database initialization halted application startup.")
