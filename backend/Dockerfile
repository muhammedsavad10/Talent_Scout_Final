# ==============================================================================
# Production Multi-Stage Dockerfile for TalentScout Enterprise FastAPI Backend
# Deployment Target: Google Cloud Run (Containerized Serverless Compute)
# Base Image: Python 3.10 Slim
# Security: OWASP Non-Root Execution (appuser:appgroup 999:999)
# Optimization: Single-Pass CPU-Only PyTorch Installation & Layered Cache
# ==============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder Stage (Dependency Pre-Installation)
# ------------------------------------------------------------------------------
FROM python:3.10-slim AS builder

WORKDIR /app

# Configure build-time environment flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1

# Install runtime utilities (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first to maximize Docker layer caching
COPY requirements.txt .

# Pre-install dependencies in a single layer using python -m pip with CPU-only PyTorch index
RUN python -m pip install --upgrade pip && \
    python -m pip install --user --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# STAGE 2: Production Runner Stage (Minimal Runtime Image)
# ------------------------------------------------------------------------------
FROM python:3.10-slim AS runner

WORKDIR /app

# Production environment configuration for Google Cloud Run
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PORT=8080 \
    PATH=/home/appuser/.local/bin:$PATH

# Install curl in runner stage for container healthcheck probe
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system group and user for OWASP container security
RUN groupadd -g 999 appgroup && \
    useradd -r -u 999 -g appgroup appuser && \
    mkdir -p /home/appuser /app && \
    chown -R appuser:appgroup /home/appuser /app

# Copy pre-installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source code with non-root user ownership
COPY --chown=appuser:appgroup . /app

# Switch execution context to non-root user
USER appuser

# Expose default Google Cloud Run port
EXPOSE 8080

# Healthcheck probe querying verified /health/liveness endpoint in main.py
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/health/liveness || exit 1

# Execute Uvicorn server using exec form to pass OS signals (SIGTERM/SIGINT) cleanly
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
