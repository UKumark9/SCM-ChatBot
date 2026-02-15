# agents/orchestrator.py - Multi-Agent System Coordinator

## Purpose
Central orchestrator that manages multiple specialized agents, routes queries based on intent analysis, and integrates intent classification for intelligent RAG usage. Provides intelligent query routing and parallel agent execution.

## Key Components

### Class: AgentOrchestrator
Manages and coordinates specialized agents for different SCM domains.

**Initialization Parameters:**
- `analytics_engine`: SCMAnalytics instance
- `data_wrapper`: Database wrapper
- `rag_module`: RAGModule instance (optional)
- `use_langchain` (bool): Enable LangChain agentic framework

## Core Methods

### `__init__(analytics_engine, data_wrapper, rag_module=None, use_langchain=False)`
Initializes orchestrator with all specialized agents.

**Agents Initialized:**
- **DelayAgent**: Delivery delays and on-time performance
- **AnalyticsAgent**: Revenue and product analytics
- **ForecastingAgent**: Demand forecasting
- **DataQueryAgent**: Raw data retrieval

**Systems Initialized:**
- **IntentClassifier**: Query type classification (policy/data/mixed)
- **MetricsTracker**: Performance monitoring
- **UIFormatter**: Response formatting

**Example:**
```python
orchestrator = AgentOrchestrator(
    analytics_engine=analytics,
    data_wrapper=data,
    rag_module=rag,
    use_langchain=False
)
```

### `analyze_intent(query)`
Analyzes query to determine appropriate agent.

**Parameters:**
- `query` (str): User's question

**Returns:** dict with intent analysis

**Intent Structure:**
```python
{
    'agent': 'delay' | 'forecasting' | 'analytics' | 'data_query' | 'multi_agent',
    'domain': str,
    'complexity': 'simple' | 'moderate' | 'complex',
    'multi_intent': bool,
    'requires_rag': bool,
    'geographic': bool,
    'product_specific': bool
}
```

**Agent Selection:**
- **delay**: Delay, delivery, on-time queries
- **forecasting**: Forecast, predict, demand queries
- **analytics**: Revenue, product, sales queries
- **data_query**: Show, list, get queries
- **multi_agent**: Complex queries requiring multiple agents

**Example:**
```python
intent = orchestrator.analyze_intent("What is the delay rate?")
# Returns: {'agent': 'delay', 'domain': 'delivery', 'complexity': 'simple'}
```

### `route_query(query)`
Routes query to appropriate agent(s) based on intent classification.

**Parameters:**
- `query` (str): User's question

**Returns:** dict with agent response

**Process:**
1. **Classify query** using IntentClassifier
   - Determines policy/data/mixed type
   - Sets use_rag and use_database flags

2. **Analyze intent** for agent selection
   - Determines which agent(s) to use
   - Detects multi-intent queries

3. **Route to agent** with classification
   - Passes classification to agent
   - Agent respects RAG/database flags

4. **Add metadata** to result
   - Intent, classification, orchestrator info
   - Store in conversation history

**Example:**
```python
result = orchestrator.route_query("What is the delay rate?")
# Classification: DATA (use_rag=False, use_database=True)
# Routes to: DelayAgent
# Time: ~3-5s (no RAG overhead)
```

**Classification Integration:**
```
Query: "What is the delay rate?"
↓
IntentClassifier: DATA (use_rag=False, use_database=True)
↓
DelayAgent: Queries database only, skips RAG
↓
Response: "6.28%" (fast, focused)
```

### `query(user_query, show_agent=True, show_metrics=True)`
Main query processing method with metrics tracking.

**Parameters:**
- `user_query` (str): User's question
- `show_agent` (bool): Include agent metadata in response
- `show_metrics` (bool): Include performance metrics

**Returns:** str (formatted response)

**Full Process:**
1. Start metrics tracking
2. Route query to appropriate agent(s)
3. Collect agent responses
4. Track agent execution and data sources
5. Calculate hallucination score
6. Format response with UIFormatter
7. End metrics tracking
8. Return formatted response

**Example:**
```python
response = orchestrator.query("What is the delay rate?")
print(response)
```

**Output:**
```
The delivery delay rate is 6.28%.

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 3.21s
────────────────────────────────────────────────────────────
```

### `_handle_multi_intent_query(query, intent)`
Handles queries requiring multiple agents.

**Parameters:**
- `query` (str): User's question
- `intent` (dict): Intent analysis

**Process:**
1. Identifies required agents
2. Executes agents in parallel (if possible)
3. Aggregates results
4. Returns combined response

**Example Multi-Intent Queries:**
- "Compare delays with revenue impact"
- "Show delivery and forecast data"
- "Analyze delays by product and state"

### `_handle_comprehensive_query(query)`
Handles comprehensive queries needing all agents.

**Parameters:**
- `query` (str): User's question

**Returns:** dict with aggregated results

**Use Cases:**
- "Give me complete SCM overview"
- "Show all metrics"
- "Comprehensive analysis"

## Agent Routing Logic

### Delay Agent
**Triggers:**
- Keywords: "delay", "delivery", "on-time", "late", "ship"
- Queries: "What is delay rate?", "Show delayed orders"

**Classification Impact:**
- DATA queries: Database only (~3-5s)
- POLICY queries: RAG only (~15s)
- MIXED queries: Both sources (~18s)

### Analytics Agent
**Triggers:**
- Keywords: "revenue", "sales", "product", "performance"
- Queries: "Show revenue by product", "Top selling products"

**Classification Impact:**
- Same as Delay Agent (DATA/POLICY/MIXED)

### Forecasting Agent
**Triggers:**
- Keywords: "forecast", "predict", "demand", "future", "trend"
- Queries: "Forecast next month demand", "Predict product trends"

**Classification Impact:**
- Usually DATA (database forecasting models)
- Rarely uses RAG (unless policy questions)

### Data Query Agent
**Triggers:**
- Keywords: "show", "list", "get", "retrieve", "display"
- Queries: "Show all orders", "List products"

**Classification Impact:**
- Always DATA (pure database queries)
- Never uses RAG

## Intent Classification Integration

### Before Classification
```python
# All queries use RAG + Database
result = delay_agent.query(query)
# Time: 45-60s (RAG overhead even for data queries)
```

### After Classification
```python
# Classify query first
classification = intent_classifier.classify_query(query)
# {'query_type': 'data', 'use_rag': False, 'use_database': True}

# Route with classification
result = delay_agent.query(query, classification=classification)
# Time: 3-5s (skips RAG for data queries)
```

### Performance Impact
- **Data queries**: 60-80% faster (skip RAG)
- **Policy queries**: Same speed (RAG still used)
- **Mixed queries**: Slight improvement (optimized routing)

## Metrics Tracking

### Tracked Metrics
- Query start/end time
- Agents executed
- Data sources used (RAG, database)
- RAG usage flag
- Hallucination score
- Success/failure status

### Integration Example
```python
# Start tracking
query_id = metrics_tracker.start_query(query, mode='agentic')

# Track agent execution
metrics_tracker.add_agent_execution(query_id, "Delay Agent", used_rag=False)

# Track data sources
metrics_tracker.add_data_source(query_id, "analytics_engine")

# End tracking
metrics_tracker.end_query(query_id, success=True)
```

## UIFormatter Integration

All responses formatted consistently:
```python
# Agent returns raw result
result = agent.query(query, classification=classification)

# Orchestrator formats with UIFormatter
formatted = UIFormatter.format_response(result)
# Returns professionally formatted response with metadata
```

## Helper Methods

### `_build_agent_info(agent_name, time_taken, rag_used=False)`
Builds agent metadata footer.

**Parameters:**
- `agent_name` (str): Agent name
- `time_taken` (float): Execution time
- `rag_used` (bool): Whether RAG was used

**Returns:** str (formatted metadata)

### `clear_history()`
Clears conversation history.

**Use Cases:**
- Reset context
- Fresh conversation
- Testing

## Dependencies

### External Libraries
- `logging`: Application logging
- `time`: Performance tracking
- `os`: Environment variables

### Internal Modules
- `agents.delay_agent`: Delay analysis
- `agents.analytics_agent`: Revenue analytics
- `agents.forecasting_agent`: Demand forecasting
- `agents.data_query_agent`: Data retrieval
- `ui_formatter`: Response formatting
- `intent_classifier`: Query classification
- `metrics_tracker`: Performance tracking

## Usage Examples

### Example 1: Simple Data Query
```python
orchestrator = AgentOrchestrator(analytics, data, rag)

response = orchestrator.query("What is the delay rate?")
# Classification: DATA
# Agent: DelayAgent
# RAG: Not used
# Time: ~3-5s
# Response: "6.28%"
```

### Example 2: Policy Query
```python
response = orchestrator.query("What are severity levels?")
# Classification: POLICY
# Agent: DelayAgent
# RAG: Used
# Time: ~15s
# Response: Policy definitions
```

### Example 3: Mixed Query
```python
response = orchestrator.query("Compare actual delay with target policy")
# Classification: MIXED
# Agent: DelayAgent
# RAG: Used
# Database: Used
# Time: ~18s
# Response: Comparison with both sources
```

### Example 4: Multi-Agent Query
```python
response = orchestrator.query("Show delays and revenue by state")
# Classification: DATA
# Agents: DelayAgent, AnalyticsAgent
# Execution: Parallel
# Time: ~5-7s
# Response: Combined results
```

## Conversation History

Tracks all queries and responses:
```python
{
    'query': str,
    'response': dict,
    'intent': dict,
    'classification': dict
}
```

**Use Cases:**
- Multi-turn conversations
- Context-aware responses
- Performance analysis

## Error Handling

### Agent Execution Error
- Logs error with traceback
- Returns error response
- Tracks in metrics as failed query

### Classification Error
- Falls back to default (DATA classification)
- Logs warning
- Continues with query processing

### RAG Unavailable
- Continues without RAG context
- Logs warning
- Uses database only

## Performance Characteristics

### Query Latency
- **Data queries**: 3-5s (no RAG)
- **Policy queries**: 15s (RAG only)
- **Mixed queries**: 18s (both sources)
- **Multi-agent**: 5-10s (depends on agents)

### Resource Usage
- Memory: ~50-100MB (agents + models)
- CPU: Low (mostly I/O bound)
- Network: API calls for RAG/LLM (if used)

## Logging

Log messages include:
- Query classification results
- Agent routing decisions
- Execution times
- Data sources used
- Errors with tracebacks

**Example:**
```
INFO - Query Classification: data | Domain: delay | Confidence: 0.50
INFO -   → Use RAG: False | Use Database: True
INFO - Routing to: Delay Agent
DEBUG - Agent execution time: 3.21s
INFO - Query completed successfully
```

## Comparison: Before vs After Intent Classification

### Before
```
Query: "What is delay rate?"
→ Always uses RAG + Database
→ Time: 45-60s
→ Unnecessary RAG overhead
```

### After
```
Query: "What is delay rate?"
→ Classification: DATA (use_rag=False)
→ Uses Database only
→ Time: 3-5s
→ 60-80% faster!
```

## Integration Points

### Used By
- `main.py`: Routes all agentic mode queries

### Uses
- `IntentClassifier`: Query classification
- All agents: Specialized processing
- `UIFormatter`: Response formatting
- `MetricsTracker`: Performance tracking
- `RAGModule`: Policy retrieval (when needed)
