# SCM Chatbot - Comprehensive Query Guide

## Overview

The Enhanced SCM Chatbot supports both **rule-based** and **AI-powered** (LLM) responses with optional **RAG (Retrieval-Augmented Generation)** for semantic search. This guide provides example prompts for accurate and insightful results.

---

## Running the Chatbot

### Basic Usage
```bash
# Run with enhanced AI (default)
python main.py

# Run in CLI mode
python main.py --mode cli

# Run with RAG for semantic search
python main.py --rag

# Run legacy rule-based mode
python main.py --legacy
```

### Options
- `--mode`: Choose `cli` or `ui` (default: `ui`)
- `--data`: Choose `train` or `test` dataset (default: `train`)
- `--enhanced`: Use AI-powered chatbot (default: `True`)
- `--legacy`: Use rule-based chatbot only
- `--rag`: Enable semantic search with RAG

---

## Query Categories & Examples

### 1. Delivery Performance Analysis

#### Basic Queries
```
What is the delivery delay rate?
Show delivery performance
Analyze delivery delays
How many orders are delayed?
What's our on-time delivery rate?
```

#### Advanced Queries
```
Which states have the worst delivery delays?
Compare delivery performance across regions
What is the average delay time for late deliveries?
Show me states with best on-time delivery
What's the median delay for orders?
How has delivery performance changed over time?
```

#### Expected Insights
- Total orders and delayed count
- Delay rate percentage
- Average, median, and maximum delay days
- Geographic breakdown by state
- On-time delivery rate
- Performance trends

---

### 2. Revenue & Financial Analysis

#### Basic Queries
```
Show revenue analysis
What are the revenue trends?
Analyze sales performance
What's the total revenue?
```

#### Advanced Queries
```
What is the monthly revenue growth rate?
Which month had the highest revenue?
Compare revenue across different states
What's the average order value?
Show revenue trends over the past year
Which regions generate the most revenue?
```

#### Expected Insights
- Total revenue
- Average order value
- Monthly revenue trends
- Growth rate analysis
- Revenue by geographic region
- Highest/lowest revenue periods

---

### 3. Product Performance

#### Basic Queries
```
Analyze product performance
Show product statistics
What are the top selling products?
```

#### Advanced Queries
```
Which product categories sell the most?
What's the average product price?
Show sales by product category
Which products have the highest revenue?
How many unique products do we have?
Compare performance across product categories
```

#### Expected Insights
- Total unique products
- Total items sold
- Average product price
- Top-selling products
- Category performance
- Revenue by category

---

### 4. Customer Behavior

#### Basic Queries
```
Analyze customer behavior
Show customer statistics
What's the repeat customer rate?
```

#### Advanced Queries
```
How many active customers do we have?
What's the average customer lifetime value?
Which customers spend the most?
What's the average orders per customer?
Compare customer distribution by state
How many customers make repeat purchases?
```

#### Expected Insights
- Total and active customers
- Average orders per customer
- Repeat customer rate
- Customer lifetime value
- Customer distribution by region
- Top spending customers

---

### 5. Demand Forecasting

#### Basic Queries
```
Forecast demand for next 30 days
What are the demand trends?
Predict future orders
```

#### Advanced Queries
```
What is the forecasted demand for next month?
Show demand trends and predictions
Is demand increasing or decreasing?
What's the historical average demand?
How accurate is the forecast model?
```

#### Expected Insights
- 30-day demand forecast
- Historical average demand
- Trend direction (increasing/decreasing)
- Model accuracy metrics (MAPE, R²)
- Future demand predictions

---

### 6. Comprehensive Reports

#### Basic Queries
```
Generate comprehensive report
Give me a complete overview
Show all key metrics
Provide a full analysis
```

#### Advanced Queries
```
What are the most important insights about our supply chain?
Generate a complete performance report
Show me all key performance indicators
What's the overall health of our supply chain?
Provide executive summary of operations
```

#### Expected Insights
- Delivery performance summary
- Revenue and financial metrics
- Product performance overview
- Customer behavior insights
- Key trends and patterns
- Recommendations

---

## Natural Language Queries (Enhanced Mode)

When using the enhanced AI mode, you can ask questions in natural language:

### Conversational Examples
```
How is our supply chain performing overall?
What should I be worried about in our delivery operations?
Can you explain why some states have higher delays?
What trends do you see in customer behavior?
Is our revenue growing or declining?
Which areas need immediate attention?
What's working well and what needs improvement?
Compare our performance this month vs last month
What insights can you provide from the data?
Help me understand our product sales patterns
```

### Comparative Queries
```
Compare delivery performance between North and South regions
Which has better performance: revenue or delivery?
Show me the difference in customer behavior across states
Compare product categories by revenue
What's the relationship between delays and customer satisfaction?
```

### Analytical Queries
```
What factors contribute to delivery delays?
Why is the repeat customer rate low/high?
What drives revenue in our top performing states?
Identify bottlenecks in our supply chain
What patterns do you see in order timing?
```

---

## Query Tips for Best Results

### 1. Be Specific
❌ "Show data"
✅ "Show delivery delay rate by state"

### 2. Ask for Comparisons
❌ "Revenue?"
✅ "Compare revenue between Q1 and Q2"

### 3. Request Insights
❌ "What's the number?"
✅ "What do the delay trends tell us about our operations?"

### 4. Use Context
❌ "How many?"
✅ "How many orders were delayed in the last month?"

### 5. Ask Follow-ups
```
User: "What's the delivery delay rate?"
Bot: [Provides 12.5% delay rate]
User: "Which states contribute most to this?"
Bot: [Provides state breakdown]
User: "What can we do to improve in those states?"
Bot: [Provides recommendations]
```

---

## Sample Conversation Flow

### Example 1: Investigating Delays
```
User: "What is our delivery performance?"
Bot: [Shows overall delay rate of 12.5%]

User: "Which states have the worst delays?"
Bot: [Shows top 5 states with highest delays]

User: "What's the average delay in those states?"
Bot: [Provides detailed delay analysis]

User: "How does this compare to on-time states?"
Bot: [Provides comparative analysis]
```

### Example 2: Revenue Analysis
```
User: "Show me our revenue trends"
Bot: [Displays revenue metrics and growth]

User: "Which month had the highest revenue?"
Bot: [Identifies peak month]

User: "What drove revenue in that month?"
Bot: [Analyzes factors contributing to peak]

User: "Can we forecast next month's revenue?"
Bot: [Provides forecast based on trends]
```

---

## Advanced Features

### With RAG Enabled (`--rag`)
RAG provides semantic search over your supply chain data:

```
Find all orders with significant delays
Show me products in the electronics category
What do we know about customer ABC123?
Find similar orders to order ID XYZ789
```

### With Enhanced AI
The LLM understands context and provides:
- Natural language responses
- Multi-step reasoning
- Contextual recommendations
- Explanations of patterns

---

## Troubleshooting Common Queries

### Query: "No data available"
**Solution**:
- Ensure data is loaded with `--data train`
- Check that CSV files exist in `data/train/`

### Query: "Analytics not initialized"
**Solution**:
- Verify data loading was successful
- Check for error messages in console

### Query: LLM not responding
**Solution**:
- Set `GROQ_API_KEY` environment variable
- Check internet connection
- Use `--legacy` mode as fallback

### Query: RAG search not working
**Solution**:
- Install dependencies: `pip install faiss-cpu sentence-transformers`
- Ensure sufficient memory for vector database

---

## Performance Tips

1. **Use Specific Queries**: More specific queries get faster, more accurate responses
2. **Start Simple**: Begin with basic queries before complex analysis
3. **Enable RAG Selectively**: RAG provides better semantic search but requires more resources
4. **Use Legacy Mode**: For fast, deterministic responses without LLM overhead

---

## API Key Setup

To use enhanced AI features:

### Windows
```cmd
set GROQ_API_KEY=your_api_key_here
python main.py
```

### Linux/Mac
```bash
export GROQ_API_KEY=your_api_key_here
python main.py
```

Get a free API key from: https://console.groq.com/

---

## Example Results

### Delivery Analysis
```
📊 Delivery Performance Analysis:
- Total Orders: 95,329
- Delayed Orders: 11,921
- Delay Rate: 12.51%
- On-Time Rate: 87.49%
- Average Delay: 8.3 days
- Maximum Delay: 187 days
- Median Delay: 5.0 days
```

### Revenue Analysis
```
💰 Revenue Analysis:
- Total Revenue: $15,432,890.45
- Average Order Value: $161.89
- Monthly Growth Rate: 3.45%
- Highest Revenue Month: 2018-11
- Lowest Revenue Month: 2016-09
```

### Comprehensive Report
```
📋 Comprehensive Supply Chain Report

## Delivery Performance
- Delay Rate: 12.51%
- Average Delay: 8.3 days

## Revenue Metrics
- Total Revenue: $15,432,890.45
- Average Order Value: $161.89
- Growth Rate: 3.45%

## Product Performance
- Unique Products: 32,951
- Total Items Sold: 112,650

## Customer Insights
- Active Customers: 96,096
- Repeat Rate: 2.9%
- Avg CLV: $160.63
```

---

## Contributing

Have suggestions for better prompts? Submit them in the issues!

## Support

For issues or questions:
- Check console logs for error messages
- Verify data files are in correct location
- Ensure all dependencies are installed
- Try `--legacy` mode if enhanced mode fails
