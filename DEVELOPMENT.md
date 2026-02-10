# Development Guide

## Environment Setup

### Requirements

- Python 3.11+
- pip 23+
- Git
- Groq API key

### Initial Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install all dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

Edit `.env` and set your Groq API key:

```
GROQ_API_KEY=your_api_key_here
```

### Verifying the Setup

```bash
# Check that imports work
python -c "import langchain; import groq; import faiss; print('All imports OK')"

# Run the application
python main.py
```

## Project Layout

| Directory | Purpose |
|-----------|---------|
| `agents/` | Multi-agent system -- orchestrator and 4 specialist agents |
| `config/` | Centralized configuration (LLM, RAG, API, analytics settings) |
| `data/` | Data loader, training CSVs, business docs, vector index |
| `modules/` | Supporting modules -- document manager, feature store, DB connectors |
| `tests/` | Test suite (pytest) |
| `tools/` | Analytics tool implementation |

### Key Source Files

| File | Description |
|------|-------------|
| `main.py` | Entry point. Initializes `SCMChatbotApp`, loads data, sets up Gradio UI |
| `enhanced_chatbot.py` | Single-LLM mode with Groq API, prompt templates, adaptive responses |
| `rag.py` | RAG module -- `DocumentProcessor` for chunking, `RAGSystem` for FAISS search |
| `rag_evaluation.py` | RAG quality metrics and evaluation framework |
| `metrics_tracker.py` | `MetricsTracker` class for recording query performance |
| `agents/orchestrator.py` | `AgentOrchestrator` -- intent detection, agent routing, result aggregation |
| `agents/delay_agent.py` | Delivery delay analysis with LangChain tool calling |
| `agents/analytics_agent.py` | Revenue and customer analytics agent |
| `agents/forecasting_agent.py` | Demand forecasting with time-series analysis |
| `agents/data_query_agent.py` | Raw DataFrame query agent |
| `config/config.py` | All configuration constants (LLM, vector DB, RAG, API, UI settings) |
| `data/data_loader.py` | CSV loading, datetime preprocessing, delay calculation |

## Configuration

All configuration is centralized in `config/config.py`:

```python
# LLM settings
LLM_CONFIG = {
    "provider": "groq",
    "model_name": "llama3-70b-8192",
    "temperature": 0.1,
    "max_tokens": 4096,
}

# RAG settings
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k": 5,
    "similarity_threshold": 0.7,
}

# Analytics thresholds
ANALYTICS_CONFIG = {
    "delay_threshold_days": 5,
    "forecast_periods": 30,
}
```

## Adding a New Agent

1. Create a new file in `agents/` (e.g., `agents/inventory_agent.py`)
2. Extend the base `SCMAgent` from `agents/scm_agent.py`
3. Define LangChain tools for the agent's capabilities
4. Register the agent in `agents/orchestrator.py`:
   - Add intent keywords to the routing logic
   - Initialize the agent in `AgentOrchestrator.__init__`
5. Add tests in `tests/`

## Adding New Data Sources

1. Place CSV files in `data/train/`
2. Update `data/data_loader.py` to load and preprocess the new data
3. Update `main.py` to pass the new data to relevant agents
4. For RAG documents, place PDFs in `data/business_docs/` and run:

```bash
python vectorize_documents.py
```

## Code Style

- **Formatter**: Black (`black --line-length 127`)
- **Linter**: Flake8 (`flake8 --max-line-length 127`)
- **Type checking**: mypy (optional)

```bash
# Format code
black .

# Lint
flake8 . --max-line-length=127

# Type check
mypy main.py enhanced_chatbot.py rag.py
```

## Common Development Tasks

### Rebuild the FAISS Vector Index

```bash
python rebuild_index.py
```

### Vectorize New Documents

```bash
python vectorize_documents.py
```

### Run with Debug Logging

```bash
python main.py --rag --agentic 2>&1 | tee debug.log
```

## Dependencies

Core dependencies from `requirements.txt`:

| Category | Packages |
|----------|----------|
| Data | pandas, numpy, scikit-learn |
| LLM | langchain, langchain-groq, groq |
| Embeddings | sentence-transformers, faiss-cpu |
| Web | fastapi, uvicorn, gradio |
| Visualization | matplotlib, seaborn, plotly |
| Utilities | python-dotenv, tqdm, requests |
| Testing | pytest, pytest-cov, pytest-asyncio |

### Optional Dependencies (commented in requirements.txt)

- `PyPDF2` -- PDF document processing
- `python-docx` -- DOCX document support
- `sqlalchemy`, `psycopg2-binary`, `pymongo`, `pymysql` -- Database connectors
- `redis` -- Distributed feature store cache
