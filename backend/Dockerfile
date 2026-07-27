# ==============================================================================
# Production Multi-Stage Dockerfile for TalentScout Enterprise FastAPI Backend
# Deployment Target: Google Cloud Run (Containerized Serverless Compute)
# Base Image: Python 3.10 Slim
# Verified Entrypoint: main:app (main.py at backend root)
# Verified Healthcheck: /health/liveness (explicitly registered in main.py)
# ==============================================================================

# ------------------------------------------------------------------------------
# STAGE 1: Builder Stage (Dependency Pre-Installation)
# ------------------------------------------------------------------------------
FROM python:3.10-slim AS builder

# Set working directory inside builder container
WORKDIR /app

# Configure build-time environment flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1

# Install runtime utility (curl for healthcheck validation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first to optimize Docker layer caching
COPY requirements.txt .

# Pre-install wheel packages into user local directory (/root/.local)
RUN pip install --user --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# STAGE 2: Production Runner Stage (Minimal Runtime Image)
# ------------------------------------------------------------------------------
FROM python:3.10-slim AS runner

# Set working directory for production application
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

# Execute Uvicorn server referencing verified main:app entrypoint
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
