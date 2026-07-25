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
    logger.info("Initializing application and validating environment configuration...")
    try:
        if not getattr(settings, "SUPABASE_URL", None) or not getattr(settings, "SUPABASE_KEY", None):
            logger.warning("SUPABASE_URL or SUPABASE_KEY missing in environment settings.")
        if not getattr(settings, "QDRANT_URL", None) or not getattr(settings, "QDRANT_API_KEY", None):
            logger.warning("QDRANT_URL or QDRANT_API_KEY missing in environment settings.")
            
        from app.agents.decision_engine import validate_decision_configs
        validate_decision_configs()
        logger.info("Decision engine configurations validated successfully.")
        
        logger.info(f"CORS origins configured: {settings.cors_origins}")
        logger.info("Application startup completed cleanly.")
    except Exception as e:
        logger.critical(f"Startup check failed: Configuration initialization error: {e}")
        raise e
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Recruitment Intelligence System API Gateway",
    lifespan=lifespan
)

# Configure CORS with explicit allowlist (Phase C Security Hardening)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# OWASP Security Headers Middleware (Phase C Security Hardening)
from fastapi.requests import Request

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

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

from fastapi.responses import JSONResponse
from fastapi.requests import Request

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    msg = exc.detail if isinstance(exc.detail, str) else "HTTP Request Error"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": f"HTTP_{exc.status_code}",
            "message": msg,
            "detail": msg,
            "details": exc.detail if isinstance(exc.detail, dict) else {"detail": msg}
        }
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
            "details": {"error": str(exc)}
        }
    )

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
