# System Architecture

## High-Level Overview

```
                    +-------------------+
                    |   Gradio Web UI   |
                    |   (Port 7860)     |
                    +--------+----------+
                             |
                    +--------v----------+
                    |     main.py       |
                    |  SCMChatbotApp    |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
    +---------v---+  +-------v-------+  +---v-----------+
    | Multi-Agent |  |  Enhanced     |  |  Legacy       |
    |  Agentic    |  |  Single-LLM   |  |  Rule-Based   |
    |  Mode       |  |  Mode         |  |  Mode         |
    +------+------+  +-------+-------+  +---------------+
           |                 |
    +------v------+  +-------v-------+
    | Orchestrator|  | Groq API      |
    | (LangChain) |  | (Llama 3.3)   |
    +------+------+  +---------------+
           |
    +------v---------------------------+
    |  Specialized Agents              |
    |  +----------+ +----------------+ |
    |  | Delay    | | Analytics      | |
    |  +----------+ +----------------+ |
    |  +----------+ +----------------+ |
    |  | Forecast | | Data Query     | |
    |  +----------+ +----------------+ |
    +----------------------------------+
              |
    +---------v---------+
    |   RAG System      |
    |   FAISS + S-Trans  |
    +-------------------+
```

## Component Details

### 1. Entry Point (`main.py`)

`SCMChatbotApp` is the main application class. It:
- Loads and preprocesses 5 CSV datasets via `data/data_loader.py`
- Initializes the selected execution mode (Agentic, Enhanced, or Legacy)
- Sets up the RAG system if enabled
- Launches the Gradio web interface
- Handles command-line arguments (`--rag`, `--agentic`, `--enhanced`, `--no-rag`, `--show-agent`)

### 2. Multi-Agent System (`agents/`)

#### Orchestrator (`agents/orchestrator.py`)

The `AgentOrchestrator` is the central controller:
- Receives user queries
- Performs **intent detection** to classify query type
- Routes to the appropriate specialist agent
- Aggregates results from multiple agents for compound queries
- Maintains conversation history
- Falls back to Enhanced mode if agent execution fails

Intent categories:
- `delay` / `delivery` -- Delay Agent
- `revenue` / `sales` / `analytics` -- Analytics Agent
- `forecast` / `predict` / `demand` -- Forecasting Agent
- `data` / `query` / `lookup` -- Data Query Agent

#### Specialist Agents

Each agent extends `SCMAgent` and defines LangChain tools:

| Agent | File | Capabilities |
|-------|------|-------------|
| Delay Agent | `agents/delay_agent.py` | On-time/late rates, delay by state, delay trends, severity analysis |
| Analytics Agent | `agents/analytics_agent.py` | Revenue by customer/product/region, sales trends, customer segmentation |
| Forecasting Agent | `agents/forecasting_agent.py` | 30-day demand prediction, seasonal patterns, trend analysis |
| Data Query Agent | `agents/data_query_agent.py` | DataFrame filtering, aggregation, lookups, order/customer/product queries |

### 3. Enhanced Single-LLM Mode (`enhanced_chatbot.py`)

`EnhancedChatbot` provides direct LLM inference via the Groq API:
- Uses `PromptTemplates` with system prompts tuned for SCM analysis
- Implements **adaptive response complexity**:
  - Simple queries get concise factual answers
  - Moderate queries include 2-3 supporting data points
  - Complex queries receive full analysis with recommendations
- Converts data context (DataFrames, analytics results) to LLM-friendly text
- Integrates with RAG for document-grounded responses

### 4. RAG System (`rag.py`)

Two main classes:

**DocumentProcessor**
- Chunks text documents into overlapping segments (500 words, 100 overlap)
- Creates structured documents from CSV data (orders, customers, products)
- Processes PDF business policy documents

**RAGSystem**
- Generates embeddings using Sentence-Transformers (`all-MiniLM-L6-v2`, 384-dim)
- Stores vectors in a FAISS index for fast similarity search
- Retrieves top-K relevant documents for a query
- Provides retrieved context to the LLM for grounded answers

Vector index files in `data/vector_index/`:
- `index.faiss` -- FAISS index binary
- `embeddings.npy` -- Raw embedding vectors
- `documents.pkl` -- Serialized document store

### 5. Data Layer

**Data Loader** (`data/data_loader.py`)
- Loads 5 CSV files from `data/train/`
- Parses datetime columns
- Calculates derived fields: `is_delayed` (bool), `delay_days` (int)
- Returns Pandas DataFrames

**Training Datasets**:
| Dataset | Records | Key Fields |
|---------|---------|------------|
| Orders | ~89K | order_id, customer_id, status, timestamps, state |
| Customers | ~99K | customer_id, city, state, zip |
| Products | ~32K | product_id, category, weight, dimensions |
| OrderItems | ~113K | order_id, product_id, price, freight |
| Payments | ~104K | order_id, payment_type, installments, value |

**Business Documents** (`data/business_docs/`):
- Product Delay Management Policy
- Inventory Management Policy
- Supplier Quality Management Policy
- Transportation Logistics Policy
- Demand Forecasting Planning Policy
- SCM Policies (general)

### 6. Supporting Modules (`modules/`)

| Module | Purpose |
|--------|---------|
| `document_manager.py` | Upload and manage business documents, auto-vectorize for RAG |
| `feature_store.py` | Cache pre-computed ML features with TTL expiration (file-based or Redis) |
| `data_connectors.py` | Database connectors for PostgreSQL, MongoDB, MySQL |

### 7. Metrics & Evaluation

**MetricsTracker** (`metrics_tracker.py`)
- Records per-query metrics: latency, mode used, agent routed, response length
- Logs to `data/metrics_log.jsonl`
- Provides aggregate statistics

**RAG Evaluation** (`rag_evaluation.py`)
- Measures retrieval precision, recall, and relevance
- Validates answer faithfulness to source documents
- Outputs results to `data/rag_evaluation_results.json`

### 8. Analytics Tool (`tools/analytics.py`)

Core analytics engine providing:
- Delivery performance metrics
- Revenue analysis and breakdowns
- Customer segmentation
- Product category analysis
- Time-series trend computation

## Data Flow

```
User Query
    |
    v
Intent Detection (Orchestrator or Enhanced mode)
    |
    v
RAG Retrieval (if enabled)
    |--- Query embedded via Sentence-Transformers
    |--- FAISS similarity search
    |--- Top-K documents retrieved
    |
    v
Agent/LLM Processing
    |--- Data context from DataFrames
    |--- RAG context from retrieved documents
    |--- Prompt template with system instructions
    |
    v
Groq API (Llama 3.3 70B)
    |
    v
Response Formatting
    |--- Adaptive complexity
    |--- Metrics logged
    |
    v
Gradio UI Display
```

## Configuration Architecture

All settings are centralized in `config/config.py`:

- `LLM_CONFIG` -- Model name, temperature, max tokens
- `VECTOR_DB_CONFIG` -- Embedding model, dimensions, index path
- `RAG_CONFIG` -- Chunk size, overlap, top-K, similarity threshold
- `ANALYTICS_CONFIG` -- Delay thresholds, forecast periods
- `API_CONFIG` -- Host, port, secret key
- `UI_CONFIG` -- Title, description, theme
- `AGENT_CONFIG` -- Max iterations, timeout
- `EVAL_THRESHOLDS` -- Accuracy, MAPE, RMSE, latency, hallucination rate targets
