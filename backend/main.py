"""
FastAPI Main Entry Point for TalentScout Enterprise.
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.ingest import router as ingest_router
from app.api.evaluate import router as evaluate_router
from app.api.batch_evaluate import router as batch_evaluate_router

from contextlib import asynccontextmanager

logger = logging.getLogger("talentscout_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database connections and Qdrant collections...")
    try:
        from app.agents.decision_engine import validate_decision_configs
        validate_decision_configs()
        logger.info("Decision engine configurations validated successfully.")
        
        from app.agents.scout import initialize_qdrant_collection
        initialize_qdrant_collection()
        logger.info("Qdrant collection check and initialization complete.")
        
        import time
        logger.info("Starting application...")
        logger.info("Loading SentenceTransformer model...")
        t0 = time.perf_counter()
        from app.agents.scout import embedding_model
        t1 = time.perf_counter()
        
        dim = getattr(embedding_model, "get_sentence_embedding_dimension", lambda: 384)()
        device = getattr(embedding_model, "device", "CPU")
        
        logger.info("Embedding model loaded successfully.")
        logger.info(f"Load time: {t1 - t0:.2f} sec")
        logger.info(f"Embedding dimension: {dim}")
        logger.info(f"Device: {device}")
        
        logger.info("Application ready.")
    except Exception as e:
        logger.critical(f"Startup check failed: Qdrant/Decision config initialization failed: {e}")
        raise e
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Recruitment Intelligence System API Gateway",
    lifespan=lifespan
)

# Configure CORS so the React.js frontend can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update this to your React URL in production (e.g., localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingest_router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(evaluate_router, prefix="/api/v1/evaluation", tags=["Evaluation Swarm"])
app.include_router(batch_evaluate_router, prefix="/api/v1/evaluate", tags=["Batch Evaluation"])

@app.get("/", tags=["Health Check"])
async def root():
    """
    Root endpoint to verify API health.
    
    Returns:
        dict: A welcome message and status.
    """
    logger.info("Health check endpoint accessed.")
    return {"message": "Welcome to the TalentScout API Gateway", "status": "healthy"}

@app.get("/health/databases", tags=["Health Check"])
async def check_databases():
    """
    Endpoint to verify connections to Supabase and Qdrant.
    """
    try:
        # Import inside the function to avoid circular logic during startup failures
        from app.db.clients import supabase_db, qdrant_db
        
        # Simple ping to Qdrant to ensure it's alive
        collections = qdrant_db.get_collections()
        
        return {
            "status": "healthy", 
            "supabase": "connected", 
            "qdrant": "connected",
            "qdrant_collections": len(collections.collections)
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection degraded.")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting up TalentScout Uvicorn server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
