"""
Optimized Feature Extraction from CSV Datasets
Uses vectorized pandas operations for fast processing
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sys

# Add modules to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.feature_store import FeatureStore, MLFeatures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OptimizedFeatureExtractor:
    """Optimized feature extraction using vectorized operations"""

    def __init__(self, data_path: str = "data/train"):
        self.data_path = Path(data_path)
        self.feature_store = FeatureStore(use_redis=False)
        self.ml_features = MLFeatures(self.feature_store)

        # Load datasets
        logger.info("Loading datasets...")
        self.customers = pd.read_csv(self.data_path / "df_Customers.csv")
        self.products = pd.read_csv(self.data_path / "df_Products.csv")
        self.orders = pd.read_csv(self.data_path / "df_Orders.csv")
        self.order_items = pd.read_csv(self.data_path / "df_OrderItems.csv")
        self.payments = pd.read_csv(self.data_path / "df_Payments.csv")

        logger.info(f"✅ Loaded {len(self.customers)} customers")
        logger.info(f"✅ Loaded {len(self.products)} products")
        logger.info(f"✅ Loaded {len(self.orders)} orders")
        logger.info(f"✅ Loaded {len(self.order_items)} order items")
        logger.info(f"✅ Loaded {len(self.payments)} payments")

    def extract_customer_features_vectorized(self):
        """Extract customer features using vectorized operations"""
        logger.info("\n📊 Extracting customer features (vectorized)...")

        # Merge payments with orders to get customer-order-value relationship
        order_values = self.payments.groupby('order_id')['payment_value'].sum().reset_index()
        order_values.columns = ['order_id', 'order_total']

        orders_with_value = self.orders.merge(order_values, on='order_id', how='left')

        # Calculate customer aggregates
        customer_stats = orders_with_value.groupby('customer_id').agg({
            'order_id': 'count',  # Total orders
            'order_total': ['sum', 'mean']  # Total spend and avg order value
        }).reset_index()

        customer_stats.columns = ['customer_id', 'total_orders', 'total_spend', 'avg_order_value']

        # Add customer location info
        customer_stats = customer_stats.merge(
            self.customers[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id',
            how='left'
        )

        # Calculate recency (days since last order)
        orders_with_dates = self.orders.copy()
        orders_with_dates['order_purchase_timestamp'] = pd.to_datetime(
            orders_with_dates['order_purchase_timestamp']
        )

        last_order_dates = orders_with_dates.groupby('customer_id')['order_purchase_timestamp'].max().reset_index()
        last_order_dates.columns = ['customer_id', 'last_order_date']
        last_order_dates['days_since_last_order'] = (
            datetime.now() - last_order_dates['last_order_date']
        ).dt.days

        customer_stats = customer_stats.merge(
            last_order_dates[['customer_id', 'days_since_last_order']],
            on='customer_id',
            how='left'
        )

        # Determine customer segment based on spend
        customer_stats['segment'] = pd.cut(
            customer_stats['total_spend'],
            bins=[0, 500, 1000, float('inf')],
            labels=['low_value', 'medium_value', 'high_value']
        )

        # Get favorite product category per customer
        order_products = self.order_items.merge(
            self.products[['product_id', 'product_category_name']],
            on='product_id',
            how='left'
        )

        order_products = order_products.merge(
            self.orders[['order_id', 'customer_id']],
            on='order_id',
            how='left'
        )

        # Get most common category per customer
        customer_categories = order_products.groupby(['customer_id', 'product_category_name']).size().reset_index(name='count')
        customer_top_category = customer_categories.loc[customer_categories.groupby('customer_id')['count'].idxmax()]
        customer_top_category = customer_top_category[['customer_id', 'product_category_name']]
        customer_top_category.columns = ['customer_id', 'favorite_category']

        customer_stats = customer_stats.merge(
            customer_top_category,
            on='customer_id',
            how='left'
        )

        # Store in feature store (batch)
        logger.info(f"Storing {len(customer_stats)} customer features...")
        success_count = 0

        for _, row in customer_stats.iterrows():
            customer_id = row['customer_id']
            features = {
                'customer_id': customer_id,
                'total_orders': int(row['total_orders']),
                'total_spend': float(row['total_spend']) if pd.notna(row['total_spend']) else 0.0,
                'avg_order_value': float(row['avg_order_value']) if pd.notna(row['avg_order_value']) else 0.0,
                'customer_state': row['customer_state'] if pd.notna(row['customer_state']) else 'unknown',
                'customer_city': row['customer_city'] if pd.notna(row['customer_city']) else 'unknown',
                'favorite_category': row['favorite_category'] if pd.notna(row['favorite_category']) else 'unknown',
                'days_since_last_order': int(row['days_since_last_order']) if pd.notna(row['days_since_last_order']) else None,
                'segment': str(row['segment']) if pd.notna(row['segment']) else 'low_value',
                'extraction_date': datetime.now().isoformat()
            }

            if self.feature_store.set('customer', customer_id, features, ttl=86400):
                success_count += 1

            # Also cache segment
            self.ml_features.cache_customer_segment(customer_id, features['segment'])

            # Progress indicator
            if success_count % 10000 == 0:
                logger.info(f"  Processed {success_count} customers...")

        logger.info(f"✅ Extracted and stored {success_count} customer features")
        return success_count

    def extract_product_features_vectorized(self):
        """Extract product features using vectorized operations"""
        logger.info("\n📦 Extracting product features (vectorized)...")

        # Calculate product volume and weight-to-volume ratio
        products_enriched = self.products.copy()
        products_enriched['volume_cm3'] = (
            products_enriched['product_length_cm'] *
            products_enriched['product_width_cm'] *
            products_enriched['product_height_cm']
        )

        products_enriched['weight_to_volume_ratio'] = (
            products_enriched['product_weight_g'] / products_enriched['volume_cm3']
        ).replace([np.inf, -np.inf], 0)

        # Calculate sales metrics
        product_sales = self.order_items.groupby('product_id').agg({
            'price': ['mean', 'sum', 'count'],
            'shipping_charges': 'mean'
        }).reset_index()

        product_sales.columns = ['product_id', 'avg_price', 'total_revenue', 'units_sold', 'avg_shipping']

        # Merge with products
        products_enriched = products_enriched.merge(product_sales, on='product_id', how='left')

        # Category ranking
        category_sales = self.order_items.merge(
            self.products[['product_id', 'product_category_name']],
            on='product_id'
        ).groupby('product_category_name').size().reset_index(name='category_orders')

        category_sales['category_rank'] = category_sales['category_orders'].rank(ascending=False)
        category_rank_dict = dict(zip(
            category_sales['product_category_name'],
            category_sales['category_rank']
        ))

        products_enriched['category_rank'] = products_enriched['product_category_name'].map(category_rank_dict)

        # Store in feature store
        logger.info(f"Storing {len(products_enriched)} product features...")
        success_count = 0

        for _, row in products_enriched.iterrows():
            product_id = row['product_id']
            features = {
                'product_id': product_id,
                'category': row['product_category_name'] if pd.notna(row['product_category_name']) else 'unknown',
                'weight_g': float(row['product_weight_g']) if pd.notna(row['product_weight_g']) else 0.0,
                'volume_cm3': float(row['volume_cm3']) if pd.notna(row['volume_cm3']) else 0.0,
                'weight_to_volume_ratio': float(row['weight_to_volume_ratio']) if pd.notna(row['weight_to_volume_ratio']) else 0.0,
                'avg_price': float(row['avg_price']) if pd.notna(row['avg_price']) else 0.0,
                'total_revenue': float(row['total_revenue']) if pd.notna(row['total_revenue']) else 0.0,
                'units_sold': int(row['units_sold']) if pd.notna(row['units_sold']) else 0,
                'avg_shipping': float(row['avg_shipping']) if pd.notna(row['avg_shipping']) else 0.0,
                'category_rank': int(row['category_rank']) if pd.notna(row['category_rank']) else 999,
                'extraction_date': datetime.now().isoformat()
            }

            if self.feature_store.set('product', product_id, features, ttl=604800):
                success_count += 1

            # Cache category
            category_info = {
                'category': features['category'],
                'category_rank': features['category_rank']
            }
            self.ml_features.cache_product_category(product_id, category_info)

            # Progress indicator
            if success_count % 10000 == 0:
                logger.info(f"  Processed {success_count} products...")

        logger.info(f"✅ Extracted and stored {success_count} product features")
        return success_count

    def extract_order_features_vectorized(self):
        """Extract order features using vectorized operations"""
        logger.info("\n📋 Extracting order features (vectorized)...")

        # Aggregate payment info per order
        order_payments = self.payments.groupby('order_id').agg({
            'payment_value': 'sum',
            'payment_type': 'first',
            'payment_installments': 'max'
        }).reset_index()

        order_payments.columns = ['order_id', 'order_total', 'payment_type', 'installments']

        # Count items per order
        order_item_counts = self.order_items.groupby('order_id').size().reset_index(name='item_count')

        # Merge all
        orders_enriched = self.orders.merge(order_payments, on='order_id', how='left')
        orders_enriched = orders_enriched.merge(order_item_counts, on='order_id', how='left')

        # Convert timestamps
        orders_enriched['order_purchase_timestamp'] = pd.to_datetime(orders_enriched['order_purchase_timestamp'])
        orders_enriched['order_delivered_timestamp'] = pd.to_datetime(orders_enriched['order_delivered_timestamp'])
        orders_enriched['order_estimated_delivery_date'] = pd.to_datetime(orders_enriched['order_estimated_delivery_date'])

        # Calculate delivery metrics
        orders_enriched['delivery_time_days'] = (
            orders_enriched['order_delivered_timestamp'] - orders_enriched['order_purchase_timestamp']
        ).dt.days

        orders_enriched['delivery_delay_days'] = (
            orders_enriched['order_delivered_timestamp'] - orders_enriched['order_estimated_delivery_date']
        ).dt.days

        orders_enriched['on_time_delivery'] = orders_enriched['delivery_delay_days'] <= 0

        # Store in feature store
        logger.info(f"Storing {len(orders_enriched)} order features...")
        success_count = 0

        for _, row in orders_enriched.iterrows():
            order_id = row['order_id']
            features = {
                'order_id': order_id,
                'customer_id': row['customer_id'],
                'order_status': row['order_status'],
                'order_total': float(row['order_total']) if pd.notna(row['order_total']) else 0.0,
                'item_count': int(row['item_count']) if pd.notna(row['item_count']) else 0,
                'payment_type': row['payment_type'] if pd.notna(row['payment_type']) else 'unknown',
                'installments': int(row['installments']) if pd.notna(row['installments']) else 0,
                'delivery_time_days': int(row['delivery_time_days']) if pd.notna(row['delivery_time_days']) else None,
                'delivery_delay_days': int(row['delivery_delay_days']) if pd.notna(row['delivery_delay_days']) else None,
                'on_time_delivery': bool(row['on_time_delivery']) if pd.notna(row['on_time_delivery']) else None,
                'extraction_date': datetime.now().isoformat()
            }

            if self.feature_store.set('order', order_id, features, ttl=3600):
                success_count += 1

            # Progress indicator
            if success_count % 10000 == 0:
                logger.info(f"  Processed {success_count} orders...")

        logger.info(f"✅ Extracted and stored {success_count} order features")
        return success_count

    def extract_aggregate_features(self):
        """Extract aggregate analytics features"""
        logger.info("\n📈 Extracting aggregate features...")

        # Top selling products
        top_products = self.order_items.groupby('product_id').size().nlargest(10).to_dict()
        self.feature_store.set('analytics', 'top_selling_products', top_products, ttl=3600)

        # Top revenue products
        top_revenue = self.order_items.groupby('product_id')['price'].sum().nlargest(10).to_dict()
        self.feature_store.set('analytics', 'top_revenue_products', top_revenue, ttl=3600)

        # Category performance
        category_perf = self.order_items.merge(
            self.products[['product_id', 'product_category_name']],
            on='product_id'
        ).groupby('product_category_name').agg({
            'price': ['sum', 'mean', 'count']
        }).reset_index()

        category_perf.columns = ['category', 'total_revenue', 'avg_price', 'order_count']
        category_dict = category_perf.to_dict('records')
        self.feature_store.set('analytics', 'category_performance', category_dict, ttl=3600)

        # Payment distribution
        payment_dist = self.payments['payment_type'].value_counts().to_dict()
        self.feature_store.set('analytics', 'payment_distribution', payment_dist, ttl=3600)

        # Order status distribution
        status_dist = self.orders['order_status'].value_counts().to_dict()
        self.feature_store.set('analytics', 'order_status_distribution', status_dist, ttl=3600)

        # Delivery performance
        orders_delivery = self.orders.copy()
        orders_delivery['order_delivered_timestamp'] = pd.to_datetime(orders_delivery['order_delivered_timestamp'])
        orders_delivery['order_estimated_delivery_date'] = pd.to_datetime(orders_delivery['order_estimated_delivery_date'])

        delivered = orders_delivery[
            orders_delivery['order_delivered_timestamp'].notna() &
            orders_delivery['order_estimated_delivery_date'].notna()
        ].copy()

        delivered['delay_days'] = (
            delivered['order_delivered_timestamp'] - delivered['order_estimated_delivery_date']
        ).dt.days

        on_time_rate = (delivered['delay_days'] <= 0).mean() * 100
        avg_delay = delivered[delivered['delay_days'] > 0]['delay_days'].mean()

        delivery_metrics = {
            'on_time_rate_percent': float(on_time_rate),
            'avg_delay_days': float(avg_delay) if pd.notna(avg_delay) else 0.0,
            'total_delivered_orders': len(delivered)
        }
        self.feature_store.set('analytics', 'delivery_performance', delivery_metrics, ttl=3600)

        logger.info(f"✅ Stored aggregate features:")
        logger.info(f"  • Top products: {len(top_products)}")
        logger.info(f"  • Category performance: {len(category_dict)} categories")
        logger.info(f"  • On-time rate: {on_time_rate:.1f}%")

        return 5  # Number of aggregate feature types

    def run_extraction(self):
        """Run optimized feature extraction pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Optimized Feature Extraction Pipeline")
        logger.info("=" * 60)

        # Extract all features
        customer_count = self.extract_customer_features_vectorized()
        product_count = self.extract_product_features_vectorized()
        order_count = self.extract_order_features_vectorized()
        aggregate_count = self.extract_aggregate_features()

        # Get final statistics
        stats = self.feature_store.get_stats()

        logger.info("\n" + "=" * 60)
        logger.info("✅ Feature Extraction Complete!")
        logger.info("=" * 60)
        logger.info(f"Feature Store Statistics:")
        logger.info(f"  • Backend: {stats['backend']}")
        logger.info(f"  • Total Features: {stats['total_features']}")
        logger.info(f"  • Storage Size: {stats.get('storage_size_mb', 0):.2f} MB")
        logger.info(f"  • Customer Features: {customer_count}")
        logger.info(f"  • Product Features: {product_count}")
        logger.info(f"  • Order Features: {order_count}")
        logger.info(f"  • Aggregate Features: {aggregate_count} types")
        logger.info("=" * 60)

        return {
            'customer_features': customer_count,
            'product_features': product_count,
            'order_features': order_count,
            'total_features': stats['total_features']
        }


def main():
    """Main execution"""
    try:
        extractor = OptimizedFeatureExtractor()
        results = extractor.run_extraction()

        print("\n✅ Feature extraction successful!")
        print(f"Total features stored: {results['total_features']}")

    except Exception as e:
        logger.error(f"❌ Feature extraction failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
