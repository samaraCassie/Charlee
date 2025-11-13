# Multi-stage Dockerfile for Charlee Backend
# Optimized for production deployment

# ========================================
# Stage 1: Builder
# ========================================
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir --user -r backend/requirements.txt

# ========================================
# Stage 2: Runtime
# ========================================
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 charlee && \
    mkdir -p /app && \
    chown -R charlee:charlee /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=charlee:charlee /root/.local /root/.local

# Copy application code
COPY --chown=charlee:charlee . .

# Switch to non-root user
USER charlee

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
