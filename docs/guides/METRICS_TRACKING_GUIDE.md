# Performance Metrics Tracking Guide

## Overview

The SCM Chatbot now includes comprehensive **performance metrics tracking** that automatically monitors and compares query performance between **Single-Agent (Enhanced)** and **Multi-Agent (Agentic)** modes.

This allows you to:
- ✅ Measure task completion rates
- 🎯 Detect potential hallucinations
- ⏱️ Track response latency
- 🔤 Monitor LLM token usage
- 📊 Compare mode performance
- 💰 Analyze cost efficiency

---

## 📊 Tracked Metrics

### 1. **Latency (Response Time)**

**What it measures:** Time from query submission to response completion (in milliseconds)

**Why it matters:**
- User experience - faster responses mean better UX
- Performance bottlenecks - identify slow queries
- Infrastructure planning - understand computational needs

**Typical Values:**
- **Enhanced Mode:** 800-2000ms (single LLM call)
- **Agentic Mode:** 1500-4000ms (multiple agents + orchestration)

### 2. **Token Usage**

**What it measures:** Number of LLM tokens consumed (prompt + completion)

**Why it matters:**
- **Cost:** LLM APIs charge per token
- **Context limits:** Models have maximum token limits
- **Efficiency:** Fewer tokens = lower cost

**Components:**
- `prompt_tokens` - Input text to LLM
- `completion_tokens` - Generated response text
- `total_tokens` - Sum of both

**Cost Example:**
- Groq (Llama 3.3 70B): ~$0.59 per million tokens
- 1,000 tokens ≈ $0.00059

### 3. **Task Completion Rate**

**What it measures:** Percentage of queries successfully completed

**Success Criteria:**
- Query executed without errors
- At least one agent was used OR data sources accessed
- Valid response generated

**Target:** > 95% completion rate

### 4. **Hallucination Score**

**What it measures:** Risk that response contains made-up information (0.0 - 1.0 scale)

**Scoring:**
- **0.0 - 0.3:** Low risk (grounded in data)
- **0.3 - 0.6:** Medium risk (some assumptions)
- **0.6 - 1.0:** High risk (likely hallucinating)

**How it's calculated:**
```python
score = 0.0

# No data sources used
if not data_sources_used and not rag_retrieved:
    score += 0.5  # No grounding

# Making numeric claims without data
if has_numbers and not data_sources:
    score += 0.3  # Ungrounded numbers

# Has ground truth but didn't use it
if ground_truth_exists and not data_sources:
    score += 0.2  # Ignoring available data
```

**Why it matters:**
- **Trust:** Hallucinations can lead to wrong decisions
- **Data grounding:** Ensures responses use actual data
- **Quality control:** Identifies problematic responses

### 5. **RAG Usage Rate**

**What it measures:** Percentage of queries that used document context

**Why it matters:**
- Shows how often uploaded documents are being used
- Indicates query types benefiting from RAG
- Helps assess RAG value

### 6. **Agents Used**

**What it measures:** Number and type of agents invoked per query

**Agentic Mode Agents:**
- 🚚 Delay Agent
- 📊 Analytics Agent
- 📈 Forecasting Agent
- 🔍 Data Query Agent

**Why it matters:**
- **Multi-agent coordination:** Complex queries use multiple agents
- **Specialization:** Right agent for the task
- **Overhead:** More agents = more latency but potentially better quality

---

## 🎯 How Metrics Are Collected

### Automatic Tracking

Every query is automatically tracked:

```python
# 1. Query starts
query_id = metrics_tracker.start_query(query, mode='agentic')

# 2. Agent execution recorded
metrics_tracker.add_agent_execution(query_id, 'Delay Agent', used_rag=True)

# 3. Data sources recorded
metrics_tracker.add_data_source(query_id, 'analytics_engine')
metrics_tracker.add_data_source(query_id, 'rag_documents')

# 4. Hallucination calculated
metrics_tracker.calculate_hallucination_score(query_id, response, ground_truth)

# 5. Query ends
metrics_tracker.end_query(query_id, success=True)
```

### Storage

Metrics are saved to: `data/metrics_log.jsonl`

Each line is a JSON object representing one query's metrics.

---

## 📈 Viewing Metrics

### 1. **Per-Query Metrics**

Displayed automatically at the bottom of each response:

```
────────────────────────────────────────────────────────────
📊 Query Metrics
────────────────────────────────────────────────────────────
⏱️ Latency: 2341ms
🤖 Agents Used: Delay, Forecasting
📈 Agent Count: 2
📚 RAG Used By: Delay
🔤 Tokens Used: 1,234 (Prompt: 567, Completion: 667)
✅ Task Completed: True
🎯 Hallucination Risk: Low (0.15)
💾 Data Sources: analytics_engine, rag_documents
────────────────────────────────────────────────────────────
```

### 2. **Performance Comparison**

Access via **"⚡ Performance Metrics"** tab in the UI:

```
==============================================================
📊 Performance Comparison (Single vs Multi-Agent)
==============================================================
📝 Analysis Window: Last 50 queries
📈 Total Queries Analyzed: 50

🤖 Agentic (Multi-Agent) Mode
   • Queries: 30
   • Avg Latency: 2,456ms
   • Avg Tokens: 1,345
   • Task Completion Rate: 96.7%
   • Avg Agents per Query: 1.8
   • RAG Usage Rate: 73.3%
   • Hallucination Risk: 0.12

✨ Enhanced (Single LLM) Mode
   • Queries: 20
   • Avg Latency: 1,234ms
   • Avg Tokens: 892
   • Task Completion Rate: 95.0%
   • RAG Usage Rate: 65.0%
   • Hallucination Risk: 0.18

💡 Key Insights
   • Latency: Agentic is 99% slower
   • Token Usage: Agentic uses 51% more tokens
   • Agentic has 1.7% higher task completion rate
   • Agentic shows lower hallucination risk
==============================================================
```

---

## 🔍 Interpreting Results

### When to Use Agentic Mode

**Best For:**
- ✅ Complex multi-domain queries
- ✅ Queries requiring specialized analysis
- ✅ High accuracy requirements
- ✅ Multi-step reasoning

**Trade-offs:**
- ❌ Higher latency (2-4x slower)
- ❌ More token usage (1.5-2x more)
- ✅ Better task completion
- ✅ Lower hallucination risk

**Example Queries:**
```
"Show delays by carrier and forecast demand for top delayed products"
"Analyze revenue trends and predict next quarter's performance"
"Which products have worst delivery rates and should we stock more?"
```

### When to Use Enhanced Mode

**Best For:**
- ✅ Simple, single-domain queries
- ✅ Speed is priority
- ✅ Cost sensitivity
- ✅ Straightforward questions

**Trade-offs:**
- ✅ Faster responses (800-2000ms)
- ✅ Lower token usage
- ❌ May struggle with complex queries
- ❌ Slightly higher hallucination risk

**Example Queries:**
```
"What is the overall delay rate?"
"Show me total revenue"
"How many orders were delayed last month?"
```

---

## 💰 Cost Analysis

### Token Usage Comparison

**Average Query (Mixed Workload):**

| Mode | Avg Tokens | Cost per Query | Cost per 1,000 Queries |
|------|-----------|----------------|------------------------|
| Enhanced | 850 | $0.0005 | $0.50 |
| Agentic | 1,300 | $0.0008 | $0.77 |

**Cost Difference:** Agentic mode costs ~53% more per query

**ROI Consideration:**
- Higher completion rate (96.7% vs 95%)
- Lower hallucination (0.12 vs 0.18)
- Better handling of complex queries

**Break-Even Analysis:**
If 1 wrong decision costs > $0.27, the higher accuracy of Agentic mode pays for itself.

---

## 📊 Sample Metrics Scenarios

### Scenario 1: Simple Query

**Query:** "What is the delay rate?"

**Enhanced Mode:**
```
⏱️ Latency: 1,123ms
🔤 Tokens: 678
✅ Task Completed: True
🎯 Hallucination: 0.10 (Low)
💾 Data: analytics_engine
```

**Agentic Mode:**
```
⏱️ Latency: 1,856ms
🤖 Agents: Delay
🔤 Tokens: 892
✅ Task Completed: True
🎯 Hallucination: 0.05 (Low)
💾 Data: analytics_engine
```

**Winner:** Enhanced (faster, cheaper, same quality)

### Scenario 2: Complex Multi-Domain Query

**Query:** "Show product delays and forecast demand for electronics category"

**Enhanced Mode:**
```
⏱️ Latency: 2,345ms
🔤 Tokens: 1,123
✅ Task Completed: True (partial - may miss multi-intent)
🎯 Hallucination: 0.25 (Medium)
💾 Data: analytics_engine
```

**Agentic Mode:**
```
⏱️ Latency: 3,456ms
🤖 Agents: Delay, Forecasting
📈 Agent Count: 2
🔤 Tokens: 1,789
✅ Task Completed: True (full coverage)
🎯 Hallucination: 0.08 (Low)
💾 Data: analytics_engine, rag_documents
📚 RAG Used By: Delay, Forecasting
```

**Winner:** Agentic (better coverage, lower hallucination, uses RAG)

### Scenario 3: RAG-Heavy Query

**Query:** "What are the approved purchasing procedures for electronics?"

**Enhanced Mode:**
```
⏱️ Latency: 1,567ms
🔤 Tokens: 945
📚 RAG: Yes
✅ Task Completed: True
🎯 Hallucination: 0.15 (Low)
💾 Data: rag_documents
```

**Agentic Mode:**
```
⏱️ Latency: 2,012ms
🤖 Agents: Data Query
🔤 Tokens: 1,034
📚 RAG: Yes
✅ Task Completed: True
🎯 Hallucination: 0.10 (Low)
💾 Data: analytics_engine, rag_documents
```

**Winner:** Enhanced (faster, cheaper, similar quality for document retrieval)

---

## 🛠️ Advanced Usage

### Programmatic Access

```python
from metrics_tracker import get_metrics_tracker

tracker = get_metrics_tracker()

# Get recent metrics
recent = tracker.get_recent_metrics(limit=100)

# Get comparison stats
stats = tracker.get_comparison_stats(window=50)

# Calculate custom metrics
agentic_latencies = [m['latency_ms'] for m in recent if m['mode'] == 'agentic']
avg_latency = sum(agentic_latencies) / len(agentic_latencies)
```

### Custom Analysis

The metrics log (`data/metrics_log.jsonl`) can be analyzed with:

**Python:**
```python
import json

metrics = []
with open('data/metrics_log.jsonl', 'r') as f:
    for line in f:
        metrics.append(json.loads(line))

# Analyze
import pandas as pd
df = pd.DataFrame(metrics)
df.groupby('mode')['latency_ms'].mean()
```

**SQL (using DuckDB):**
```sql
SELECT
    mode,
    AVG(latency_ms) as avg_latency,
    AVG(total_tokens) as avg_tokens,
    AVG(task_completion::INT) as completion_rate
FROM read_json_auto('data/metrics_log.jsonl')
GROUP BY mode;
```

---

## 🎓 Best Practices

### 1. **Monitor Regularly**

Check metrics weekly to:
- Identify performance degradation
- Understand usage patterns
- Optimize mode selection

### 2. **Set Alerts**

Create alerts for:
- Latency > 5000ms (very slow)
- Completion rate < 90% (quality issue)
- Hallucination score > 0.5 (accuracy concern)
- Token usage spike (cost issue)

### 3. **A/B Testing**

Compare modes for your specific workload:
- Run same queries in both modes
- Measure quality differences
- Calculate cost vs quality trade-off

### 4. **Optimize Based on Data**

Use metrics to:
- Choose default mode for UI
- Route query types to best mode
- Adjust thresholds (similarity, confidence)
- Identify agent improvements needed

---

## 🐛 Troubleshooting

### "No metrics available"

**Cause:** No queries run yet or metrics file missing

**Solution:** Run some queries first, metrics will appear

### Metrics not updating in UI

**Cause:** Need to refresh

**Solution:** Click "Refresh Performance Metrics" button

### High hallucination scores

**Cause:** Responses not grounded in data

**Solutions:**
- Ensure analytics engine is working
- Upload relevant documents for RAG
- Check data source connections
- Review query phrasing

### Inconsistent latency

**Cause:** Network, server load, or cold starts

**Solutions:**
- Check network connection
- Look at avg latency over time, not single queries
- Consider caching for repeated queries

---

## 📚 Related Documentation

- [Multi-Agent Architecture](docs/MULTI_INTENT_FIX.md)
- [RAG Integration](docs/RAG_AUTO_DETECTION.md)
- [Product-Level Analysis](PRODUCT_LEVEL_ANALYSIS.md)
- [Real-World Applications](docs/REAL_WORLD_APPLICATION.md)

---

## 🔄 Future Enhancements

Planned metrics improvements:

1. **Quality Metrics**
   - User satisfaction ratings
   - Response accuracy scoring
   - Citation verification

2. **Cost Tracking**
   - Real-time cost calculation
   - Budget alerts
   - Cost optimization recommendations

3. **Performance Prediction**
   - Predict query latency before execution
   - Suggest optimal mode for query type
   - Auto-route based on complexity

4. **Detailed Traces**
   - Agent execution timeline
   - RAG retrieval details
   - LLM reasoning steps

5. **Export & Reporting**
   - CSV/Excel export
   - Weekly performance reports
   - Dashboard visualizations

---

## Summary

The metrics tracking system provides comprehensive visibility into:
- ✅ **Performance:** Latency and throughput
- 💰 **Cost:** Token usage and efficiency
- 🎯 **Quality:** Task completion and hallucination risk
- 📊 **Comparison:** Single vs multi-agent performance
- 💡 **Insights:** Data-driven optimization

Use these metrics to make informed decisions about:
- Which mode to use for different query types
- When the higher cost of agentic mode is justified
- How to improve system performance
- Whether RAG is providing value

**Remember:** Metrics are tools for improvement, not just monitoring. Use them to continuously optimize your SCM chatbot deployment!

---

**Version:** 2.4 (Metrics Tracking)
**Last Updated:** January 30, 2026
**Status:** ✅ Production Ready
