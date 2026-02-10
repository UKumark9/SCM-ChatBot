# agents/data_query_agent.py - Raw Data Retrieval Agent

## Purpose
Specialized agent for retrieving raw data from database. Handles "show", "list", "get" queries that require direct database access without complex analytics.

## Key Components

### Class: DataQueryAgent
Handles raw data retrieval queries.

**Initialization Parameters:**
- `analytics_engine`: SCMAnalytics instance
- `data_wrapper`: Database wrapper
- `rag_module`: RAGModule instance (optional)

## Core Methods

### `query(user_query, classification=None)`
Processes data retrieval queries with classification support.

**Parameters:**
- `user_query` (str): User's question
- `classification` (dict): Intent classification (optional)

**Returns:** dict with data response

**Query Types:**

1. **List Queries** (DATA):
   - "Show all orders"
   - "List products"
   - "Get customers"

2. **Filtered Queries** (DATA):
   - "Show orders for California"
   - "List products with low stock"
   - "Get delayed deliveries"

3. **Count Queries** (DATA):
   - "How many orders?"
   - "Count products"
   - "Total customers"

## Supported Queries

### Show Orders
- "Show all orders"
- "List orders"
- "Get recent orders"

**Response:**
```
Recent Orders:

| Order ID | Customer | Product | Status | Date |
|----------|----------|---------|--------|------|
| 12345 | Acme Corp | Product A | Delivered | 2026-02-05 |
| 12346 | Tech Inc | Product B | In Transit | 2026-02-06 |
| 12347 | Global LLC | Product C | Delayed | 2026-02-07 |
...

Showing 10 of 1,234 total orders
```

### List Products
- "List all products"
- "Show products"
- "Get product catalog"

**Response:**
```
Product Catalog:

1. Product A - $45.99 (In Stock: 1,250)
2. Product B - $32.50 (In Stock: 980)
3. Product C - $67.00 (In Stock: 450)
...

Total Products: 47
```

### Filtered Data
- "Show orders for Texas"
- "List delayed deliveries"
- "Get high-value orders"

**Response:**
```
Orders for Texas:

| Order ID | Amount | Status | Days Since Order |
|----------|--------|--------|-----------------|
| 12350 | $1,250.00 | Delivered | 5 |
| 12351 | $890.50 | In Transit | 2 |
...

Total: 45 orders
Total Value: $52,340.00
```

### Count Queries
- "How many orders?"
- "Count delayed deliveries"
- "Total products"

**Response:**
```
Total Orders: 1,234
- Delivered: 1,156 (93.7%)
- In Transit: 56 (4.5%)
- Delayed: 22 (1.8%)
```

## Helper Methods

### `_get_orders(filters=None, limit=10)`
Retrieves orders from database.

**Parameters:**
- `filters` (dict): Filter criteria (state, status, etc.)
- `limit` (int): Maximum records to return

**Returns:** list of order dicts

### `_get_products(filters=None)`
Retrieves product catalog.

**Parameters:**
- `filters` (dict): Filter criteria

**Returns:** list of product dicts

### `_get_customers(filters=None)`
Retrieves customer data.

**Parameters:**
- `filters` (dict): Filter criteria

**Returns:** list of customer dicts

### `_parse_filters(query)`
Extracts filters from natural language query.

**Parameters:**
- `query` (str): User's question

**Returns:** dict with filter criteria

**Example:**
```python
_parse_filters("Show orders for California")
# Returns: {'state': 'CA'}

_parse_filters("List delayed deliveries")
# Returns: {'status': 'Delayed'}
```

### `_format_table(data, columns)`
Formats data as table.

**Parameters:**
- `data` (list): Data rows
- `columns` (list): Column names

**Returns:** str (markdown table)

## Integration with Classification

### Pure Data Query
```python
Query: "Show all orders"
Classification: DATA (use_rag=False)
→ Database query only
→ Time: ~1-2s
→ Response: Order list
```

### Never Uses RAG
- DataQueryAgent focuses on raw data retrieval
- Classification almost always DATA type
- Minimal processing, direct database access

## Performance Characteristics

### Simple List Query
- **Time**: 1-2 seconds
- **Operation**: Direct SELECT query
- **Optimization**: Indexed columns, LIMIT clause

### Filtered Query
- **Time**: 2-4 seconds
- **Operation**: WHERE clause filtering
- **Optimization**: Indexed filter columns

### Large Result Sets
- **Time**: 3-5 seconds
- **Operation**: Pagination, aggregation
- **Optimization**: LIMIT + OFFSET

## Response Examples

### Order List
```
Orders:

| ID | Customer | Product | Amount | Status |
|----|----------|---------|--------|--------|
| 12345 | Acme Corp | Widget A | $1,250.00 | Delivered |
| 12346 | Tech Inc | Widget B | $890.50 | In Transit |
| 12347 | Global LLC | Widget C | $2,340.00 | Delayed |

Showing 10 of 1,234 orders

────────────────────────────────────────────────────────────
🤖 Agent: Data Query Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 1.87s
────────────────────────────────────────────────────────────
```

### Count Query
```
Total Orders: 1,234

Status Breakdown:
✅ Delivered: 1,156 (93.7%)
🚚 In Transit: 56 (4.5%)
⚠️ Delayed: 22 (1.8%)

────────────────────────────────────────────────────────────
🤖 Agent: Data Query Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 0.95s
────────────────────────────────────────────────────────────
```

## Query Parsing

### Keywords Detected
- **List/Show**: Retrieve records
- **Get**: Fetch specific data
- **Count/How many**: Aggregation
- **State names**: Geographic filtering
- **Status terms**: Status filtering

### Filter Extraction
```python
"Show orders for California" → {'state': 'CA'}
"List delayed deliveries" → {'status': 'Delayed'}
"Get high-value orders" → {'min_amount': 1000}
```

## Pagination

### Default Limits
- Orders: 10 per page
- Products: 20 per page
- Large tables: 25 per page

### Pagination Info
```
Showing 10 of 1,234 total orders
Page 1 of 124
```

## Dependencies

### Internal Modules
- `data_wrapper`: Database access
- `ui_formatter`: Table formatting

### External Libraries
- `logging`: Query logging

## Error Handling

### No Results Found
```
No orders found matching your criteria.

Try:
• Removing filters
• Checking spelling
• Broadening search criteria
```

### Database Error
```
❌ Error retrieving data from database.
Please try again or contact support.
```

### Invalid Filter
```
⚠️ Unrecognized filter: "XYZ"
Supported filters: state, status, product, date
```

## Usage Examples

### List All Orders
```python
agent = DataQueryAgent(analytics, data)
result = agent.query("show orders", classification={'query_type': 'data'})
# Returns order list
```

### Filtered Query
```python
result = agent.query("orders for Texas")
# Returns Texas orders only
```

### Count Query
```python
result = agent.query("how many orders?")
# Returns count with breakdown
```

## Integration Points

### Used By
- `agents/orchestrator.py`: Routes list/show/get queries

### Uses
- `data_wrapper.execute_query()`: Database access
- `UIFormatter.format_table()`: Table formatting

## Optimization

### Indexing
- Orders indexed by: order_id, customer, state, status
- Products indexed by: product_id, category
- Fast filtering on indexed columns

### Query Limits
- Default LIMIT to prevent large result sets
- Pagination for better performance
- Count queries use COUNT() for efficiency

## Best Practices

1. **Always use LIMIT**: Prevent overwhelming responses
2. **Index filter columns**: Fast WHERE clause execution
3. **Format as tables**: Better readability
4. **Include totals**: Context for partial results
5. **Clear error messages**: Help users refine queries
