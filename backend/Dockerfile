# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps for building some wheels (cryptography) and proper timezone data
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev tzdata && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first to leverage layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose default port
EXPOSE 8000

# Non-root user for security (optional)
RUN useradd -ms /bin/bash appuser
USER appuser

# Start the app (use module invocation to avoid PATH issues)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

