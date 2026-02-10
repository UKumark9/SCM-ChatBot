# AI-Powered Supply Chain Management Chatbot

An intelligent conversational interface for supply chain analytics, built with Python, LangChain, Groq API, and FAISS-based RAG.

## Features

- **Multi-Agent Mode** -- 4 specialized LangChain agents (Delay, Analytics, Forecasting, Data Query) with intelligent routing
- **Enhanced Single-LLM Mode** -- Direct Groq API inference with adaptive response complexity
- **RAG System** -- Retrieval-Augmented Generation using FAISS + Sentence-Transformers for document-grounded answers
- **Gradio Web UI** -- Interactive chat interface with mode switching on port 7860
- **Metrics Tracking** -- Built-in performance monitoring and query analytics

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Groq API (Llama 3.3 70B) |
| Agent Framework | LangChain + langchain-groq |
| Vector Search | FAISS (CPU) |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| UI | Gradio 4.0+ |
| Backend | FastAPI + Uvicorn |
| Data | Pandas, NumPy, Scikit-learn |
| Containerization | Docker + Docker Compose |

## Quick Start

### Prerequisites

- Python 3.11+
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd scm_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the Application

```bash
# Default mode (Enhanced + RAG)
python main.py

# Multi-Agent Agentic mode with RAG
python main.py --rag --agentic

# Enhanced mode only (no RAG)
python main.py --enhanced --no-rag

# Show agent routing info
python main.py --show-agent
```

The Gradio UI will be available at `http://localhost:7860`.

## Project Structure

```
scm_chatbot/
├── main.py                  # Application entry point
├── enhanced_chatbot.py      # Single-LLM enhanced mode
├── rag.py                   # RAG module (FAISS + embeddings)
├── rag_evaluation.py        # RAG evaluation metrics
├── metrics_tracker.py       # Performance tracking
├── vectorize_documents.py   # Document vectorization utility
├── rebuild_index.py         # FAISS index rebuild utility
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker build configuration
├── docker-compose.yml       # Docker Compose services
├── agents/
│   ├── orchestrator.py      # Agent routing & coordination
│   ├── delay_agent.py       # Delivery delay analysis
│   ├── analytics_agent.py   # Revenue & performance analytics
│   ├── forecasting_agent.py # Demand forecasting
│   ├── data_query_agent.py  # Raw data access
│   └── scm_agent.py         # Base agent class
├── config/
│   └── config.py            # Centralized configuration
├── data/
│   ├── data_loader.py       # CSV data loading & preprocessing
│   ├── train/               # Training CSV datasets
│   ├── business_docs/       # PDF policy documents for RAG
│   └── vector_index/        # FAISS index files
├── modules/
│   ├── document_manager.py  # Document upload & vectorization
│   ├── feature_store.py     # ML feature caching
│   └── data_connectors.py   # Database connectors
├── tests/                   # Test suite
└── tools/
    └── analytics.py         # Analytics tool implementation
```

## Execution Modes

### 1. Multi-Agent Agentic Mode (`--agentic`)
Routes queries to specialized agents via LangChain orchestration:
- **Delay Agent** -- Delivery performance, delay rates, regional analysis
- **Analytics Agent** -- Revenue trends, customer metrics, sales data
- **Forecasting Agent** -- Demand predictions, seasonal patterns
- **Data Query Agent** -- Direct data lookups, filtering, aggregation

### 2. Enhanced Single-LLM Mode (`--enhanced`)
Direct Groq API inference with adaptive response complexity:
- **Simple** -- Direct factual answers
- **Moderate** -- Answer with supporting data points
- **Complex** -- Full analysis with recommendations

### 3. Legacy Rule-Based Mode
Keyword-based pattern matching (works offline, no API required).

## Data

The system uses 5 CSV datasets in `data/train/`:
- `df_Orders.csv` -- Order records with timestamps and status
- `df_Customers.csv` -- Customer information and locations
- `df_Products.csv` -- Product catalog
- `df_OrderItems.csv` -- Order line items
- `df_Payments.csv` -- Payment records

Business policy PDFs in `data/business_docs/` are used for RAG-grounded answers.

## Documentation

- [DEVELOPMENT.md](DEVELOPMENT.md) -- Development setup, code style, and contribution guide
- [TESTING.md](TESTING.md) -- Test suite overview and how to run tests
- [ARCHITECTURE.md](ARCHITECTURE.md) -- System architecture and design decisions
- [DEPLOYMENT.md](DEPLOYMENT.md) -- Docker deployment and production setup
- [API_REFERENCE.md](API_REFERENCE.md) -- Configuration reference and API details

## License

See [LICENSE](LICENSE) for details.
