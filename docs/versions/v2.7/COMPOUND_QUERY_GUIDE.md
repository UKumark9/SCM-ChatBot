# Compound Query Processing Guide

## Overview

The SCM Chatbot features **advanced compound query processing** that intelligently handles complex questions spanning multiple domains (delays, analytics, forecasting, data queries) in a single natural language query.

**Version:** 2.7 (Enhanced Multi-Agent)
**Status:** ✅ Production Ready
**Last Updated:** January 31, 2026

---

## 🎯 What Are Compound Queries?

Compound queries are questions that involve multiple SCM domains in a single request:

**Example Compound Queries:**
```
"Show me delivery delays and forecast demand for electronics"
"What are the delays and revenue performance?"
"Show product delays and also predict demand for next month"
"Analyze revenue trends and delivery performance"
```

The system automatically:
✅ **Detects** multiple intents in your question
✅ **Decomposes** the query into domain-specific sub-queries
✅ **Routes** to appropriate specialized agents
✅ **Executes** in optimal order
✅ **Synthesizes** cross-domain insights
✅ **Combines** results into a coherent response

---

## 🚀 Key Features

### 1. **Intelligent Multi-Intent Detection**

The orchestrator uses enhanced keyword and phrase detection to identify compound queries.

**Detection Mechanisms:**
- ✅ **Keyword scoring** - Counts domain-specific keywords
- ✅ **Phrase matching** - Detects multi-word patterns (2x weight)
- ✅ **Conjunction detection** - Identifies "and", "also", "plus", etc.
- ✅ **Adaptive thresholds** - Lowers threshold when conjunctions present

**Example:**
```
Query: "Show delays and forecast demand"

Detection:
- Delay keywords: ['delays'] → score 1
- Delay phrases: [] → score 0
- Total delay score: 1

- Forecast keywords: ['forecast', 'demand'] → score 2
- Forecast phrases: ['forecast demand'] → score 2
- Total forecast score: 4

- Conjunction detected: "and" → Enables multi-intent

Result: Multi-agent query → Delay Agent + Forecasting Agent
```

### 2. **Query Decomposition**

Complex queries are broken down into agent-specific sub-queries.

**Example:**
```
Query: "Show product delays and forecast demand for electronics"

Decomposition:
- Delay Agent sub-query: "Show product delays for electronics"
- Forecasting Agent sub-query: "forecast demand for electronics"

Each agent receives the most relevant part of the query.
```

### 3. **Optimal Execution Order**

Agents execute in logical order to maximize efficiency:

**Priority Order:**
1. **Data Query Agent** (provides context for others)
2. **Delay Agent** (delivery performance)
3. **Analytics Agent** (revenue/sales data)
4. **Forecasting Agent** (predictions based on historical data)

**Example:**
```
Agents needed: [forecasting, delay, analytics]

Execution order: [delay → analytics → forecasting]
(Logical flow: performance → current state → future predictions)
```

### 4. **Cross-Agent Insights** ⭐ NEW

The system generates insights that span multiple domains!

**Insight Types:**

**Delay + Forecasting:**
```
⚠️ Supply Chain Risk: High delay rate (12%) combined with increasing
demand may lead to customer dissatisfaction. Consider increasing safety
stock or improving supplier performance.
```

**Delay + Analytics:**
```
💰 Revenue Impact: Current delay rate may be affecting customer
satisfaction and repeat purchase rates. Improving delivery performance
could boost revenue.
```

**Analytics + Forecasting:**
```
📈 Inventory Planning: Growing demand forecast suggests reviewing
inventory levels and procurement schedules to avoid stockouts.
```

**Triple Agent (All three):**
```
🔄 Holistic View: Analysis spans delivery performance, financial
metrics, and demand forecasting. Use these combined insights for
strategic planning and operational optimization.
```

### 5. **Context Sharing**

Agents can share context during multi-agent execution:

- Delay metrics → Used for cross-insights
- Revenue data → Correlated with performance
- Forecast trends → Inform strategic recommendations

---

## 📊 Enhanced Intent Detection Algorithm

### Phrase-Based Scoring

**Delay Domain:**
```python
Keywords (1 point each):
- delay, late, on-time, delivery, shipped, arrived

Phrases (2 points each):
- "delivery delay", "late delivery", "delayed order"
- "delivery performance", "on time delivery", "shipping delay"
```

**Analytics Domain:**
```python
Keywords (1 point each):
- revenue, sales, profit, customer, performance, order value

Phrases (2 points each):
- "total revenue", "customer behavior", "sales performance"
- "revenue analysis", "product performance", "top products"
```

**Forecasting Domain:**
```python
Keywords (1 point each):
- forecast, predict, future, demand, projection, estimate

Phrases (2 points each):
- "demand forecast", "predict demand", "future demand"
- "forecast sales", "demand prediction", "trend forecast"
```

### Conjunction Detection

Detected conjunctions automatically trigger multi-intent mode:
- " and "
- " also "
- " plus "
- " as well as "
- " along with "
- " with "

**Example:**
```
Query: "Show delays also forecast demand"

Without conjunction detection:
- Delay score: 1
- Forecast score: 2
Result: Single agent (Forecasting)

With conjunction detection:
- Conjunction "also" detected
- Threshold lowered for multi-intent
Result: Multi-agent (Delay + Forecasting)
```

---

## 💡 Usage Examples

### Example 1: Delay + Forecasting

**Query:**
```
"Show me delivery delays and forecast demand for the next 30 days"
```

**System Process:**
```
1. Intent Detection:
   - Delay score: 3 (delay, delivery, delays)
   - Forecast score: 4 (forecast, demand + phrase "forecast demand")
   - Conjunction: "and"
   → Multi-intent detected

2. Query Decomposition:
   - Delay: "Show me delivery delays"
   - Forecasting: "forecast demand for the next 30 days"

3. Execution Order:
   - Delay → Forecasting

4. Context Extraction:
   - Delay rate: 6.28%
   - Forecast trend: increasing

5. Cross-Insights:
   ✅ Growth Opportunity: Excellent delivery performance with
   growing demand. Good position to capture market share.
```

**Response:**
```
📊 DELIVERY PERFORMANCE
Delivery Performance Summary:
- Delay Rate: 6.28%
- On-Time Rate: 93.72%

📈 DEMAND FORECAST
30-Day Demand Forecast:
- Forecasted Demand: 2,456 units
- Historical Average: 2,234 units/month
- Trend: Increasing (+9.9%)

═══════════════════════════════════════════════════════════
💡 CROSS-DOMAIN INSIGHTS
═══════════════════════════════════════════════════════════
✅ Growth Opportunity: Excellent delivery performance with
growing demand. Good position to capture market share. Monitor
capacity for sustained performance.

────────────────────────────────────────────────────────────
🤖 Agents Executed: Delay, Forecasting
📊 Execution Order: Delay → Forecasting
📚 RAG Used By: Delay
────────────────────────────────────────────────────────────
```

### Example 2: Product-Level Multi-Domain

**Query:**
```
"Show delays for electronics and predict demand"
```

**Response:**
```
📊 DELIVERY PERFORMANCE
Product-Level Delay Analysis (All Products):

📊 Overall Statistics:
- Total Orders: 15,423
- Delayed Orders: 2,187
- Delay Rate: 14.18%

🔴 Top 5 Delayed Products:
1. Product ABC123: 22.5% delay rate
...

📈 DEMAND FORECAST
30-Day Demand Forecast:
- Forecasted Demand: 3,421 units
- Trend: Increasing

═══════════════════════════════════════════════════════════
💡 CROSS-DOMAIN INSIGHTS
═══════════════════════════════════════════════════════════
⚠️ Supply Chain Risk: High delay rate combined with increasing
demand may lead to customer dissatisfaction. Consider increasing
safety stock or improving supplier performance.

────────────────────────────────────────────────────────────
🤖 Agents Executed: Delay, Forecasting
📊 Execution Order: Delay → Forecasting
────────────────────────────────────────────────────────────
```

### Example 3: Triple Agent Query

**Query:**
```
"Show me delays, revenue performance, and demand forecast"
```

**Response:**
```
📊 DELIVERY PERFORMANCE
[Delay statistics...]

💰 REVENUE & ANALYTICS
[Revenue analysis...]

📈 DEMAND FORECAST
[Forecast details...]

═══════════════════════════════════════════════════════════
💡 CROSS-DOMAIN INSIGHTS
═══════════════════════════════════════════════════════════
💰 Revenue Impact: Current delay rate may be affecting customer
satisfaction and repeat purchase rates. Improving delivery
performance could boost revenue.

📈 Inventory Planning: Growing demand forecast suggests reviewing
inventory levels and procurement schedules to avoid stockouts.

🔄 Holistic View: Analysis spans delivery performance, financial
metrics, and demand forecasting. Use these combined insights for
strategic planning and operational optimization.

────────────────────────────────────────────────────────────
🤖 Agents Executed: Delay, Analytics, Forecasting
📊 Execution Order: Delay → Analytics → Forecasting
📚 RAG Used By: Delay, Analytics
────────────────────────────────────────────────────────────
```

### Example 4: Natural Conjunctions

**Query:**
```
"Show product delays plus forecast sales"
```

**Detected:**
- Conjunction: "plus" ✅
- Multi-intent with lowered threshold

**Query:**
```
"What are the delays along with revenue trends?"
```

**Detected:**
- Conjunction: "along with" ✅
- Multi-intent: Delay + Analytics

---

## 🔧 Configuration

### Adjust Multi-Intent Threshold

**File:** `agents/orchestrator.py` (Line ~254)

```python
# Current threshold
MULTI_INTENT_THRESHOLD = 2

# More sensitive (detects more compound queries)
MULTI_INTENT_THRESHOLD = 1

# Less sensitive (requires stronger signals)
MULTI_INTENT_THRESHOLD = 3
```

### Add Custom Phrases

**File:** `agents/orchestrator.py` (Lines ~125-150)

```python
delay_patterns = {
    'keywords': ['delay', 'late', ...],
    'phrases': [
        'delivery delay',
        'late delivery',
        # Add your custom phrases
        'slow shipping',
        'shipment delay'
    ]
}
```

### Customize Cross-Agent Insights

**File:** `agents/orchestrator.py` (Method: `_generate_cross_agent_insights`)

Add your own insight rules:

```python
# Custom insight example
if 'delay' in agents_used and 'analytics' in agents_used:
    delay_rate = context_data.get('delay_rate')
    if delay_rate and delay_rate > 15:
        insights.append(
            "🚨 Critical: Extremely high delay rate. "
            "Immediate action required."
        )
```

---

## 🧪 Testing Compound Queries

### Test Cases

**1. Basic Compound Query:**
```python
response = orchestrator.query("Show delays and forecast demand")
# Should invoke: Delay + Forecasting
```

**2. Triple Domain:**
```python
response = orchestrator.query("Show delays, revenue, and forecast")
# Should invoke: Delay + Analytics + Forecasting
# Should include cross-insights
```

**3. With Conjunction Variation:**
```python
queries = [
    "Show delays and forecast",
    "Show delays also forecast",
    "Show delays plus forecast",
    "Show delays along with forecast"
]
# All should trigger multi-agent
```

**4. Product-Level Compound:**
```python
response = orchestrator.query("Show product delays and predict demand for electronics")
# Should use product-level analysis
# Should decompose into sub-queries
```

**5. Verify Execution Order:**
```python
response = orchestrator.query("Forecast demand and show delays")
# Check execution order: Delay → Forecasting (not input order)
```

---

## 📈 Performance Metrics

All compound queries tracked with detailed metrics:

```
📊 Query Metrics
────────────────────────────────────────────────────────────
⏱️ Latency: 4,567ms
🤖 Agents Used: Delay, Analytics, Forecasting
📈 Agent Count: 3
📊 Execution Order: Delay → Analytics → Forecasting
📚 RAG Used By: Delay, Analytics
🔤 Tokens Used: 2,845 (Prompt: 1,234, Completion: 1,611)
✅ Task Completed: True
🎯 Hallucination Risk: Low (0.09)
💾 Data Sources: analytics_engine, rag_documents
────────────────────────────────────────────────────────────
```

**Key Observations:**
- Multi-agent queries have higher latency (3-5x single agent)
- More tokens used but better coverage
- Lower hallucination risk (multiple data sources)
- Higher task completion rate

---

## 🐛 Troubleshooting

### Issue: Multi-agent not triggering

**Problem:** Query should use multiple agents but only one invoked

**Solutions:**
1. Check if query contains conjunctions ("and", "also", "plus")
2. Verify keyword scores meet threshold (default: 2)
3. Add relevant phrases to pattern lists
4. Lower MULTI_INTENT_THRESHOLD to 1 for testing

**Debug:**
```python
intent = orchestrator.analyze_intent("your query here")
print(f"Detected agents: {intent['agents']}")
print(f"Multi-intent: {intent['multi_intent']}")
print(f"Sub-queries: {intent['sub_queries']}")
```

### Issue: Wrong execution order

**Problem:** Agents execute in suboptimal order

**Solution:**
Check `_get_execution_order()` priority mapping:
```python
priority = {
    'data_query': 1,  # First
    'delay': 2,
    'analytics': 3,
    'forecasting': 4  # Last
}
```

### Issue: No cross-insights generated

**Problem:** Expected cross-domain insights but none appear

**Causes:**
1. Need at least 2 agents for cross-insights
2. Context extraction may have failed
3. No matching insight rules for agent combination

**Solution:**
Enable debug logging to see extracted context:
```python
logger.setLevel(logging.DEBUG)
# Check logs for "Context data: ..."
```

---

## 🔄 Future Enhancements

Planned improvements:

1. **LLM-Based Intent Detection**
   - Use embeddings for semantic intent matching
   - Handle paraphrasing and synonyms better
   - Contextual understanding

2. **Smart Context Passing**
   - Pass delay data to forecasting agent
   - Use revenue trends in demand predictions
   - Bidirectional context sharing

3. **Adaptive Insights**
   - Learn which insights users find valuable
   - Generate industry-specific recommendations
   - Personalized insight templates

4. **Parallel Agent Execution**
   - Execute independent agents concurrently
   - Reduce latency for multi-agent queries
   - Better resource utilization

5. **Query Expansion**
   - Automatically suggest related analyses
   - "Also consider analyzing..."
   - Proactive insights

---

## 📚 Related Documentation

- [Multi-Agent Enhancement](MULTI_AGENT_ENHANCEMENT.md)
- [Product-Level Analysis](PRODUCT_LEVEL_ANALYSIS.md)
- [Metrics Tracking Guide](METRICS_TRACKING_GUIDE.md)
- [Targeted Responses](TARGETED_RESPONSES_UPDATE.md)

---

## ✅ Summary

The enhanced compound query processing provides:

✅ **Phrase-based intent detection** - More accurate than keywords alone
✅ **Conjunction detection** - Identifies explicit multi-intent signals
✅ **Query decomposition** - Domain-specific sub-queries
✅ **Optimal execution order** - Logical agent sequencing
✅ **Cross-agent insights** ⭐ - Synthesized multi-domain recommendations
✅ **Context sharing** - Agents leverage each other's results
✅ **Comprehensive metrics** - Full tracking of multi-agent execution

**Key Principle:** *The system doesn't just route to multiple agents—it orchestrates them intelligently to provide cohesive, actionable insights that span multiple SCM domains.*

---

**Example Power Query:**
```
"Show me product delays, revenue impact, and demand forecast for electronics"

Result:
→ Product-level delay analysis
→ Revenue correlation with delays
→ Category-specific demand forecast
→ Cross-insights on supply chain risks
→ Actionable recommendations
```

---

**Version:** 2.7 (Compound Query Processing)
**Last Updated:** January 31, 2026
**Status:** ✅ Production Ready
