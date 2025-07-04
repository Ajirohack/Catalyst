# Multi-stage build for production optimization
FROM python:3.11-slim AS base

# Set environment variables for optimal Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libffi-dev \
    libpq-dev \
    postgresql-client \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    libtiff5-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    pkg-config \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies with improved error handling
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --timeout=600 -r requirements.txt \
    && pip install --no-cache-dir python-dotenv gunicorn

# Production stage
FROM base AS production

# Set production environment variables
ENV ENVIRONMENT=production \
    WORKERS=4

# Copy application code
COPY --chown=app:app . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/reports /app/storage /app/uploads \
    && chown -R app:app /app \
    && chmod -R 755 /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check with proper endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use gunicorn for production with optimized settings
CMD ["gunicorn", "main:app", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--workers", "4", \
    "--bind", "0.0.0.0:8000", \
    "--timeout", "120", \
    "--keep-alive", "5", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "100", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]

# Development stage
FROM base AS development

# Set development environment variables
ENV ENVIRONMENT=development \
    DEBUG=true \
    LOG_LEVEL=DEBUG

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-asyncio==0.21.1 \
    pytest-cov==4.1.0 \
    black==23.11.0 \
    flake8==6.1.0 \
    isort==5.12.0 \
    mypy==1.7.1 \
    pre-commit==3.5.0 \
    watchdog==3.0.0

# Copy application code
COPY --chown=app:app . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/reports /app/storage /app/uploads \
    && chown -R app:app /app \
    && chmod -R 755 /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Run with reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]