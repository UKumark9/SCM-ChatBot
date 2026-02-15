# agents/analytics_agent.py - Revenue and Performance Analytics Agent

## Purpose
Specialized agent for revenue analysis, product performance, and sales metrics. Supports classification-based intelligent RAG usage for policy vs data queries.

## Key Components

### Class: AnalyticsAgent
Handles revenue, product, and sales analytics queries.

**Initialization Parameters:**
- `analytics_engine`: SCMAnalytics instance
- `data_wrapper`: Database wrapper
- `rag_module`: RAGModule instance (optional)

## Core Methods

### `query(user_query, classification=None)`
Processes analytics queries with classification support.

**Parameters:**
- `user_query` (str): User's question
- `classification` (dict): Intent classification (optional)

**Returns:** dict with response and metadata

**Query Types:**

1. **Revenue Queries** (DATA):
   - "What is total revenue?"
   - "Show revenue by product"
   - "Revenue breakdown by state"

2. **Product Performance** (DATA):
   - "Top selling products"
   - "Product sales analysis"
   - "Which products have lowest sales?"

3. **Policy Questions** (POLICY):
   - "What is the revenue target?"
   - "Define product performance criteria"
   - "Explain sales thresholds"

## Supported Query Types

### Total Revenue
- "What is total revenue?"
- "Show overall sales"
- "Total sales amount"

**Response:**
```
Total Revenue: $1,245,678.90
```

### Revenue by Product
- "Revenue by product"
- "Product sales breakdown"
- "Show product revenue"

**Response:**
```
Revenue by Product:
1. Product A: $456,789.00 (36.7%)
2. Product B: $345,678.00 (27.8%)
3. Product C: $234,567.00 (18.8%)
...
```

### Revenue by State
- "Revenue by state"
- "Geographic revenue breakdown"
- "Which states generate most revenue?"

**Response:**
```
Revenue by State:
1. California: $523,456.78 (42.0%)
2. Texas: $345,678.90 (27.7%)
3. New York: $234,567.89 (18.8%)
...
```

### Top/Bottom Products
- "Top selling products"
- "Best performing products"
- "Worst performing products"

**Response:**
```
Top 10 Products by Revenue:
1. Product X: $123,456.00
2. Product Y: $98,765.00
...
```

## Helper Methods

### `_analyze_revenue_metrics()`
Calculates revenue metrics from database.

**Returns:** dict with:
- `total_revenue`: Overall revenue
- `revenue_by_product`: Product breakdown
- `revenue_by_state`: Geographic breakdown
- `top_products`: Top performing products
- `avg_order_value`: Average order value

### `_get_product_performance(top_n=10)`
Retrieves top/bottom product performance.

**Parameters:**
- `top_n` (int): Number of products to return

**Returns:** list of product performance dicts

### `_format_revenue_display(metrics)`
Formats revenue metrics for display.

**Parameters:**
- `metrics` (dict): Raw metrics

**Returns:** str (formatted display)

### `_calculate_percentages(breakdown_dict, total)`
Calculates percentages for breakdowns.

**Parameters:**
- `breakdown_dict` (dict): Revenue breakdown
- `total` (float): Total revenue

**Returns:** dict with values and percentages

## Integration with Classification

### Data Query (Fast)
```python
Query: "What is total revenue?"
Classification: DATA (use_rag=False)
→ Database query only
→ Time: ~2-3s
→ Response: "$1,245,678.90"
```

### Policy Query (RAG)
```python
Query: "What is the revenue target?"
Classification: POLICY (use_rag=True)
→ RAG document retrieval
→ Time: ~15s
→ Response: Policy definitions
```

### Mixed Query
```python
Query: "Compare actual revenue with target"
Classification: MIXED (use_rag=True, use_database=True)
→ Both sources
→ Time: ~18s
→ Response: Comparison with policy context
```

## Performance Characteristics

### Simple Revenue Query
- **Time**: 2-3 seconds
- **Sources**: Database only
- **Optimization**: No RAG overhead

### Complex Analytics
- **Time**: 4-6 seconds
- **Sources**: Database with calculations
- **Operations**: Aggregations, grouping

### With Policy Context
- **Time**: 15-18 seconds
- **Sources**: RAG + Database
- **Use Case**: Policy comparisons

## Response Examples

### Simple Revenue
```
Total Revenue: $1,245,678.90

────────────────────────────────────────────────────────────
🤖 Agent: Analytics Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 2.15s
────────────────────────────────────────────────────────────
```

### Product Breakdown
```
Revenue by Product:

| Product | Revenue | Percentage |
|---------|----------|-----------|
| Product A | $456,789.00 | 36.7% |
| Product B | $345,678.00 | 27.8% |
| Product C | $234,567.00 | 18.8% |

────────────────────────────────────────────────────────────
🤖 Agent: Analytics Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 3.87s
────────────────────────────────────────────────────────────
```

## Dependencies

### Internal Modules
- `analytics_engine`: Revenue calculations
- `data_wrapper`: Database access
- `rag`: Policy retrieval (optional)
- `ui_formatter`: Response formatting

## Error Handling

### No Data Available
- Returns informative message
- Suggests data refresh or different query

### Calculation Error
- Logs error details
- Returns partial results if available

## Usage Examples

### Revenue Analysis
```python
agent = AnalyticsAgent(analytics, data)
result = agent.query("total revenue?", classification={'query_type': 'data'})
# Fast, focused response
```

### Product Performance
```python
result = agent.query("top products?", classification={'query_type': 'data'})
# Returns top performers
```

### Policy Comparison
```python
result = agent.query("revenue vs target?", classification={'query_type': 'mixed'})
# Uses both RAG and database
```

## Integration Points

### Used By
- `agents/orchestrator.py`: Routes revenue/analytics queries

### Uses
- `analytics_engine.calculate_revenue()`: Metrics
- `rag.retrieve_context()`: Policy docs (when needed)
- `UIFormatter`: Response formatting
