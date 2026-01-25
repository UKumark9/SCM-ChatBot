# 📚 SCM Chatbot - Developer Handbook

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Installation & Setup](#3-installation--setup)
4. [Component Deep Dive](#4-component-deep-dive)
5. [Development Guidelines](#5-development-guidelines)
6. [API Reference](#6-api-reference)
7. [Testing Strategy](#7-testing-strategy)
8. [Deployment](#8-deployment)
9. [Troubleshooting](#9-troubleshooting)
10. [Performance Optimization](#10-performance-optimization)
11. [Future Enhancements](#11-future-enhancements)

---

## 1. Introduction

### 1.1 Project Overview

The Supply Chain Management (SCM) Chatbot is an AI-powered conversational interface designed to provide intelligent insights into supply chain operations. It leverages modern NLP techniques, agentic AI, and retrieval-augmented generation to answer complex queries about:

- Order delivery performance
- Revenue and financial metrics
- Inventory management
- Demand forecasting
- Supplier performance

### 1.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| LLM | Groq (Llama 3 70B) | Natural language understanding |
| Agent Framework | LangChain | Orchestration and tool calling |
| Vector DB | FAISS | Semantic search |
| Embeddings | SentenceTransformers | Document encoding |
| Data Processing | Pandas, NumPy | Data manipulation |
| UI | Gradio | Web interface |
| API | FastAPI (optional) | REST endpoints |

### 1.3 Key Features

- **Agentic AI**: Multi-agent system with specialized tools
- **RAG**: Grounded responses using knowledge base
- **Real-time Analytics**: Instant insights from data
- **Scalable**: Handles large datasets efficiently
- **Extensible**: Easy to add new capabilities

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                       │
│                    (Gradio UI / CLI)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  LANGCHAIN AGENT ORCHESTRATOR               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │Query Parser  │→ │Tool Selector │→ │Response Gen  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────┬────────┬────────┬────────┬────────┬─────────────────┘
     │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────────┐
│ Delay  ││Revenue ││Inventory││Forecast││    RAG     │
│Analytics││Analytics││Analytics││ Module ││   Module   │
└────────┘└────────┘└────────┘└────────┘└─────┬──────┘
                                              │
                                     ┌────────▼────────┐
                                     │  Vector Database │
                                     │     (FAISS)     │
                                     └─────────────────┘
                                              ▲
                                              │
                                     ┌────────┴────────┐
                                     │ Embedding Model │
                                     │ (SentenceTrans) │
                                     └─────────────────┘
```

### 2.2 Component Responsibilities

#### 2.2.1 User Interface Module
- **Purpose**: Provide interaction layer for users
- **Implementation**: Gradio web UI and CLI
- **Inputs**: Natural language queries
- **Outputs**: Formatted responses with metrics

#### 2.2.2 LangChain Agent Orchestrator
- **Purpose**: Central controller and decision maker
- **Key Responsibilities**:
  - Parse and understand user queries
  - Select appropriate tools
  - Execute multi-step reasoning
  - Synthesize responses
- **Implementation**: `agents/scm_agent.py`

#### 2.2.3 Analytics Modules
- **Purpose**: Perform specialized supply chain analysis
- **Modules**:
  - `DelayAnalytics`: Delivery performance
  - `RevenueAnalytics`: Financial metrics
  - `InventoryAnalytics`: Stock management
  - `DemandForecasting`: Predictive analytics
  - `SupplierAnalytics`: Vendor performance

#### 2.2.4 RAG Module
- **Purpose**: Retrieve relevant context for queries
- **Components**:
  - Document chunker
  - Embedding generator
  - Vector database (FAISS)
  - Semantic search

#### 2.2.5 Data Layer
- **Purpose**: Load and preprocess datasets
- **Implementation**: `data/data_loader.py`
- **Capabilities**:
  - CSV loading
  - Data cleaning
  - Feature engineering
  - Synthetic data generation

---

## 3. Installation & Setup

### 3.1 System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 2GB
- Python: 3.8+

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 5GB
- GPU: Optional for faster embeddings

### 3.2 Installation Steps

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd scm_chatbot
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
EOF
```

#### Step 5: Verify Installation
```bash
python -c "import langchain; import faiss; print('✅ Installation successful')"
```

### 3.3 First Run

```bash
# CLI mode
python main.py --mode cli --data train

# Web UI mode
python main.py --mode ui --data train

# Without LangChain (fallback)
python main.py --mode cli --no-langchain
```

---

## 4. Component Deep Dive

### 4.1 Data Loader (`data/data_loader.py`)

#### Purpose
Handles all data loading, preprocessing, and synthetic data generation.

#### Key Classes

**SCMDataLoader**
```python
class SCMDataLoader:
    def __init__(self, dataset_paths: Dict[str, str])
    def load_all_data() -> Tuple
    def merge_order_data() -> pd.DataFrame
    def get_data_summary() -> Dict
```

**Usage Example:**
```python
from data.data_loader import SCMDataLoader

loader = SCMDataLoader(DATASET_PATHS['train'])
orders, customers, products, items, payments = loader.load_all_data()
summary = loader.get_data_summary()
```

**DataSynthesizer**
```python
class DataSynthesizer:
    @staticmethod
    def generate_supplier_data(n_suppliers: int) -> pd.DataFrame
    
    @staticmethod
    def generate_inventory_data(products_df: pd.DataFrame) -> pd.DataFrame
    
    @staticmethod
    def generate_demand_forecast(orders_df: pd.DataFrame) -> pd.DataFrame
```

### 4.2 RAG Module (`models/rag_module.py`)

#### Architecture
```
User Query → Embedding → FAISS Search → Top-K Documents → Context
```

#### Key Classes

**VectorDatabase**
```python
class VectorDatabase:
    def __init__(self, embedding_model: str, dimension: int)
    def create_index()
    def add_documents(documents: List[Dict])
    def search(query: str, top_k: int) -> List[Dict]
    def save(path: str)
    def load(path: str)
```

**RAGModule**
```python
class RAGModule:
    def __init__(self, config: Dict)
    def build_knowledge_base(orders_df, products_df, customers_df)
    def retrieve(query: str, top_k: int) -> List[Dict]
```

**Usage Example:**
```python
from models.rag_module import RAGModule

rag = RAGModule(VECTOR_DB_CONFIG)
rag.build_knowledge_base(orders, products, customers)
results = rag.retrieve("Order O123", top_k=5)
```

#### Document Chunking Strategy

Documents are split using overlapping windows:
- Chunk size: 500 characters
- Overlap: 50 characters
- Preserves context across chunks

### 4.3 Analytics Tools (`tools/analytics.py`)

#### 4.3.1 DelayAnalytics

**Methods:**
```python
get_delay_summary() -> Dict
get_delays_by_state() -> pd.DataFrame
get_delays_by_month() -> pd.DataFrame
```

**Output Example:**
```python
{
    "total_orders": 89316,
    "delayed_orders": 56774,
    "delay_rate_percent": 63.57,
    "avg_delay_days": 4.23,
    "max_delay_days": 189
}
```

#### 4.3.2 RevenueAnalytics

**Methods:**
```python
get_revenue_summary() -> Dict
get_revenue_by_category(products_df) -> pd.DataFrame
get_monthly_revenue() -> pd.DataFrame
```

#### 4.3.3 InventoryAnalytics

**Methods:**
```python
get_inventory_summary() -> Dict
get_low_stock_products(top_n: int) -> pd.DataFrame
get_inventory_by_warehouse() -> pd.DataFrame
```

#### 4.3.4 DemandForecasting

**Methods:**
```python
calculate_moving_average(window: int) -> pd.DataFrame
forecast_next_n_days(n_days: int) -> Dict
calculate_forecast_accuracy() -> Dict
```

**Forecasting Algorithm:**
- Method: Simple Moving Average (7-day window)
- Can be extended to ARIMA, Prophet, or ML models
- Accuracy metrics: MAPE, RMSE

### 4.4 LangChain Agent (`agents/scm_agent.py`)

#### SCMAgent Class

**Initialization:**
```python
class SCMAgent:
    def __init__(self, config: Dict, analytics_tools: Dict, rag_module)
```

**Core Methods:**
```python
def _create_tools() -> List[Tool]
def _create_agent() -> AgentExecutor
def query(user_input: str) -> str
def reset_history()
```

**Tool Creation:**
Each analytics module is wrapped as a LangChain Tool:

```python
Tool(
    name="DelayAnalysis",
    func=lambda x: str(analytics_tools['delay'].get_delay_summary()),
    description="Get delivery delay statistics..."
)
```

**Agent Prompt Template:**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent Supply Chain Management assistant..."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

### 4.5 User Interface (`ui/gradio_interface.py`)

#### Gradio Interface Features

- **Chatbot**: Multi-turn conversation
- **Stats Panel**: Real-time metrics
- **Examples**: Pre-configured queries
- **Clear History**: Reset conversation

**Interface Creation:**
```python
def create_gradio_interface(app: SCMChatbotApp) -> gr.Blocks:
    with gr.Blocks() as interface:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        submit = gr.Button("Send")
        # ... event handlers
    return interface
```

---

## 5. Development Guidelines

### 5.1 Code Style

**Follow PEP 8:**
- Line length: 100 characters
- 4 spaces for indentation
- Docstrings for all classes and functions

**Type Hints:**
```python
def process_data(df: pd.DataFrame, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Process dataframe and return statistics.
    
    Args:
        df: Input dataframe
        threshold: Filtering threshold
        
    Returns:
        Dictionary of statistics
    """
    pass
```

### 5.2 Logging

**Use structured logging:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing started")
logger.warning("Low stock detected")
logger.error("Database connection failed", exc_info=True)
```

### 5.3 Error Handling

**Graceful degradation:**
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    result = fallback_value()
finally:
    cleanup()
```

### 5.4 Adding New Analytics

**Step 1: Create Analytics Class**
```python
# In tools/analytics.py
class NewAnalytics:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def get_summary(self) -> Dict:
        # Implementation
        return {"metric": value}
```

**Step 2: Initialize in Main**
```python
# In main.py
self.analytics_tools['new'] = NewAnalytics(self.data)
```

**Step 3: Create Tool**
```python
# In agents/scm_agent.py
Tool(
    name="NewAnalysis",
    func=lambda x: str(self.analytics_tools['new'].get_summary()),
    description="Description for the agent..."
)
```

### 5.5 Adding New Data Sources

**Step 1: Extend Data Loader**
```python
# In data/data_loader.py
def load_new_source(self, path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Preprocessing
    return df
```

**Step 2: Update Configuration**
```python
# In config/config.py
DATASET_PATHS = {
    ...
    "new_source": "path/to/new/data.csv"
}
```

---

## 6. API Reference

### 6.1 Main Application

**class SCMChatbotApp**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__` | use_langchain, use_rag | None | Initialize app |
| `load_data` | data_path | None | Load datasets |
| `setup` | data_path | None | Complete setup |
| `query` | user_input: str | str | Process query |

### 6.2 Data Loader

**class SCMDataLoader**

| Method | Returns | Description |
|--------|---------|-------------|
| `load_all_data` | Tuple[5 DataFrames] | Load all datasets |
| `merge_order_data` | DataFrame | Merge related data |
| `get_data_summary` | Dict | Get statistics |

### 6.3 Analytics Classes

**All analytics classes follow this pattern:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_summary` | Dict | Overall statistics |
| `get_detailed_analysis` | DataFrame | Detailed breakdown |

### 6.4 RAG Module

**class RAGModule**

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `build_knowledge_base` | orders_df, products_df, customers_df | None | Build vector DB |
| `retrieve` | query: str, top_k: int | List[Dict] | Search documents |
| `save` | path: str | None | Save to disk |
| `load` | path: str | None | Load from disk |

---

## 7. Testing Strategy

### 7.1 Test Structure

```
tests/
├── test_all.py           # Main test file
├── test_data_loader.py   # Data loading tests
├── test_analytics.py     # Analytics tests
├── test_rag.py          # RAG tests
└── test_agent.py        # Agent tests
```

### 7.2 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_analytics.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 7.3 Writing Tests

**Unit Test Example:**
```python
def test_delay_summary():
    orders = pd.DataFrame({
        'order_id': ['O1', 'O2'],
        'is_delayed': [True, False],
        'delivery_delay_days': [5, 0]
    })
    
    analytics = DelayAnalytics(orders)
    summary = analytics.get_delay_summary()
    
    assert summary['total_orders'] == 2
    assert summary['delayed_orders'] == 1
    assert summary['delay_rate_percent'] == 50.0
```

### 7.4 Integration Tests

Test complete workflows:
```python
def test_end_to_end():
    # Setup
    app = SCMChatbotApp(use_langchain=False)
    app.setup('train')
    
    # Query
    response = app.query("What is the delay rate?")
    
    # Assert
    assert "delay" in response.lower()
    assert "%" in response
```

---

## 8. Deployment

### 8.1 Production Checklist

- [ ] Set environment variables
- [ ] Configure logging to files
- [ ] Enable authentication
- [ ] Set up rate limiting
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test failover scenarios

### 8.2 Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--mode", "ui"]
```

**Build and Run:**
```bash
docker build -t scm-chatbot .
docker run -p 8000:8000 -e GROQ_API_KEY=xxx scm-chatbot
```

### 8.3 Cloud Deployment

**AWS EC2:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip

# Setup application
git clone <repo>
cd scm_chatbot
pip3 install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/scm-chatbot.service
sudo systemctl enable scm-chatbot
sudo systemctl start scm-chatbot
```

---

## 9. Troubleshooting

### 9.1 Common Issues

**Issue: "FAISS not available"**
```bash
# Solution:
pip install faiss-cpu
# Or for GPU:
pip install faiss-gpu
```

**Issue: "LangChain agent initialization failed"**
```bash
# Check API key
echo $GROQ_API_KEY

# Use simple agent as fallback
python main.py --no-langchain
```

**Issue: "Out of memory"**
```python
# Reduce batch size in RAG module
config['batch_size'] = 100  # Instead of 1000

# Or limit knowledge base size
rag.build_knowledge_base(orders.head(5000), ...)
```

### 9.2 Debugging

**Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check agent decisions:**
```python
agent_executor = AgentExecutor(..., verbose=True)
```

---

## 10. Performance Optimization

### 10.1 Data Loading

**Use chunking:**
```python
chunks = pd.read_csv('large_file.csv', chunksize=10000)
for chunk in chunks:
    process(chunk)
```

**Cache processed data:**
```python
import pickle
with open('processed_data.pkl', 'wb') as f:
    pickle.dump(data, f)
```

### 10.2 RAG Optimization

**Pre-compute embeddings:**
```python
# Save embeddings
rag.save('models/faiss_index')

# Load instead of recomputing
rag.load('models/faiss_index')
```

**Reduce vector dimensions:**
```python
# Use smaller embedding model
config['embedding_model'] = 'all-MiniLM-L6-v2'  # 384 dim
```

### 10.3 Agent Optimization

**Limit tool calls:**
```python
agent_executor = AgentExecutor(
    max_iterations=5,  # Prevent infinite loops
    timeout=30  # 30 second timeout
)
```

### 10.4 Caching

**LLM response caching:**
```python
from langchain.cache import SQLiteCache
import langchain
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")
```

---

## 11. Future Enhancements

### 11.1 Planned Features

#### Phase 1 (Short-term)
- [ ] Real-time data ingestion
- [ ] Advanced forecasting (ARIMA, Prophet)
- [ ] Multi-language support
- [ ] Export reports to PDF

#### Phase 2 (Medium-term)
- [ ] Integration with ERP systems
- [ ] Automated alerting
- [ ] Dashboard with charts
- [ ] Mobile app

#### Phase 3 (Long-term)
- [ ] Predictive maintenance
- [ ] Optimization recommendations
- [ ] ML-based anomaly detection
- [ ] Blockchain integration for tracking

### 11.2 Research Directions

- Fine-tuning LLM on SCM data
- Multi-modal inputs (images, PDFs)
- Federated learning for privacy
- Explainable AI techniques

---

## Appendix

### A. Configuration Reference

Complete configuration options in `config/config.py`

### B. Dataset Schema

**Orders Table:**
- order_id (string)
- customer_id (string)
- order_status (string)
- order_purchase_timestamp (datetime)
- order_delivered_timestamp (datetime)
- is_delayed (boolean)

**Products Table:**
- product_id (string)
- product_category_name (string)
- product_weight_g (float)
- product_dimensions (float)

### C. API Endpoints (Future)

```
GET  /api/v1/analytics/delays
GET  /api/v1/analytics/revenue
GET  /api/v1/analytics/inventory
POST /api/v1/query
POST /api/v1/chat
```

### D. Glossary

- **RAG**: Retrieval-Augmented Generation
- **FAISS**: Facebook AI Similarity Search
- **MAPE**: Mean Absolute Percentage Error
- **SCM**: Supply Chain Management
- **LLM**: Large Language Model

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Maintained By:** M.Tech Student  
**Status:** Active Development
