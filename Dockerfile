# ============================================================================
# VOLTA Enterprise AI Platform — Production Dockerfile
# Phase 7.8: Enterprise Deployment, Scaling & Operationalization
# ============================================================================

FROM python:3.11-slim AS base

# Build arguments
ARG PLATFORM_VERSION=7.8.0
ARG BUILD_DATE
ARG GIT_COMMIT

# Labels
LABEL org.opencontainers.image.title="VOLTA Enterprise AI Platform"
LABEL org.opencontainers.image.description="Enterprise AI Platform with 9-tier runtime stack (v7.0-v7.8)"
LABEL org.opencontainers.image.version="${PLATFORM_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.source="https://github.com/likith1502/volta-ai-chatbot"
LABEL org.opencontainers.image.licenses="MIT"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLATFORM_VERSION=${PLATFORM_VERSION}

# Create non-root user
RUN groupadd -r volta && useradd -r -g volta -d /app -s /bin/false volta

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Builder stage
# ============================================================================
FROM base AS builder

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Production stage
# ============================================================================
FROM base AS production

# Copy installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY backend/ .

# Create required directories
RUN mkdir -p /app/logs /app/data /app/backups \
    && chown -R volta:volta /app

# Switch to non-root user
USER volta

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "warning"]
