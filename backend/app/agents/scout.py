"""
Temporary reconstruction stub.

Reconstructed after Phase 5 data loss.

This implementation only restores application startup.

Full logic will be implemented in later reconstruction phases.
"""
import logging
import sys
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings
from app.db.clients import qdrant_db

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    logger.critical(f"Failed to load required AI components: {e}. Failing fast.")
    sys.exit(1)

def initialize_qdrant_collection():
    """
    Checks and initializes Qdrant collections.
    """
    collection_name = "resumes"
    try:
        collections_response = qdrant_db.get_collections()
        collections = collections_response.collections
        
        if not any(c.name == collection_name for c in collections):
            qdrant_db.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection '{collection_name}'.")
        else:
            logger.info(f"Qdrant collection '{collection_name}' already exists.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {e}")
        raise

def get_embedding(text: str) -> list[float]:
    """Generates embeddings using the loaded SentenceTransformer."""
    return embedding_model.encode(text).tolist()

def index_resume(evaluation_id: str, text: str, metadata: dict = None):
    """Upserts the resume into Qdrant."""
    from qdrant_client.models import PointStruct
    vector = get_embedding(text)
    # Using a deterministic UUID generation or hash for id could be needed, but we'll use string hash or evaluation_id if it's integer/uuid
    # Qdrant accepts UUID string or integer for id.
    import uuid
    try:
        point_id = str(uuid.UUID(evaluation_id))
    except ValueError:
        import hashlib
        point_id = str(uuid.UUID(hashlib.md5(evaluation_id.encode()).hexdigest()))
        
    point = PointStruct(id=point_id, vector=vector, payload=metadata or {})
    qdrant_db.upsert(collection_name="resumes", points=[point])
    
def semantic_search(query: str, limit: int = 5):
    """Performs a semantic search on the resumes collection."""
    vector = get_embedding(query)
    results = qdrant_db.query_points(
        collection_name="resumes",
        query=vector,
        limit=limit
    )
    return getattr(results, "points", results)

