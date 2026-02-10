# extract_features_optimized.py - Feature Extraction Utility

## Purpose
Optimized utility for extracting features from supply chain data for analytics and machine learning. Processes large datasets efficiently with parallel processing and caching.

## Key Components

### Class: FeatureExtractor
Handles feature extraction from SCM data.

**Initialization Parameters:**
- `data_wrapper`: Database wrapper
- `use_cache` (bool): Enable feature caching
- `n_jobs` (int): Number of parallel jobs

## Core Methods

### `extract_delivery_features(order_data)`
Extracts delivery-related features.

**Parameters:**
- `order_data` (DataFrame): Order records

**Extracted Features:**
- `days_to_delivery`: Time from order to delivery
- `is_delayed`: Boolean delay flag
- `delay_severity`: Critical/Major/Minor classification
- `on_time_flag`: On-time delivery indicator
- `delivery_day_of_week`: Weekday analysis
- `delivery_month`: Seasonal patterns

**Returns:** DataFrame with features

### `extract_revenue_features(sales_data)`
Extracts revenue and sales features.

**Parameters:**
- `sales_data` (DataFrame): Sales records

**Extracted Features:**
- `order_value`: Total order amount
- `product_category`: Product classification
- `revenue_by_state`: Geographic revenue
- `customer_lifetime_value`: CLV calculation
- `purchase_frequency`: Repeat purchase rate

**Returns:** DataFrame with features

### `extract_temporal_features(datetime_column)`
Extracts time-based features.

**Parameters:**
- `datetime_column` (Series): Datetime values

**Extracted Features:**
- `year`, `month`, `day`
- `day_of_week`, `week_of_year`
- `quarter`, `is_weekend`
- `is_month_end`, `is_quarter_end`

**Returns:** DataFrame with temporal features

### `extract_geographic_features(location_data)`
Extracts location-based features.

**Parameters:**
- `location_data` (DataFrame): Location records

**Extracted Features:**
- `state_code`: Standardized state codes
- `region`: Geographic region (West, East, etc.)
- `urban_rural`: Urban/rural classification
- `distance_from_warehouse`: Shipping distance

**Returns:** DataFrame with geographic features

### `extract_product_features(product_data)`
Extracts product-related features.

**Parameters:**
- `product_data` (DataFrame): Product records

**Extracted Features:**
- `product_category`: Category classification
- `price_tier`: Low/Medium/High price tier
- `stock_level`: Inventory level
- `product_age`: Days since first sale
- `popularity_score`: Sales rank

**Returns:** DataFrame with product features

## Optimization Features

### Parallel Processing
```python
extractor = FeatureExtractor(data_wrapper, n_jobs=4)
# Uses 4 CPU cores for parallel feature extraction
```

### Caching
```python
extractor = FeatureExtractor(data_wrapper, use_cache=True)
# Caches extracted features for repeated queries
```

### Batch Processing
```python
# Process large datasets in batches
for batch in data_batches:
    features = extractor.extract_delivery_features(batch)
    # Process batch
```

## Helper Methods

### `_calculate_delay_severity(days_delayed)`
Classifies delay severity.

**Parameters:**
- `days_delayed` (int): Days past due date

**Returns:** str ('Critical', 'Major', 'Minor', 'On-Time')

### `_normalize_state_code(state_name)`
Standardizes state names to codes.

**Parameters:**
- `state_name` (str): State name or code

**Returns:** str (2-letter state code)

### `_calculate_clv(customer_orders)`
Calculates customer lifetime value.

**Parameters:**
- `customer_orders` (DataFrame): Customer order history

**Returns:** float (CLV estimate)

## Usage Examples

### Extract Delivery Features
```python
from extract_features_optimized import FeatureExtractor

extractor = FeatureExtractor(data_wrapper, use_cache=True)

# Get order data
orders = data_wrapper.get_orders()

# Extract features
delivery_features = extractor.extract_delivery_features(orders)
print(delivery_features.head())
```

### Extract All Features
```python
# Extract multiple feature sets
delivery_features = extractor.extract_delivery_features(orders)
revenue_features = extractor.extract_revenue_features(sales)
temporal_features = extractor.extract_temporal_features(orders['order_date'])
geographic_features = extractor.extract_geographic_features(orders)

# Combine features
all_features = pd.concat([
    delivery_features,
    revenue_features,
    temporal_features,
    geographic_features
], axis=1)
```

### Batch Processing
```python
# Process large dataset in batches
batch_size = 10000
all_features = []

for i in range(0, len(orders), batch_size):
    batch = orders.iloc[i:i+batch_size]
    features = extractor.extract_delivery_features(batch)
    all_features.append(features)

# Combine batches
final_features = pd.concat(all_features)
```

## Performance Characteristics

### Single-threaded
- **10K records**: ~2-5 seconds
- **100K records**: ~20-40 seconds
- **1M records**: ~3-5 minutes

### Multi-threaded (4 cores)
- **10K records**: ~1-2 seconds
- **100K records**: ~8-15 seconds
- **1M records**: ~1-2 minutes

### With Caching
- **First run**: Normal time
- **Subsequent runs**: ~90% faster (cache hit)

## Feature Store Integration

### Save Features
```python
# Extract features
features = extractor.extract_delivery_features(orders)

# Save to feature store
features.to_parquet('feature_store/delivery_features.parquet')
```

### Load Cached Features
```python
# Load from feature store
cached_features = pd.read_parquet('feature_store/delivery_features.parquet')
```

## Dependencies

### Required Libraries
```python
import pandas as pd
import numpy as np
from multiprocessing import Pool
import joblib  # For caching
```

### Internal Modules
- `data_wrapper`: Database access

## Error Handling

### Missing Data
- Fills with appropriate defaults
- Logs warnings for missing critical fields
- Continues processing valid records

### Invalid Values
- Validates data types
- Handles outliers
- Clips extreme values

### Processing Errors
- Logs errors with record IDs
- Skips problematic records
- Returns partial results

## Use Cases

1. **Analytics Dashboard**: Feature extraction for reporting
2. **Machine Learning**: Training data preparation
3. **Data Export**: Feature-rich data exports
4. **Performance Analysis**: KPI calculation

## Best Practices

1. **Use caching** for repeated extractions
2. **Enable parallel processing** for large datasets
3. **Batch process** very large datasets (>1M records)
4. **Validate features** after extraction
5. **Monitor memory** with large datasets

## Integration Points

### Used By
- Analytics engine
- ML model training scripts
- Data export utilities

### Uses
- `data_wrapper`: Database queries
- pandas: Data manipulation
