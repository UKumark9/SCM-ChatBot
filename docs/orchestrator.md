# Agent Orchestrator

## Purpose

The `AgentOrchestrator` is the **central controller** for the multi-agent SCM (Supply Chain Management) system. It receives user queries, determines which specialized agent(s) should handle them, and returns formatted responses.

## Architecture

### Initialization (lines 35-123)
Sets up:
- **4 specialized agents**: `DelayAgent`, `AnalyticsAgent`, `ForecastingAgent`, `DataQueryAgent`
- **LLM client**: Groq's `llama-3.3-70b-versatile` via LangChain (temperature=0.1)
- **IntentClassifier**: for query type classification (policy vs data vs mixed)
- **ForecastingEngine**: SARIMA-based forecasting (demand, revenue, delay rate, category)
- Each agent receives the shared LLM client, RAG module, and its relevant data sources

### Intent Analysis — Hybrid Approach (lines 125-288)

`analyze_intent()` uses a **two-tier hybrid routing system**:

#### Tier 1: Keyword/Phrase Scoring (fast path, ~0ms)

Scores the query against 4 agent domains using substring matching:

| Agent | Trigger Keywords | Trigger Phrases |
|-------|-----------------|-----------------|
| Delay | delay, late, delivery, on-time, shipped, arrived | delivery delay, late delivery, delivery performance |
| Analytics | revenue, sales, profit, performance, behavior, analysis | total revenue, customer behavior, sales performance |
| Forecasting | forecast, predict, demand, sarima, prophet, seasonal | demand forecast, revenue forecast, time series forecast |
| Data Query | show, list, get, find, display, customers, orders, top | show me, find order, top products, monthly trend |

Scoring: keywords = +1 point, phrases = +2 points. Confidence = `min(max_score / 10, 0.95)`.

Routing decisions:
- **Multi-intent**: 2+ agents score >= 2 (or >= 1 with conjunctions like "and") -> confidence 0.85
- **Comprehensive**: keywords like "report", "overview" score >= 2 -> confidence 0.90
- **Single-intent**: highest-scoring agent -> confidence 0.10-0.95
- **No match**: defaults to analytics -> confidence 0.50

#### Tier 2: LLM Fallback Router (lines 290-406)

When keyword confidence < 0.6, `_llm_route()` is invoked to make the routing decision using the LLM:

- **Model**: same `self.llm_client` (Llama 3.3 70B via Groq), bound to temperature=0 for deterministic output
- **Prompt**: system message describing the 4 agents + JSON schema for structured output
- **Output**: JSON with `agent`, `agents`, `confidence`, `multi_intent`, `sub_queries`, `execution_order`
- **Validation**: agent names checked against whitelist, confidence clamped 0.0-0.95, missing fields get defaults
- **Fallback**: on any error (network, JSON parse, validation), silently returns the keyword result with a warning log
- **Provenance**: adds `'routed_by': 'llm'` to the intent dict for logging/debugging

| Scenario | Keyword Confidence | LLM Triggered? |
|----------|-------------------|----------------|
| No keywords match (score=0) | 0.50 | Yes |
| Weak match (score 1-5) | 0.10-0.50 | Yes |
| Strong match (score >= 6) | >= 0.60 | No |
| Multi-intent detected | 0.85 | No |
| Comprehensive report | 0.90 | No |

### Query Routing (lines 476-546)
`route_query()` is the main dispatch method:
1. Classifies the query via `IntentClassifier` (RAG vs database vs both)
2. Runs `analyze_intent()` (keyword scoring + optional LLM fallback)
3. Logs routing provenance (`routed_by=keyword` or `routed_by=llm`)
4. Dispatches to the appropriate handler (single agent, multi-agent, or comprehensive)
5. Attaches metadata (intent, classification, orchestrator type)
6. Stores in conversation history

### Query Decomposition (lines 408-453)
`_decompose_query()` splits compound queries on conjunctions ("and", "also", "plus") and assigns segments to agents based on keyword presence.

### Execution Order (lines 455-474)
`_get_execution_order()` determines agent priority: data_query (1) -> delay (2) -> analytics (3) -> forecasting (4). Data query runs first because it provides context for other agents.

### Multi-Intent Handling (lines 548-669)
For compound queries (e.g., "show delay rate and forecast demand"):
1. **Decomposes** the query into sub-queries per agent
2. **Executes** agents in priority order
3. **Extracts** intermediate metrics (delay rate, revenue, forecast trend) for cross-agent analysis
4. **Combines** results with markdown section headers separated by `---`
5. **Generates cross-agent insights** (e.g., "high delays + growing demand = supply chain risk")

### Cross-Agent Insights (lines 711-786)
Rule-based insight generation from extracted metrics across agent domains:

| Agent Pair | Insight Example |
|-----------|----------------|
| Delay + Forecasting | High delay + increasing demand = supply chain risk |
| Delay + Forecasting | Low delay + increasing demand = growth opportunity |
| Delay + Analytics | High delay rate = potential revenue impact |
| Analytics + Forecasting | Increasing demand = review inventory levels |
| 3+ agents | Holistic view recommendation for strategic planning |

### Comprehensive Query Handler (lines 788-831)
Triggered by keywords like "comprehensive", "report", "overview". Invokes all 3 main agents (delay, analytics, forecasting) with predefined queries and combines results under a single report heading.

### Public API (lines 833-916)
`query()` is the main entry point called by the UI:
1. Starts metrics tracking (latency, data sources, hallucination score)
2. Calls `route_query()`
3. Formats the response via `UIFormatter.format_response()`
4. Returns a formatted markdown string

### Helper Methods
- `_format_compact_metrics()` (lines 918-955): Formats latency, data sources, hallucination score as compact icons
- `_build_agent_info()` (lines 957-977): Builds agent execution info footer with status
- `clear_history()` (lines 979-982): Clears conversation history

## Data Flow
```
User Query
  |
  v
IntentClassifier.classify_query()  -->  policy / data / mixed
  |
  v
analyze_intent()
  |-- Keyword Scoring (Tier 1)
  |     confidence >= 0.6?  -->  use keyword result
  |     confidence < 0.6?   -->  _llm_route() (Tier 2, LLM fallback)
  |
  v
route_query()
  |-- Single Agent   -->  delay / analytics / forecasting / data_query
  |-- Multi-Agent    -->  _handle_multi_intent_query()
  |-- Comprehensive  -->  _handle_comprehensive_query()
  |
  v
UIFormatter.format_response()
  |
  v
Formatted Markdown Response
```

## LLM Usage Summary

| Component | Uses LLM? | Purpose |
|-----------|-----------|---------|
| Keyword scoring (`analyze_intent`) | No | Fast substring matching |
| LLM fallback (`_llm_route`) | Yes (conditional) | Route ambiguous queries |
| Query decomposition | No | String split on conjunctions |
| Cross-agent insights | No | Hardcoded if/else rules |
| Execution order | No | Static priority map |
| Agent responses | Yes (always) | LangChain tool-calling agents generate answers |
