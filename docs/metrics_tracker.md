# metrics_tracker.py - Query Performance Tracking

## Purpose
Lightweight metrics tracker for monitoring query performance, comparing Agentic vs Enhanced mode, and detecting potential hallucinations. Provides real-time performance statistics and comparison displays.

## Key Components

### Class: MetricsTracker
Performance tracking and metrics aggregation.

**Initialization Parameters:**
- `max_history` (int): Maximum queries to track (default: 100)

## Core Methods

### `__init__(max_history=100)`
Initializes metrics tracker with history storage.

**Storage:**
- `metrics_history`: deque with max length (FIFO)
- `active_queries`: dict of in-progress queries

### `start_query(query, mode='agentic')`
Begins tracking a new query.

**Parameters:**
- `query` (str): User's question
- `mode` (str): Query mode ('agentic', 'enhanced', 'cli', 'ui')

**Returns:** str (unique query_id)

**Tracked Data:**
- Query text
- Mode used
- Start timestamp
- Agents executed (list)
- Data sources used (list)
- RAG usage flag

**Example:**
```python
tracker = MetricsTracker()
query_id = tracker.start_query("What is delay rate?", mode='agentic')
# Returns: "1675890234567_0"
```

### `add_agent_execution(query_id, agent_name, used_rag=False)`
Records agent execution for query.

**Parameters:**
- `query_id` (str): Query identifier
- `agent_name` (str): Name of executed agent
- `used_rag` (bool): Whether agent used RAG

**Updates:**
- Appends agent to agents_executed list
- Sets rag_used flag if True

**Example:**
```python
tracker.add_agent_execution(query_id, "Delay Agent", used_rag=False)
tracker.add_agent_execution(query_id, "Analytics Agent", used_rag=True)
```

### `add_data_source(query_id, source)`
Records data source usage.

**Parameters:**
- `query_id` (str): Query identifier
- `source` (str): Data source name

**Sources:**
- `rag_documents`: Policy documents from RAG
- `analytics_engine`: Database analytics
- `external_api`: External data sources

**Example:**
```python
tracker.add_data_source(query_id, "analytics_engine")
tracker.add_data_source(query_id, "rag_documents")
```

### `calculate_hallucination_score(query_id, response, ground_truth_data=None)`
Calculates hallucination risk score.

**Parameters:**
- `query_id` (str): Query identifier
- `response` (str): Generated response
- `ground_truth_data` (dict): Optional validation data

**Returns:** float (0.0-1.0, lower is better)

**Scoring Heuristics:**
- RAG or analytics used: 0.1 (low risk - grounded)
- Ground truth provided: 0.1 (low risk - validated)
- No grounding data: 0.3 (medium risk - ungrounded)

**Example:**
```python
score = tracker.calculate_hallucination_score(
    query_id,
    "The delay rate is 6.28%",
    ground_truth_data={'analytics': True}
)
# Returns: 0.1 (low risk)
```

### `end_query(query_id, success=True, error=None)`
Marks query as complete and saves metrics.

**Parameters:**
- `query_id` (str): Query identifier
- `success` (bool): Whether query succeeded
- `error` (str): Optional error message

**Saves:**
- Final metrics to history
- Calculates latency
- Cleans up active_queries

**Metrics Saved:**
```python
{
    'query_id': str,
    'query': str,
    'mode': str,
    'latency_ms': float,
    'success': bool,
    'agents_executed': list,
    'data_sources_used': list,
    'rag_used': bool,
    'hallucination_score': float,
    'timestamp': float,
    'error': str or None
}
```

**Example:**
```python
tracker.end_query(query_id, success=True)
# Saves complete metrics to history
```

### `get_recent_metrics(limit=10)`
Retrieves recent query metrics.

**Parameters:**
- `limit` (int): Number of recent queries to return

**Returns:** list of metrics dicts

**Example:**
```python
recent = tracker.get_recent_metrics(limit=5)
for metric in recent:
    print(f"{metric['query']}: {metric['latency_ms']:.0f}ms")
```

### `get_summary_stats()`
Calculates summary statistics across all tracked queries.

**Returns:** dict with statistics

**Statistics:**
```python
{
    'total_queries': int,
    'average_latency_ms': float,
    'success_rate': float (0-100),
    'rag_usage_rate': float (0-100),
    'average_hallucination_score': float (0-1)
}
```

**Example:**
```python
stats = tracker.get_summary_stats()
print(f"Total Queries: {stats['total_queries']}")
print(f"Avg Latency: {stats['average_latency_ms']:.0f}ms")
print(f"Success Rate: {stats['success_rate']:.1f}%")
```

### `format_comparison_display(window=50)`
Formats performance comparison for UI display.

**Parameters:**
- `window` (int): Number of recent queries to analyze

**Returns:** str (markdown-formatted comparison)

**Output Sections:**
1. **Overall Statistics**
   - Total queries
   - Average latency
   - Success rate
   - RAG usage rate

2. **Mode Comparison** (if both modes used)
   - Agentic vs Enhanced statistics
   - Performance improvement percentage
   - Side-by-side comparison table

3. **Recent Queries** (last 10)
   - Query text (truncated)
   - Mode icon (🤖 or ✨)
   - Success status (✅ or ❌)
   - RAG usage (📚 or 💾)
   - Latency

**Example Output:**
```markdown
## Performance Metrics (Last 50 Queries)

### Overall Statistics
- **Total Queries:** 50
- **Average Latency:** 15234ms (15.23s)
- **Success Rate:** 98.0%
- **RAG Usage Rate:** 45.0%

---

### Mode Comparison

| Mode | Queries | Avg Latency | Success Rate |
|------|---------|-------------|--------------|
| Agentic | 30 | 5234ms (5.23s) | 100.0% |
| Enhanced | 20 | 48567ms (48.57s) | 95.0% |

**Performance Improvement:** Agentic mode is **89.2% faster** than Enhanced mode

---

### Recent Queries

1. 🤖 ✅ **What is the delivery delay rate?** - 3210ms 💾
2. ✨ ✅ **What are severity levels?** - 52340ms 📚
3. 🤖 ✅ **Show delayed orders** - 4120ms 💾
...

*Showing last 10 of 50 queries*
```

### `clear_history()`
Clears all tracked metrics.

**Use Cases:**
- Reset statistics
- Fresh performance comparison
- Testing scenarios

**Example:**
```python
tracker.clear_history()
# All metrics cleared, fresh start
```

## Global Instance

### `get_metrics_tracker()`
Returns singleton metrics tracker instance.

**Returns:** MetricsTracker (global instance)

**Pattern:** Singleton (one instance per application)

**Example:**
```python
from metrics_tracker import get_metrics_tracker

tracker = get_metrics_tracker()
query_id = tracker.start_query("Query text")
```

## Usage Examples

### Example 1: Track Complete Query
```python
from metrics_tracker import get_metrics_tracker

tracker = get_metrics_tracker()

# Start tracking
query_id = tracker.start_query("What is delay rate?", mode='agentic')

# Record agent execution
tracker.add_agent_execution(query_id, "Delay Agent", used_rag=False)

# Record data source
tracker.add_data_source(query_id, "analytics_engine")

# Calculate hallucination score
tracker.calculate_hallucination_score(
    query_id,
    "The delay rate is 6.28%",
    ground_truth_data={'analytics': True}
)

# End tracking
tracker.end_query(query_id, success=True)
```

### Example 2: Display Performance Comparison
```python
# Get comparison display
comparison = tracker.format_comparison_display(window=50)
print(comparison)
# Outputs markdown-formatted performance comparison
```

### Example 3: Analyze Statistics
```python
# Get summary stats
stats = tracker.get_summary_stats()

if stats['average_latency_ms'] > 10000:
    print("⚠️ High average latency detected")

if stats['success_rate'] < 90:
    print("⚠️ Low success rate, investigate errors")
```

## Integration Points

### Used By
- `agents/orchestrator.py`: Tracks all agentic queries
- `main.py`: Displays performance metrics in UI

### Integrates With
- Gradio UI: Performance Metrics tab
- Logging system: Metrics logged for debugging

## Performance Characteristics

### Memory Usage
- ~1KB per tracked query
- Max 100 queries (default) = ~100KB
- Minimal overhead

### Processing Overhead
- start_query: <1ms
- end_query: <1ms
- format_comparison_display: ~5-10ms
- Negligible impact on query processing

## Metrics Interpretation

### Latency
- **Fast**: <5s (Agentic data queries)
- **Medium**: 5-20s (Agentic policy queries)
- **Slow**: >40s (Enhanced with RAG)

### Success Rate
- **Excellent**: >95%
- **Good**: 85-95%
- **Needs Attention**: <85%

### RAG Usage Rate
- **Agentic**: ~30-40% (intelligent usage)
- **Enhanced with RAG**: 100% (always uses)
- **Enhanced without RAG**: 0% (never uses)

### Hallucination Score
- **Low Risk**: <0.2 (grounded in data)
- **Medium Risk**: 0.2-0.5 (some uncertainty)
- **High Risk**: >0.5 (ungrounded response)

## Comparison: Agentic vs Enhanced

### Typical Results
```
Agentic Mode:
- Avg Latency: 5-8s
- Success Rate: 98-100%
- RAG Usage: 30-40%

Enhanced Mode (with RAG):
- Avg Latency: 45-60s
- Success Rate: 95-98%
- RAG Usage: 100%

Performance Improvement: 80-92% faster (Agentic)
```

## Error Handling

### Query Not Found
- Silently ignores invalid query_id
- Logs warning for debugging

### Empty History
- Returns empty statistics
- Shows "No queries recorded" message

### Invalid Data
- Handles missing fields gracefully
- Uses defaults for optional metrics

## Logging

Logs key events:
- Query start/end
- Metrics calculation
- History cleared

**Log Levels:**
- INFO: Normal operations
- DEBUG: Detailed metrics
- WARNING: Invalid operations

## Future Enhancements

### Potential Features
1. **Persistent Storage**: Save metrics to database
2. **Advanced Analytics**: Trend analysis, anomaly detection
3. **Real-time Dashboards**: Live performance monitoring
4. **Alerts**: Notify on performance degradation
5. **Export**: CSV/JSON export for external analysis
6. **Filtering**: Filter by mode, time range, success status
7. **Aggregations**: Hourly/daily/weekly statistics
