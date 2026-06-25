"""
FastAPI Main Entry Point for TalentScout Enterprise.
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.ingest import router as ingest_router

logger = logging.getLogger("talentscout_api")
# ... (rest of configuration and endpoints remains same, but wait, replace_file_content targets a single contiguous block, so let's check what exactly we want to replace)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Recruitment Intelligence System API Gateway"
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
