# Product-Level Forecast and Delay Analysis

## Overview

The SCM Chatbot now supports **product-level** and **category-level** analysis for both delivery delays and demand forecasting. This enhancement allows users to get granular insights into how individual products or product categories perform.

---

## 🚀 New Features

### 1. **Product-Level Delay Analysis**

Analyze delivery delays at the product or category level to identify which products have the highest delay rates.

**Capabilities:**
- Analyze delays for specific products
- Analyze delays by product category
- Identify top delayed products and categories
- Compare product delay rates against overall metrics

### 2. **Product-Level Demand Forecasting**

Generate demand forecasts for individual products to improve inventory planning and procurement.

**Capabilities:**
- Forecast demand for specific products (30/60/90 days)
- Analyze product-specific demand trends
- Get product-level forecast accuracy metrics
- Receive actionable insights for inventory management

---

## 📊 How to Use

### Product Delay Analysis

#### Example Queries:

```
"Show me delivery delays for product XYZ"
"Which products have the highest delay rates?"
"What is the delay rate for electronics category?"
"Analyze delays by product category"
"Show me the top 10 products with worst delivery performance"
```

#### What You'll Get:

```
Product-Level Delay Analysis (Product ABC123):

📊 Overall Statistics:
- Total Orders: 1,234
- Delayed Orders: 156
- Delay Rate: 12.64%
- On-Time Rate: 87.36%
- Average Delay: 3.2 days
- Max Delay: 15.0 days

🔴 Top 5 Delayed Products:
1. Product XYZ: 15.3% delay rate (45/294 orders)
2. Product ABC: 12.8% delay rate (32/250 orders)
...

📦 Top 5 Delayed Categories:
1. Electronics: 14.2% delay rate (234/1,648 orders)
2. Furniture: 11.5% delay rate (156/1,357 orders)
...
```

### Product Demand Forecasting

#### Example Queries:

```
"Forecast demand for product ABC123 for 30 days"
"What will be the demand for product XYZ next quarter?"
"Predict sales for product 12345"
"Show me 60-day forecast for product SKU-999"
```

#### What You'll Get:

```
Product Demand Forecast:

📦 Product: ABC123
📅 Forecast Period: 30 days

📊 Historical Performance:
- Historical Average: 45.3 units/day
- Trend: Increasing

📈 Forecast Quality:
- Model Accuracy (MAPE): 12.45%
- R² Score: 0.876
- RMSE: 5.32

💡 Insights:
- Demand is growing. Consider increasing inventory levels.
- High forecast accuracy. Reliable for planning.
```

---

## 🛠️ Technical Implementation

### 1. Analytics Engine Enhancement

**New Method:** `analyze_product_delays()`

**File:** [tools/analytics.py](tools/analytics.py)

```python
def analyze_product_delays(
    self,
    product_id: Optional[str] = None,
    category: Optional[str] = None
) -> Dict:
    """
    Analyze delivery delays at product or category level

    Args:
        product_id: Specific product ID to analyze
        category: Product category to analyze

    Returns:
        Dictionary with delay statistics and top delayed products/categories
    """
```

**Features:**
- Merges orders with products and order items
- Filters by product_id or category
- Calculates delay metrics at product level
- Identifies top delayed products and categories
- Handles edge cases (no data, missing categories)

**Existing Method Enhanced:** `forecast_demand()`

Already supported `product_id` parameter for product-level forecasting.

### 2. Delay Agent Enhancement

**File:** [agents/delay_agent.py](agents/delay_agent.py)

**New Tool:** `GetProductDelays`

```python
Tool(
    name="GetProductDelays",
    func=self._get_product_delays,
    description="Get delivery delays at product or category level"
)
```

**New Method:** `_get_product_delays()`

- Parses query to extract product_id or category
- Calls analytics engine
- Formats results for user display
- Includes top delayed products/categories when applicable

**Updated Prompt:**
Enhanced system prompt to mention product-level delay analysis capabilities.

### 3. Forecasting Agent Enhancement

**File:** [agents/forecasting_agent.py](agents/forecasting_agent.py)

**New Tool:** `ForecastProductDemand`

```python
Tool(
    name="ForecastProductDemand",
    func=self._forecast_product_demand,
    description="Forecast demand for a specific product"
)
```

**New Method:** `_forecast_product_demand()`

- Parses query to extract product_id and periods
- Calls analytics engine with product_id
- Provides detailed forecast output
- Includes actionable insights based on trends and accuracy

**Updated Prompt:**
Enhanced to differentiate between overall and product-level forecasting.

---

## 📝 Usage Examples

### Multi-Agent Queries

The system can now handle compound queries involving product-level analysis:

```
"Show me delivery delays for electronics and forecast demand for the next 30 days"
```

This will:
1. Trigger Delay Agent → Product delay analysis for electronics
2. Trigger Forecasting Agent → Overall demand forecast
3. Combine results into comprehensive response

### Product-Specific Deep Dive

```
"Analyze product ABC123 - show delays and forecast"
```

This will:
1. Delay Agent → Specific product delay analysis
2. Forecasting Agent → Product-specific demand forecast
3. Provides complete picture for that product

---

## 🎯 Use Cases

### 1. **Inventory Optimization**

**Scenario:** A product has high demand but also high delays.

**Query:** "Show delays and forecast for product XYZ"

**Action:** Increase safety stock to compensate for delivery delays while meeting growing demand.

### 2. **Supplier Performance**

**Scenario:** Identify which product categories have worst delivery performance.

**Query:** "Which product categories have highest delay rates?"

**Action:** Investigate supplier issues for problematic categories.

### 3. **Procurement Planning**

**Scenario:** Plan purchases for high-demand products.

**Query:** "Forecast demand for product ABC for 90 days"

**Action:** Place procurement orders based on accurate product-level forecasts.

### 4. **Product Rationalization**

**Scenario:** Identify low-performing products.

**Query:** "Show me products with declining demand and high delays"

**Action:** Consider discontinuing or replacing problematic products.

---

## 🔧 API Format

### Internal Tool Call Format

**For Delay Analysis:**
```python
# Specific product
_get_product_delays("product_id:ABC123")

# Category
_get_product_delays("category:Electronics")

# All products (shows top delayed)
_get_product_delays("")
```

**For Demand Forecasting:**
```python
# Product with custom period
_forecast_product_demand("product_id:ABC123,periods:60")

# Product with default 30 days
_forecast_product_demand("product_id:ABC123,periods:30")
```

---

## 📊 Data Requirements

### For Product Delay Analysis

**Required Data:**
- Orders with delivery timestamps
- Order items linking orders to products
- Products table with product_id
- Delay calculations (is_delayed, delay_days)

**Optional Data:**
- Product categories (for category-level analysis)

### For Product Forecasting

**Required Data:**
- Order items with product_id and timestamps
- Historical sales data (minimum 30 days recommended)

**Quality Factors:**
- More historical data = better forecasts
- Products with regular sales patterns = more accurate
- Products with at least 20+ historical orders recommended

---

## 🚦 Limitations & Considerations

### Delay Analysis

1. **Minimum Sample Size:** Products need at least 5 orders for meaningful delay rate analysis
2. **Categories:** Category analysis only available if product_category_name exists in data
3. **Filtering:** Can analyze by product OR category, not both simultaneously

### Demand Forecasting

1. **Data Sparsity:** Products with irregular sales may have less accurate forecasts
2. **New Products:** Products with < 30 days history will have limited forecast reliability
3. **Model Accuracy:** Check MAPE and R² scores in output to assess forecast quality
4. **Trend Detection:** Linear regression may not capture complex seasonal patterns

---

## 🎓 Forecast Accuracy Interpretation

### MAPE (Mean Absolute Percentage Error)

- **< 15%:** Excellent accuracy - reliable for planning
- **15-30%:** Good accuracy - usable with caution
- **> 30%:** Poor accuracy - consider alternative methods or more data

### R² Score

- **> 0.8:** Strong model fit - high confidence
- **0.5-0.8:** Moderate fit - reasonable predictions
- **< 0.5:** Weak fit - low confidence, need better data

---

## 🔄 Future Enhancements

Potential improvements for product-level analysis:

1. **Advanced Forecasting Models**
   - ARIMA for seasonality
   - Prophet for multi-seasonality
   - LSTM neural networks for complex patterns

2. **Category-Level Forecasting**
   - Aggregate forecasts by category
   - Category trend analysis

3. **Multi-Product Analysis**
   - Compare multiple products side-by-side
   - Product portfolio optimization

4. **Root Cause Analysis**
   - Why specific products have delays
   - Link delays to carriers, regions, or vendors

5. **Real-Time Alerts**
   - Notify when product delays exceed threshold
   - Alert when forecast accuracy drops

---

## 📞 Support & Testing

### Testing the Features

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Select Agentic Mode** in the UI

3. **Try product-level queries:**
   ```
   "Show delays for product ABC123"
   "Forecast demand for product XYZ for 60 days"
   "Which product categories have highest delays?"
   "Show me product-level delay and forecast analysis"
   ```

4. **Check agent execution** in the response footer to see which agents ran

### Diagnostic Queries

Test the system with these queries:

```
# Overall vs Product-Level
"Compare overall delays with product ABC delays"

# Multi-Product
"Show me delays for top 5 products"

# Trend Analysis
"Forecast demand for growing products"

# Combined Analysis
"Show product XYZ delays, forecast, and recommendations"
```

---

## 📚 Related Documentation

- [Multi-Agent Architecture](docs/MULTI_INTENT_FIX.md)
- [RAG Integration](docs/RAG_AUTO_DETECTION.md)
- [Real-World Applications](docs/REAL_WORLD_APPLICATION.md)
- [Quick Reference](QUICK_REFERENCE.md)

---

**Version:** 2.3 (Product-Level Analysis)
**Last Updated:** January 30, 2026
**Status:** ✅ Production Ready

---

## Summary

Product-level forecast and delay analysis provides granular insights for:
- 📦 Individual product performance monitoring
- 📊 Category-level trend analysis
- 📈 Accurate demand forecasting per product
- 🔍 Identifying problem products and categories
- 💡 Data-driven inventory and procurement decisions

The multi-agent system automatically routes product-level queries to the appropriate specialized agents, combining analytics precision with natural language understanding for powerful supply chain insights.
