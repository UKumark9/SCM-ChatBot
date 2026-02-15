# agents/delay_agent.py - Delivery Delay Analysis Agent

## Purpose
Specialized agent for analyzing delivery delays, on-time performance, and delay severity levels. Integrates with intent classification to intelligently use RAG for policy questions and database for data queries.

## Key Components

### Class: DelayAgent
Handles all delivery delay-related queries.

**Initialization Parameters:**
- `analytics_engine`: SCMAnalytics instance
- `data_wrapper`: Database wrapper
- `rag_module`: RAGModule instance (optional)

## Core Methods

### `__init__(analytics_engine, data_wrapper, rag_module=None)`
Initializes delay agent with analytics and optional RAG.

### `query(user_query, classification=None)`
Processes delay-related queries with intent classification support.

**Parameters:**
- `user_query` (str): User's question
- `classification` (dict): Intent classification result (optional)

**Returns:** dict with response and metadata

**Classification-Based Routing:**

1. **POLICY Query** (use_rag=True, use_database=False):
   ```python
   Query: "What are severity levels?"
   → Retrieves from RAG only
   → Returns policy definitions
   → Time: ~15s
   ```

2. **DATA Query** (use_rag=False, use_database=True):
   ```python
   Query: "What is the delay rate?"
   → Queries database only
   → Returns actual metrics
   → Time: ~3-5s
   ```

3. **MIXED Query** (use_rag=True, use_database=True):
   ```python
   Query: "Compare actual delay with target"
   → Uses both RAG and database
   → Returns comprehensive comparison
   → Time: ~18s
   ```

**Example:**
```python
delay_agent = DelayAgent(analytics, data, rag)

# Data query (fast)
result = delay_agent.query(
    "What is the delay rate?",
    classification={'use_rag': False, 'use_database': True}
)
# Returns: {'response': '6.28%', 'used_rag': False, 'success': True}

# Policy query (uses RAG)
result = delay_agent.query(
    "What are severity levels?",
    classification={'use_rag': True, 'use_database': False}
)
# Returns: {' response': 'Critical: >5 days...', 'used_rag': True}
```

### Key Query Types Handled

#### Delay Rate Queries
- "What is the delay rate?"
- "Show delivery performance"
- "Current on-time percentage"

**Response Format:**
```
The delivery delay rate is 6.28%.
On-time delivery rate: 93.72%
```

#### Delayed Orders
- "Show delayed orders"
- "List overdue deliveries"
- "Which orders are late?"

**Response Format:**
```
Delayed Orders:
1. Order #12345 - 8 days late (Critical)
2. Order #12346 - 4 days late (Major)
...
```

#### Severity Levels (Policy)
- "What are severity levels?"
- "Define delay classifications"
- "Explain delay categories"

**Response Format:**
```
### 📚 Policy Documents

Severity Levels:
• Critical Delay: >5 business days beyond committed date
• Major Delay: 3-5 business days beyond committed date
• Minor Delay: 1-2 business days beyond committed date
```

#### Geographic Analysis
- "Show delays by state"
- "Which states have highest delays?"
- "Delay rate for California"

**Response Format:**
```
Delays by State:
1. CA: 8.5% delay rate
2. TX: 6.2% delay rate
3. NY: 7.1% delay rate
```

## Helper Methods

### `_analyze_delay_metrics()`
Analyzes delivery delay metrics from database.

**Returns:** dict with:
- `delay_rate_percentage`: Overall delay rate
- `on_time_rate`: On-time delivery percentage
- `total_orders`: Total order count
- `delayed_orders`: Delayed order count
- `avg_delay_days`: Average delay duration
- `delays_by_state`: Geographic breakdown

### `_get_delayed_orders(limit=10)`
Retrieves list of delayed orders.

**Parameters:**
- `limit` (int): Maximum orders to return

**Returns:** list of order dicts

### `_format_delay_analysis(metrics)`
Formats delay metrics for display.

**Parameters:**
- `metrics` (dict): Raw metrics data

**Returns:** str (formatted analysis)

### `_classify_delay_severity(delay_days)`
Classifies delay into severity level.

**Parameters:**
- `delay_days` (int): Days delayed

**Returns:** str ("Critical", "Major", "Minor")

**Classification:**
- Critical: >5 days
- Major: 3-5 days
- Minor: 1-2 days

## Integration with Intent Classification

### Classification Flow
```
User Query: "What is the delay rate?"
↓
Orchestrator classifies: DATA (use_rag=False, use_database=True)
↓
DelayAgent.query(query, classification={...})
↓
Agent checks classification flags:
- should_use_rag = False  ← Skip RAG
- should_use_database = True  ← Query database
↓
Query database for metrics
↓
Return: "6.28%" (fast, focused)
```

### Code Implementation
```python
def query(self, user_query, classification=None):
    # Get classification flags
    should_use_rag = classification.get('use_rag', True) if classification else True
    should_use_database = classification.get('use_database', True) if classification else True

    # Policy-only question?
    if classification and classification['query_type'] == 'policy':
        if should_use_rag and rag_context:
            return UIFormatter.format_rag_context(rag_context)

    # Data question - skip RAG, query database only
    if should_use_database:
        metrics = self._analyze_delay_metrics()
        response = f"Delay rate: {metrics['delay_rate_percentage']:.2f}%"

    # Mixed query - append RAG context if available
    if classification['query_type'] == 'mixed' and rag_context:
        response += UIFormatter.format_rag_context(rag_context)

    return {'response': response, 'used_rag': should_use_rag}
```

## Performance Characteristics

### Data Queries (No RAG)
- **Time**: 3-5 seconds
- **Sources**: Database only
- **Optimization**: 60-80% faster than with RAG
- **Example**: "What is delay rate?" → "6.28%"

### Policy Queries (RAG Only)
- **Time**: 15 seconds
- **Sources**: RAG documents only
- **Use Case**: Policy definitions, guidelines
- **Example**: "What are severity levels?" → Policy definitions

### Mixed Queries (Both)
- **Time**: 18 seconds
- **Sources**: RAG + Database
- **Use Case**: Comparisons, comprehensive analysis
- **Example**: "Compare actual vs target" → Both sources

## Response Format Examples

### Simple Data Response
```
The delivery delay rate is 6.28%.

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 3.21s
────────────────────────────────────────────────────────────
```

### Policy Response
```
### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Delay Management Policy | Relevance: 0.85

Severity Levels:
• Critical Delay: >5 business days beyond committed delivery date
• Major Delay: 3-5 business days beyond committed delivery date
• Minor Delay: 1-2 business days beyond committed delivery date
───────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent | 📚 RAG | ✅ Success
📁 Sources: Policy Documents
⏱️ Time: 14.52s
────────────────────────────────────────────────────────────
```

### Comprehensive Response (Mixed)
```
**Current Performance:**
• Delay Rate: 6.28%
• On-Time Rate: 93.72%

### 📚 Policy Documents

Target Performance:
• On-Time Delivery Target: >95%
• Maximum Acceptable Delay: <5%

**Analysis:**
❌ Below target by 1.28 percentage points
✅ Delay rate within acceptable limits

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent | 📚 RAG | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 18.34s
────────────────────────────────────────────────────────────
```

## Dependencies

### Internal Modules
- `analytics_engine`: Delay metrics calculation
- `data_wrapper`: Database queries
- `rag`: Policy document retrieval
- `ui_formatter`: Response formatting

### External Libraries
- `logging`: Agent logging

## Error Handling

### Database Error
- Returns error message
- Logs exception
- Marks response as failed

### RAG Unavailable
- Continues without policy context
- Logs warning
- Uses database only

### No Data Found
- Returns "No delay data available"
- Suggests data refresh

## Usage Examples

### Example 1: Quick Metric Check
```python
agent = DelayAgent(analytics, data)
result = agent.query("delay rate?", classification={'query_type': 'data'})
# Fast response, no RAG overhead
```

### Example 2: Policy Information
```python
result = agent.query("severity levels?", classification={'query_type': 'policy'})
# Uses RAG, returns policy definitions
```

### Example 3: Detailed Analysis
```python
result = agent.query("Show delayed orders by severity")
# Database query with severity classification
```

## Integration Points

### Used By
- `agents/orchestrator.py`: Routes delay queries

### Uses
- `analytics_engine.analyze_delivery_delays()`: Metrics
- `rag.retrieve_context()`: Policy documents
- `UIFormatter.format_response()`: Output formatting
