# API & Configuration Reference

## Configuration (`config/config.py`)

### LLM Configuration

```python
LLM_CONFIG = {
    "provider": "groq",
    "model_name": "llama3-70b-8192",
    "temperature": 0.1,        # Low temperature for factual responses
    "max_tokens": 4096,
    "api_key": os.getenv("GROQ_API_KEY")
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | str | LLM provider (`groq`) |
| `model_name` | str | Model identifier |
| `temperature` | float | Response randomness (0.0-1.0) |
| `max_tokens` | int | Maximum response length |

### Vector Database Configuration

```python
VECTOR_DB_CONFIG = {
    "provider": "faiss",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384,
    "index_path": str(MODELS_DIR / "faiss_index")
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | str | Vector store backend (`faiss`) |
| `embedding_model` | str | Sentence-Transformers model name |
| `dimension` | int | Embedding vector dimensionality |
| `index_path` | str | Path to FAISS index files |

### RAG Configuration

```python
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k": 5,
    "similarity_threshold": 0.7
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `chunk_size` | int | Words per document chunk |
| `chunk_overlap` | int | Overlapping words between chunks |
| `top_k` | int | Number of documents to retrieve |
| `similarity_threshold` | float | Minimum cosine similarity score (0.0-1.0) |

### Analytics Configuration

```python
ANALYTICS_CONFIG = {
    "delay_threshold_days": 5,
    "inventory_low_threshold": 10,
    "inventory_high_threshold": 1000,
    "forecast_periods": 30
}
```

### API Configuration

```python
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "secret_key": "your-secret-key-change-in-production"
}
```

### UI Configuration

```python
UI_CONFIG = {
    "title": "AI-Powered Supply Chain Management Chatbot",
    "description": "Ask questions about orders, inventory, suppliers, and logistics",
    "theme": "default",
    "share": False
}
```

### Agent Configuration

```python
AGENT_CONFIG = {
    "max_iterations": 10,
    "timeout": 60,
    "verbose": True
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_iterations` | int | Maximum LangChain agent iterations per query |
| `timeout` | int | Agent execution timeout in seconds |
| `verbose` | bool | Enable detailed agent logging |

### Evaluation Thresholds

```python
EVAL_THRESHOLDS = {
    "accuracy": 0.85,
    "mape": 15.0,
    "rmse": 10.0,
    "latency": 2.0,
    "hallucination_rate": 0.05
}
```

## Command-Line Arguments

```
python main.py [OPTIONS]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--rag` | off | Enable RAG (Retrieval-Augmented Generation) |
| `--agentic` | off | Use multi-agent agentic mode |
| `--enhanced` | on | Use enhanced single-LLM mode |
| `--no-rag` | off | Disable RAG explicitly |
| `--show-agent` | off | Display agent routing information in responses |

## Key Classes

### `SCMChatbotApp` (main.py)

Main application class.

```python
app = SCMChatbotApp(
    use_enhanced=True,    # Enable enhanced mode
    use_rag=True,         # Enable RAG
    show_agent=True,      # Show agent info
    use_agentic=False,    # Use agentic mode
    init_all_modes=False  # Initialize all modes at startup
)
app.load_data("train")
app.launch()
```

### `EnhancedChatbot` (enhanced_chatbot.py)

Single-LLM chatbot with Groq API.

```python
chatbot = EnhancedChatbot(
    analytics_engine=analytics,
    data_wrapper=data,
    rag_module=rag_system
)
response = chatbot.process_query("What is the delivery delay rate?")
```

### `AgentOrchestrator` (agents/orchestrator.py)

Multi-agent coordinator.

```python
orchestrator = AgentOrchestrator(
    analytics_engine=analytics,
    data_wrapper=data,
    rag_module=rag_system,
    use_langchain=True
)
result = orchestrator.route_query("Show revenue by product category")
```

### `RAGSystem` (rag.py)

Vector search and retrieval.

```python
rag = RAGSystem()
rag.build_index(documents)           # Build FAISS index
results = rag.retrieve("delay policy", top_k=5)  # Search
```

### `DocumentProcessor` (rag.py)

Document chunking and preparation.

```python
processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
documents = processor.create_documents_from_data(data_processor)
```

### `MetricsTracker` (metrics_tracker.py)

Performance monitoring.

```python
tracker = MetricsTracker()
tracker.record_query(
    query="...",
    response="...",
    latency=0.5,
    mode="agentic",
    agent="delay"
)
stats = tracker.get_summary()
```

## Dataset Schema

### Orders (`df_Orders.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | str | Unique order identifier |
| `customer_id` | str | Customer reference |
| `order_status` | str | Status (delivered, shipped, etc.) |
| `order_purchase_timestamp` | datetime | Purchase time |
| `order_delivered_customer_date` | datetime | Delivery time |
| `order_estimated_delivery_date` | datetime | Estimated delivery |
| `is_delayed` | bool | Calculated: delivery after estimate |
| `delay_days` | int | Calculated: days of delay |

### Customers (`df_Customers.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | str | Unique customer identifier |
| `customer_city` | str | City |
| `customer_state` | str | State code |
| `customer_zip_code_prefix` | str | ZIP prefix |

### Products (`df_Products.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | str | Unique product identifier |
| `product_category_name` | str | Category |
| `product_weight_g` | float | Weight in grams |
| `product_length_cm` | float | Length |
| `product_height_cm` | float | Height |
| `product_width_cm` | float | Width |

### OrderItems (`df_OrderItems.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | str | Order reference |
| `product_id` | str | Product reference |
| `price` | float | Item price |
| `freight_value` | float | Shipping cost |

### Payments (`df_Payments.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | str | Order reference |
| `payment_type` | str | Payment method |
| `payment_installments` | int | Number of installments |
| `payment_value` | float | Payment amount |

## Ports

| Service | Port | Protocol |
|---------|------|----------|
| Gradio UI | 7860 | HTTP |
| FastAPI (optional) | 8000 | HTTP |
