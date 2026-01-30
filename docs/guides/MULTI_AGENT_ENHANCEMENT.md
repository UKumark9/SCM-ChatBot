# Multi-Agent Processing Enhancement

## Overview

The SCM Chatbot now features **enhanced multi-agent processing** that intelligently handles complex queries involving multiple domains (delays, forecasting, analytics, and data queries) in a single question.

**Version:** 2.6
**Status:** ✅ Production Ready
**Last Updated:** January 31, 2026

---

## 🚀 Key Features

### 1. **Intelligent Intent Detection**

The orchestrator automatically detects when a query requires multiple agents and routes accordingly.

**Example:**
```
User: "Show me product delays and forecast demand for electronics"

System detects:
- Delay intent (keywords: "delays", "product")
- Forecasting intent (keywords: "forecast", "demand")

Routes to:
✅ Delay Agent → Product-level delay analysis
✅ Forecasting Agent → Demand forecasting
✅ Combines results into unified response
```

### 2. **Product-Level Analysis Integration**

Both rule-based and LangChain agents now support product-level queries with natural language parsing.

**Capabilities:**
- ✅ Detect product mentions ("product ABC123")
- ✅ Detect category mentions ("electronics", "furniture", etc.)
- ✅ Show top delayed products when no specific product specified
- ✅ Show top delayed categories across all products

### 3. **Seamless Result Combination**

Multiple agent results are intelligently combined with section headers and summaries.

---

## 📊 How It Works

### Multi-Intent Detection Algorithm

**File:** [agents/orchestrator.py](agents/orchestrator.py) (Lines 102-180)

```python
# Keyword scoring system
delay_keywords = ['delay', 'late', 'on-time', 'delivery', 'shipped']
analytics_keywords = ['revenue', 'sales', 'profit', 'customer', 'product']
forecast_keywords = ['forecast', 'predict', 'future', 'demand', 'trend']
data_keywords = ['show', 'list', 'get', 'find', 'order id']

# Calculate scores
delay_score = sum(1 for kw in delay_keywords if kw in query_lower)
analytics_score = sum(1 for kw in analytics_keywords if kw in query_lower)
# ... etc

# Multi-intent threshold
MULTI_INTENT_THRESHOLD = 2

# Detect multi-intent queries
high_scoring_agents = [agent for agent, score in scores.items()
                       if score >= MULTI_INTENT_THRESHOLD]

if len(high_scoring_agents) > 1:
    # Multi-agent query detected
    intent['multi_intent'] = True
    intent['agents'] = high_scoring_agents
```

### Product Query Detection (Rule-Based Mode)

**File:** [agents/delay_agent.py](agents/delay_agent.py) (Lines 258-295)

```python
# Priority detection - product queries handled FIRST
if 'product' in query_lower or 'category' in query_lower or 'item' in query_lower:
    response = self._get_product_delays(user_query)
# Then geographic queries
elif 'state' in query_lower or 'where' in query_lower:
    response = self._get_state_delays()
# Then trends
elif 'trend' in query_lower or 'over time' in query_lower:
    response = self._get_delay_trends()
# Then specific metrics
elif 'what is the delay rate' in query_lower:
    response = f"The current delivery delay rate is **{result['delay_rate_percentage']:.2f}%**"
# Default summary
else:
    response = "Delivery Performance Summary..."
```

### Natural Language Parsing

**File:** [agents/delay_agent.py](agents/delay_agent.py) (Lines 166-199)

```python
def _get_product_delays(self, query: str = "") -> str:
    """Parse natural language for product/category"""

    # Structured format (from LangChain)
    if query.startswith("product_id:"):
        product_id = query.replace("product_id:", "").strip()
    elif query.startswith("category:"):
        category = query.replace("category:", "").strip()

    # Natural language parsing
    else:
        # Detect category names
        categories = ['electronics', 'furniture', 'clothing', 'toys', ...]
        for cat in categories:
            if cat in query_lower:
                category = cat.title()
                break

        # Detect "product X" pattern
        product_match = re.search(r'product\s+([A-Za-z0-9_-]+)', query_lower)
        if product_match:
            product_id = product_match.group(1)
```

---

## 💡 Usage Examples

### Example 1: Multi-Agent Query

**Query:**
```
"Show me delivery delays by state and forecast demand for the next 30 days"
```

**System Response:**
```
📊 DELIVERY PERFORMANCE
[State-level delay breakdown from Delay Agent]

📈 DEMAND FORECAST
[30-day forecast from Forecasting Agent]

────────────────────────────────────────────────────────────
🤖 Agents Executed: Delay, Forecasting
📚 RAG Used By: Delay
────────────────────────────────────────────────────────────
```

### Example 2: Product-Level Delay Analysis

**Query:**
```
"What are the delays for electronics products?"
```

**System Response:**
```
Product-Level Delay Analysis (All Products):

📊 Overall Statistics:
- Total Orders: 15,423
- Delayed Orders: 2,187
- Delay Rate: 14.18%
- On-Time Rate: 85.82%
- Average Delay: 8.5 days
- Max Delay: 45.2 days

🔴 Top 5 Delayed Products:
1. Product ABC123: 22.5% delay rate (45/200 orders)
2. Product XYZ789: 18.3% delay rate (32/175 orders)
3. Product DEF456: 16.1% delay rate (28/174 orders)
4. Product GHI321: 15.8% delay rate (25/158 orders)
5. Product JKL654: 14.2% delay rate (21/148 orders)

📦 Top 5 Delayed Categories:
1. Electronics: 14.2% delay rate (234/1,648 orders)
2. Furniture: 11.5% delay rate (156/1,357 orders)
3. Sports: 10.8% delay rate (89/824 orders)
4. Books: 9.2% delay rate (78/848 orders)
5. Toys: 8.5% delay rate (65/765 orders)
```

### Example 3: Specific Product Query

**Query:**
```
"Show delays for product ABC123"
```

**System Response:**
```
Product-Level Delay Analysis (Product ABC123):

📊 Overall Statistics:
- Total Orders: 200
- Delayed Orders: 45
- Delay Rate: 22.50%
- On-Time Rate: 77.50%
- Average Delay: 12.3 days
- Max Delay: 35.0 days
```

### Example 4: Category Query

**Query:**
```
"What are the delays for electronics category?"
```

**System Response:**
```
Product-Level Delay Analysis (Category Electronics):

📊 Overall Statistics:
- Total Orders: 1,648
- Delayed Orders: 234
- Delay Rate: 14.20%
- On-Time Rate: 85.80%
- Average Delay: 9.8 days
- Max Delay: 42.5 days
```

### Example 5: Combined Product + Forecast Query

**Query:**
```
"Show product delays and forecast demand"
```

**System Response:**
```
📊 DELIVERY PERFORMANCE
[Product-level delay analysis with top delayed products/categories]

📈 DEMAND FORECAST
[Overall demand forecast for 30 days]

────────────────────────────────────────────────────────────
🤖 Agents Executed: Delay, Forecasting
📈 Agent Count: 2
────────────────────────────────────────────────────────────
```

---

## 🎯 Keyword Detection

### Delay Agent Triggers

**Product-Level Queries:**
- "product" → Product analysis
- "category" → Category analysis
- "item" → Product analysis
- "electronics", "furniture", etc. → Specific category

**Geographic Queries:**
- "state"
- "where"
- "geographic"

**Temporal Queries:**
- "trend"
- "over time"

**Specific Metrics:**
- "what is the delay rate"
- "on-time rate"
- "how many delayed"
- "average delay"
- "maximum delay"

**Comprehensive Queries:**
- "statistics"
- "show all"
- "comprehensive"
- "analyze"
- "overview"

### Multi-Intent Triggers

**Delay + Forecasting:**
- "delays" + "forecast"
- "delivery" + "predict"
- "late" + "demand"

**Delay + Analytics:**
- "delays" + "revenue"
- "delivery" + "sales"
- "on-time" + "customer"

**Analytics + Forecasting:**
- "revenue" + "forecast"
- "sales" + "predict"
- "customer" + "demand"

**Triple Agent (Delay + Analytics + Forecasting):**
- "delays" + "revenue" + "forecast"
- "comprehensive report"
- "full analysis"

---

## 🔧 Technical Implementation

### Files Modified

1. **agents/delay_agent.py**
   - Added product/category keyword detection (line 264)
   - Enhanced `_get_product_delays()` with natural language parsing (lines 166-199)
   - Prioritized product queries in rule-based routing (lines 258-295)

2. **agents/orchestrator.py**
   - Multi-intent detection already implemented (lines 102-180)
   - `_handle_multi_intent_query()` for multi-agent coordination (lines 237-326)

3. **tools/analytics.py**
   - `analyze_product_delays()` method (lines 53-158)
   - Returns top delayed products and categories when no filter specified

### Detection Priority (Rule-Based Mode)

1. **Product/Category queries** (HIGHEST PRIORITY)
2. Geographic queries
3. Temporal/trend queries
4. Specific metric questions
5. Comprehensive analysis requests
6. Default summary (FALLBACK)

---

## 📈 Performance Metrics

All multi-agent queries are tracked with comprehensive metrics:

- ✅ **Latency:** Time to execute all agents
- ✅ **Agent Count:** Number of agents invoked
- ✅ **RAG Usage:** Which agents used RAG context
- ✅ **Token Usage:** Total tokens across all agents
- ✅ **Task Completion:** Success rate
- ✅ **Hallucination Score:** Data grounding quality

**Example Metrics Display:**
```
────────────────────────────────────────────────────────────
📊 Query Metrics
────────────────────────────────────────────────────────────
⏱️ Latency: 3,245ms
🤖 Agents Used: Delay, Forecasting
📈 Agent Count: 2
📚 RAG Used By: Delay
🔤 Tokens Used: 1,876 (Prompt: 892, Completion: 984)
✅ Task Completed: True
🎯 Hallucination Risk: Low (0.08)
💾 Data Sources: analytics_engine, rag_documents
────────────────────────────────────────────────────────────
```

---

## 🛠️ Configuration

### Adjust Multi-Intent Threshold

To make multi-agent detection more or less sensitive:

**File:** `agents/orchestrator.py` (Line 156)

```python
# Current value: 2
MULTI_INTENT_THRESHOLD = 2

# More sensitive (detects more multi-agent queries)
MULTI_INTENT_THRESHOLD = 1

# Less sensitive (requires stronger signals)
MULTI_INTENT_THRESHOLD = 3
```

### Add Custom Categories

To detect additional product categories:

**File:** `agents/delay_agent.py` (Line 191)

```python
categories = ['electronics', 'furniture', 'clothing', 'toys', 'books',
              'sports', 'home', 'garden', 'automotive', 'food',
              # Add your custom categories here
              'appliances', 'jewelry', 'beauty', 'tools']
```

---

## 🧪 Testing

### Test Multi-Agent Processing

```python
# Test in main.py or notebook
from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator(analytics, data_wrapper, rag_module)

# Multi-agent query
response = orchestrator.query("Show delays and forecast demand")

# Should invoke multiple agents
print(response)
```

### Test Product Detection

```python
# Test product-level delay analysis
response = orchestrator.query("What are the delays for electronics?")

# Should show product-level analysis with top delayed products
print(response)
```

### Verify Metrics

```python
from metrics_tracker import get_metrics_tracker

tracker = get_metrics_tracker()
stats = tracker.get_comparison_stats(window=10)

# Check if multi-agent queries are tracked
print(stats)
```

---

## 🐛 Troubleshooting

### Issue: Products not showing in delay response

**Problem:** Query about products returns generic delay summary

**Solution:**
- Ensure query contains "product", "category", or specific category name
- Check that analytics.analyze_product_delays() is being called
- Verify data has product information (order_items + products tables)

### Issue: Multi-agent not triggering

**Problem:** Query should use multiple agents but only one is invoked

**Solutions:**
- Lower MULTI_INTENT_THRESHOLD from 2 to 1
- Add more keywords to intent detection lists
- Check that query contains keywords from 2+ agent categories

### Issue: Wrong agent selected

**Problem:** Query routed to incorrect agent

**Solutions:**
- Review keyword lists in orchestrator.py (lines 124-137)
- Add domain-specific keywords
- Check query for ambiguous terms

---

## 🔄 Future Enhancements

Planned improvements:

1. **Semantic Intent Detection**
   - Use LLM embeddings for intent classification
   - Handle synonyms and variations better
   - Context-aware routing

2. **Query Decomposition**
   - Break complex queries into sub-queries
   - Optimal agent execution order
   - Dependency resolution

3. **Cross-Agent Analysis**
   - Correlate delays with revenue impact
   - Link forecast to delay patterns
   - Product recommendations based on multi-factor analysis

4. **Adaptive Routing**
   - Learn from user feedback
   - Optimize agent selection over time
   - Personalized routing based on user preferences

5. **Parallel Execution**
   - Execute independent agents concurrently
   - Reduce overall latency
   - Better resource utilization

---

## 📚 Related Documentation

- **[Compound Query Processing Guide](COMPOUND_QUERY_GUIDE.md)** ⭐ NEW - Complete guide to enhanced multi-agent capabilities
- [Product-Level Analysis Guide](PRODUCT_LEVEL_ANALYSIS.md)
- [Metrics Tracking Guide](METRICS_TRACKING_GUIDE.md)
- [Targeted Responses Update](TARGETED_RESPONSES_UPDATE.md)
- [Multi-Intent Fix Documentation](docs/MULTI_INTENT_FIX.md)

---

## 🆕 Version 2.7 Enhancements

**Enhanced Compound Query Processing:**
- ✅ **Phrase-based intent detection** (2x weight vs. keywords)
- ✅ **Conjunction detection** ("and", "also", "plus", etc.)
- ✅ **Query decomposition** into agent-specific sub-queries
- ✅ **Optimal execution ordering** (data_query → delay → analytics → forecasting)
- ✅ **Cross-agent insights** ⭐ - Synthesized multi-domain recommendations
- ✅ **Context sharing** between agents during execution

**See:** [Compound Query Processing Guide](COMPOUND_QUERY_GUIDE.md) for complete details.

---

## ✅ Summary

The multi-agent processing enhancement provides:

✅ **Intelligent routing** to multiple agents in a single query
✅ **Product-level analysis** with natural language understanding
✅ **Seamless result combination** with proper formatting
✅ **Comprehensive metrics** tracking for all multi-agent queries
✅ **Flexible configuration** for different use cases
✅ **Robust error handling** and fallbacks
✅ **Enhanced intent detection** with phrases and conjunctions ⭐ NEW
✅ **Query decomposition** for agent-specific sub-queries ⭐ NEW
✅ **Cross-domain insights** spanning multiple agents ⭐ NEW

**Key Principle:** *The system automatically detects complex intents, orchestrates specialized agents intelligently, and synthesizes insights that span multiple SCM domains.*

**Example Power Query:**
```
"Show product delays and forecast demand for electronics"

→ Detects multi-intent (delay + forecasting)
→ Decomposes into sub-queries
→ Executes in optimal order
→ Generates cross-agent insights
→ Provides actionable recommendations
```

---

**Version:** 2.7 (Enhanced Multi-Agent with Compound Queries)
**Last Updated:** January 31, 2026
**Status:** ✅ Production Ready
