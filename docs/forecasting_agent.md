# agents/forecasting_agent.py - Demand Forecasting Agent

## Purpose
Specialized agent for demand forecasting, trend analysis, and future predictions. Uses statistical models and historical data for forecasting.

## Key Components

### Class: ForecastingAgent
Handles demand forecasting and prediction queries.

**Initialization Parameters:**
- `analytics_engine`: SCMAnalytics instance
- `data_wrapper`: Database wrapper
- `rag_module`: RAGModule instance (optional)

## Core Methods

### `query(user_query, classification=None)`
Processes forecasting queries with classification support.

**Parameters:**
- `user_query` (str): User's question
- `classification` (dict): Intent classification (optional)

**Returns:** dict with forecast response

**Query Types:**

1. **Demand Forecasts** (DATA):
   - "Forecast next month demand"
   - "Predict product demand"
   - "Future sales projection"

2. **Trend Analysis** (DATA):
   - "Show demand trends"
   - "What are the trends?"
   - "Analyze demand patterns"

3. **Policy Questions** (POLICY - rare):
   - "What is the forecasting methodology?"
   - "Explain forecast confidence intervals"

## Supported Forecasts

### Product Demand Forecast
- "Forecast product demand"
- "Predict next month sales"
- "Demand projection"

**Response:**
```
Product Demand Forecast (Next 30 Days):

| Product | Current Demand | Forecasted | Change |
|---------|----------------|------------|--------|
| Product A | 1,250 units | 1,420 units | +13.6% |
| Product B | 980 units | 1,050 units | +7.1% |
| Product C | 750 units | 820 units | +9.3% |

Forecast Confidence: 85%
```

### Trend Analysis
- "Show demand trends"
- "Analyze demand patterns"
- "What are the trends?"

**Response:**
```
Demand Trend Analysis:

Overall Trend: ↗️ Increasing (+8.5% month-over-month)

Key Insights:
• Product A: Strong upward trend (+15%)
• Product B: Stable with slight growth (+3%)
• Product C: Declining trend (-5%)

Seasonality Detected: Yes (Peak in Q4)
```

### Future Projections
- "Predict next quarter demand"
- "3-month forecast"
- "Long-term demand projection"

**Response:**
```
90-Day Demand Forecast:

Month 1: 12,450 units (±850 units)
Month 2: 13,120 units (±920 units)
Month 3: 13,780 units (±1,010 units)

Total Projected Demand: 39,350 units
Confidence Level: 78%
```

## Forecasting Methods

### Time Series Analysis
- Historical data analysis
- Trend identification
- Seasonality detection

### Statistical Models
- Moving averages
- Exponential smoothing
- Linear regression

### Confidence Intervals
- Upper/lower bounds
- Prediction uncertainty
- Accuracy metrics

## Helper Methods

### `_generate_demand_forecast(horizon_days=30)`
Generates demand forecast for specified horizon.

**Parameters:**
- `horizon_days` (int): Forecast period in days

**Returns:** dict with forecast data

### `_analyze_trends()`
Analyzes historical trends.

**Returns:** dict with trend analysis

### `_calculate_confidence(forecast_data)`
Calculates forecast confidence level.

**Parameters:**
- `forecast_data` (dict): Forecast results

**Returns:** float (0-1 confidence score)

### `_format_forecast_display(forecast)`
Formats forecast for display.

**Parameters:**
- `forecast` (dict): Raw forecast data

**Returns:** str (formatted forecast)

## Integration with Classification

### Data Query (Common)
```python
Query: "Forecast next month demand"
Classification: DATA
→ Statistical model forecasting
→ Time: ~5-7s
→ Response: Forecast with confidence
```

### Policy Query (Rare)
```python
Query: "What is the forecasting methodology?"
Classification: POLICY
→ RAG retrieval
→ Time: ~15s
→ Response: Methodology documentation
```

## Performance Characteristics

### Simple Forecast
- **Time**: 5-7 seconds
- **Computation**: Statistical models
- **Data**: Historical database records

### Complex Forecast
- **Time**: 8-12 seconds
- **Computation**: Multi-product, long horizon
- **Data**: Extensive historical analysis

### With Policy Context
- **Time**: 18-20 seconds
- **Sources**: RAG + Forecasting models
- **Use Case**: Methodology explanations

## Response Examples

### Demand Forecast
```
30-Day Demand Forecast:

Total Forecasted Demand: 15,670 units
Current Run Rate: 14,250 units/month
Expected Growth: +10.0%

Confidence Level: 82%

────────────────────────────────────────────────────────────
🤖 Agent: Forecasting Agent | ✅ Success
📁 Sources: Database (Historical Data)
⏱️ Time: 6.45s
────────────────────────────────────────────────────────────
```

### Trend Analysis
```
Demand Trend Analysis:

📈 Overall Trend: Increasing (+8.5% MoM)

Product Insights:
• Product A: ↗️ Strong growth (+15.2%)
• Product B: → Stable (+2.8%)
• Product C: ↘️ Declining (-4.5%)

Seasonality: Detected (Q4 peak)
Recommendation: Increase inventory for Product A

────────────────────────────────────────────────────────────
🤖 Agent: Forecasting Agent | ✅ Success
📁 Sources: Database
⏱️ Time: 7.21s
────────────────────────────────────────────────────────────
```

## Forecast Accuracy

### Validation Methods
- Backtesting on historical data
- Mean Absolute Percentage Error (MAPE)
- Confidence interval validation

### Typical Accuracy
- **Short-term** (7-30 days): 85-90%
- **Medium-term** (30-90 days): 75-85%
- **Long-term** (90+ days): 65-75%

## Dependencies

### Internal Modules
- `analytics_engine`: Historical data
- `data_wrapper`: Database access
- `rag`: Methodology docs (optional)
- `ui_formatter`: Response formatting

### External Libraries (if used)
- `numpy`: Statistical calculations
- `pandas`: Time series analysis
- `statsmodels`: Forecasting models

## Error Handling

### Insufficient Data
- Returns message about minimum data requirements
- Suggests data collection period

### Model Convergence Issues
- Falls back to simpler model
- Logs warning with details

### Extreme Predictions
- Caps forecasts at reasonable bounds
- Flags outliers for review

## Usage Examples

### Quick Forecast
```python
agent = ForecastingAgent(analytics, data)
result = agent.query("forecast demand", classification={'query_type': 'data'})
# Returns 30-day forecast
```

### Trend Analysis
```python
result = agent.query("show trends", classification={'query_type': 'data'})
# Returns trend insights
```

### Long-term Projection
```python
result = agent.query("3-month forecast")
# Returns quarterly projection
```

## Integration Points

### Used By
- `agents/orchestrator.py`: Routes forecasting queries

### Uses
- `analytics_engine.get_historical_data()`: Time series
- `ui_formatter`: Response formatting
