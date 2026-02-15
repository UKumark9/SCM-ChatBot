# SCM Chatbot - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Base image with Python and dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/train \
    data/business_docs \
    data/vector_index \
    logs

# Set permissions
RUN chmod -R 755 /app

# Expose Gradio default port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Default command - run the application
CMD ["python", "main.py", "--rag", "--agentic"]

# Alternative commands (uncomment as needed):
# CMD ["python", "main.py", "--enhanced"]  # Enhanced mode only
# CMD ["python", "main.py", "--no-rag"]    # Without RAG
