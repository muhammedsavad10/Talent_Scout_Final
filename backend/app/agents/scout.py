"""
Temporary reconstruction stub.

Reconstructed after Phase 5 data loss.

This implementation only restores application startup.

Full logic will be implemented in later reconstruction phases.
"""
import logging
import sys
from app.core.config import settings

logger = logging.getLogger(__name__)

class DummyEmbeddingModel:
    def __init__(self):
        self.device = "CPU"
    
    def get_sentence_embedding_dimension(self):
        return 384
        
    def encode(self, *args, **kwargs):
        raise RuntimeError(
            "SentenceTransformer unavailable. "
            "Semantic evaluation is disabled. "
            "Install dependencies before running production evaluations."
        )

try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    if settings.DEVELOPMENT_MODE:
        logger.warning(
            f"Could not load SentenceTransformer: {e}. "
            f"Using DummyEmbeddingModel for startup because DEVELOPMENT_MODE=True. "
            f"Semantic evaluations will fail."
        )
        embedding_model = DummyEmbeddingModel()
    else:
        logger.critical(f"Failed to load required AI components: {e}. Failing fast in production mode.")
        sys.exit(1)

def initialize_qdrant_collection():
    """
    Checks and initializes Qdrant collections.
    """
    logger.info("Reconstructed stub: initialize_qdrant_collection executed.")
    return True

def parse_resume_stub(text: str) -> dict:
    """
    Simulates the LLM parsing layer since LLM logic is excluded from C4A.
    Returns a structured dictionary representing the parsed resume based on keywords.
    """
    if "MALFORMED" in text:
        return {"error": "Malformed resume text"}
        
    if "IDEAL" in text:
        return {
            "personal_info": {"name": "Ideal Candidate"},
            "skills": {"languages": ["Python", "JavaScript"]},
            "hard_skills": ["FastAPI", "React", "Docker"],
            "work_history": [{}, {}, {}, {}], # 8 years
            "education": [{"degree": "B.S. Computer Science"}]
        }
    
    if "MISSING_MANDATORY" in text:
        return {
            "personal_info": {"name": "Missing Mandatory"},
            "skills": {"languages": ["Java"]},
            "hard_skills": ["Spring"],
            "work_history": [{}, {}, {}],
            "education": [{"degree": "B.S. Computer Science"}]
        }
        
    if "JUNIOR" in text:
        return {
            "personal_info": {"name": "Junior Candidate"},
            "skills": {"languages": ["Python"]},
            "hard_skills": [],
            "work_history": [{}], # 2 years
            "education": [{"degree": "B.S. Computer Science"}]
        }
        
    if "DUPLICATE" in text:
        return {
            "personal_info": {"name": "Duplicate Candidate"},
            "skills": {"languages": ["Python", "PYTHON", "python"]},
            "hard_skills": ["FastAPI", "fast-api"],
            "work_history": [{}, {}],
            "education": [{"degree": "B.S. Computer Science"}]
        }
        
    # Default Strong candidate missing preferred
    return {
        "personal_info": {"name": "Strong Default"},
        "skills": {"languages": ["Python"]},
        "hard_skills": ["Django"],
        "work_history": [{}, {}, {}],
        "education": [{"degree": "B.S. Computer Science"}]
    }
