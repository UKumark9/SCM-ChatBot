# Deployment Guide

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Groq API key

### Build and Run

```bash
# Build the Docker image
docker build -t scm-chatbot .

# Run with environment variable
docker run -p 7860:7860 -e GROQ_API_KEY=your_key scm-chatbot
```

### Using Docker Compose

```bash
# Set API key in .env file
echo "GROQ_API_KEY=your_key" > .env

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f scm-chatbot

# Stop
docker-compose down
```

The application will be available at `http://localhost:7860`.

### Docker Configuration

**Dockerfile** -- Multi-stage build based on `python:3.11-slim`:
- Stage 1: Base image with system dependencies (gcc, g++, git, curl)
- Stage 2: Python dependency installation from `requirements.txt`
- Stage 3: Application code copy and directory setup
- Health check via curl on port 7860
- Default command: `python main.py --rag --agentic`

**docker-compose.yml** -- Service configuration:
- Maps port 7860 for Gradio UI
- Mounts `data/`, `logs/`, and `config/` as volumes for persistence
- Passes `GROQ_API_KEY` from `.env`
- Auto-restart policy: `unless-stopped`
- Health check with 30s interval

### Optional Services

The `docker-compose.yml` includes commented-out configurations for:

| Service | Port | Purpose |
|---------|------|---------|
| MongoDB | 27017 | Advanced data storage |
| Redis | 6379 | Feature store caching |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Monitoring dashboards |

Uncomment the relevant sections in `docker-compose.yml` to enable them.

## Manual Deployment

### Production Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_key
export PYTHONUNBUFFERED=1

# Build the FAISS index (first time only)
python vectorize_documents.py

# Start the application
python main.py --rag --agentic
```

### Running with Uvicorn (FastAPI)

If using the FastAPI backend directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## CI/CD Pipeline

The project includes a GitHub Actions workflow at `.github/workflows/ci-cd.yml` with 7 stages:

| Stage | Trigger | Description |
|-------|---------|-------------|
| Lint | All pushes/PRs | Black formatting + Flake8 linting |
| Test | After lint | pytest with coverage |
| RAG Validation | After test | RAG retrieval quality checks |
| Performance | After test | Response latency benchmarks |
| Docker Build | After tests pass | Container build verification |
| Deploy | Main branch only | Deployment to target environment |
| Release | Tagged commits | Release packaging |

### Branch Strategy

- `main` -- Production-ready code, triggers deploy
- `develop` -- Integration branch, runs full CI

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API authentication key |
| `PYTHONUNBUFFERED` | No | Set to `1` for real-time log output |

## Data Volumes

When deploying with Docker, ensure these directories persist between restarts:

| Volume Mount | Purpose |
|-------------|---------|
| `./data:/app/data` | Training data, vector index, business docs |
| `./logs:/app/logs` | Application logs |
| `./config:/app/config` | Configuration files |

## Health Checks

The Docker configuration includes a health check:

```
GET http://localhost:7860/
Interval: 30s
Timeout: 10s
Retries: 3
Start period: 40s
```

## Rebuilding the Vector Index

If business documents change, rebuild the FAISS index:

```bash
# Inside container
docker exec -it scm-chatbot python vectorize_documents.py

# Or rebuild index specifically
docker exec -it scm-chatbot python rebuild_index.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Container fails to start | Check `GROQ_API_KEY` is set in `.env` |
| Port 7860 already in use | Change port mapping in `docker-compose.yml` |
| Out of memory | Reduce `max_tokens` in `config/config.py` |
| Slow startup | First run downloads the Sentence-Transformers model (~90MB) |
| Vector index errors | Run `python rebuild_index.py` inside the container |
