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
from app.api.auth import router as auth_router

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://talent-scout-final-mocha.vercel.app",
    ],
    allow_origin_regex=r"https://talent-scout-final-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OWASP Security Headers & Observability Middleware (Phase C & H)
import uuid
import time
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse
from app.core.metrics import metrics_collector

DOC_ENDPOINTS = {"/docs", "/redoc", "/openapi.json"}

@app.middleware("http")
async def add_security_headers_and_observability(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    correlation_id = request.headers.get("X-Correlation-ID", request_id)
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    metrics_collector.record_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration
    )
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Route-scoped CSP: Allow jsDelivr CDN & inline scripts exclusively for OpenAPI Swagger/ReDoc pages
    if request.url.path in DOC_ENDPOINTS:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://cdn.jsdelivr.net https://fastapi.tiangolo.com;"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
    return response

# Register routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(ingest_router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(evaluate_router, prefix="/api/v1/evaluation", tags=["Evaluation Swarm"])
app.include_router(batch_evaluate_router, prefix="/api/v1/evaluate", tags=["Batch Evaluation"])

@app.get("/", tags=["Health Check"])
async def root():
    """
    Root endpoint to verify API health.
    """
    logger.info("Health check endpoint accessed.")
    return {"message": "Welcome to the TalentScout API Gateway", "status": "healthy"}

@app.get("/health/liveness", tags=["Health Check"])
async def liveness_probe():
    """
    Kubernetes / Docker liveness probe to verify application process status.
    """
    return {"status": "alive", "service": "talentscout-api"}

@app.get("/health/readiness", tags=["Health Check"])
async def readiness_probe():
    """
    Kubernetes / Docker readiness probe to verify service capacity to accept traffic.
    """
    try:
        from app.agents.decision_engine import validate_decision_configs
        validate_decision_configs()
        return {"status": "ready", "service": "talentscout-api"}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready.")

@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """
    Exposes Prometheus-formatted operational metrics.
    """
    return Response(
        content=metrics_collector.generate_prometheus_text(),
        media_type="text/plain; version=0.0.4"
    )

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
    from app.db.clients import get_supabase_client, get_qdrant_client
    
    supabase_status = "local_fallback"
    try:
        sp_client = get_supabase_client()
        if sp_client:
            supabase_status = "connected"
    except Exception as e:
        logger.warning(f"Supabase health probe check: {e}")

    qdrant_status = "local_fallback"
    collections_count = 0
    try:
        qd_client = get_qdrant_client()
        if qd_client and hasattr(qd_client, "get_collections"):
            collections = qd_client.get_collections()
            collections_count = len(collections.collections)
            qdrant_status = "connected"
    except Exception as e:
        logger.warning(f"Qdrant health probe check: {e}")

    return {
        "status": "healthy", 
        "supabase": supabase_status, 
        "qdrant": qdrant_status,
        "qdrant_collections": collections_count
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting up TalentScout Uvicorn server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
