"""
Data Loader Module
Handles loading, preprocessing, and managing supply chain datasets
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SCMDataLoader:
    """Supply Chain Management Data Loader"""
    
    def __init__(self, dataset_paths: Dict[str, str]):
        """
        Initialize data loader
        
        Args:
            dataset_paths: Dictionary containing paths to all CSV files
        """
        self.dataset_paths = dataset_paths
        self.orders = None
        self.customers = None
        self.products = None
        self.order_items = None
        self.payments = None
        
    def load_all_data(self) -> Tuple:
        """Load all datasets and perform initial preprocessing"""
        logger.info("Loading all datasets...")
        
        try:
            # Load datasets
            self.orders = pd.read_csv(self.dataset_paths['orders'])
            self.customers = pd.read_csv(self.dataset_paths['customers'])
            self.products = pd.read_csv(self.dataset_paths['products'])
            self.order_items = pd.read_csv(self.dataset_paths['order_items'])
            self.payments = pd.read_csv(self.dataset_paths['payments'])
            
            # Preprocess
            self._preprocess_orders()
            self._preprocess_products()
            
            logger.info(f"Loaded: {len(self.orders)} orders, {len(self.customers)} customers, "
                       f"{len(self.products)} products, {len(self.order_items)} order items, "
                       f"{len(self.payments)} payments")
            
            return self.orders, self.customers, self.products, self.order_items, self.payments
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _preprocess_orders(self):
        """Preprocess orders data"""
        # Convert date columns
        date_columns = ['order_purchase_timestamp', 'order_approved_at', 
                       'order_delivered_timestamp', 'order_estimated_delivery_date']
        
        for col in date_columns:
            if col in self.orders.columns:
                self.orders[col] = pd.to_datetime(self.orders[col], errors='coerce')
        
        # Calculate delivery delay
        self.orders['delivery_delay_days'] = (
            self.orders['order_delivered_timestamp'] - 
            self.orders['order_estimated_delivery_date']
        ).dt.days
        
        # Flag delayed orders
        self.orders['is_delayed'] = self.orders['delivery_delay_days'] > 0
        
        # Calculate processing time
        self.orders['processing_time_hours'] = (
            self.orders['order_approved_at'] - 
            self.orders['order_purchase_timestamp']
        ).dt.total_seconds() / 3600
        
        # Fill missing values
        self.orders['delivery_delay_days'].fillna(0, inplace=True)
        self.orders['is_delayed'].fillna(False, inplace=True)
    
    def _preprocess_products(self):
        """Preprocess products data"""
        # Fill missing product dimensions with median
        dimension_cols = ['product_weight_g', 'product_length_cm', 
                         'product_height_cm', 'product_width_cm']
        
        for col in dimension_cols:
            if col in self.products.columns:
                median_val = self.products[col].median()
                self.products[col].fillna(median_val, inplace=True)
        
        # Calculate product volume
        self.products['product_volume_cm3'] = (
            self.products['product_length_cm'] * 
            self.products['product_height_cm'] * 
            self.products['product_width_cm']
        )
    
    def merge_order_data(self) -> pd.DataFrame:
        """Merge all order-related data into single dataframe"""
        # Merge orders with customers
        merged = self.orders.merge(self.customers, on='customer_id', how='left')
        
        # Merge with order items
        merged = merged.merge(self.order_items, on='order_id', how='left')
        
        # Merge with products
        merged = merged.merge(self.products, on='product_id', how='left')
        
        # Merge with payments
        merged = merged.merge(self.payments, on='order_id', how='left')
        
        logger.info(f"Merged dataset shape: {merged.shape}")
        return merged
    
    def get_data_summary(self) -> Dict:
        """Generate summary statistics for all datasets"""
        summary = {
            "total_orders": len(self.orders),
            "total_customers": len(self.customers),
            "total_products": len(self.products),
            "total_revenue": self.order_items['price'].sum() if 'price' in self.order_items.columns else 0,
            "avg_order_value": self.order_items['price'].mean() if 'price' in self.order_items.columns else 0,
            "delayed_orders": self.orders['is_delayed'].sum(),
            "delay_rate": (self.orders['is_delayed'].mean() * 100),
            "order_statuses": self.orders['order_status'].value_counts().to_dict(),
            "top_states": self.customers['customer_state'].value_counts().head(5).to_dict(),
            "top_categories": self.products['product_category_name'].value_counts().head(5).to_dict()
        }
        return summary


class DataSynthesizer:
    """Synthesize missing or additional data for testing"""
    
    @staticmethod
    def generate_supplier_data(n_suppliers: int = 100) -> pd.DataFrame:
        """Generate synthetic supplier data"""
        np.random.seed(42)
        
        suppliers = pd.DataFrame({
            'supplier_id': [f'SUP{str(i).zfill(5)}' for i in range(n_suppliers)],
            'supplier_name': [f'Supplier {i}' for i in range(n_suppliers)],
            'supplier_rating': np.random.uniform(3.0, 5.0, n_suppliers).round(2),
            'on_time_delivery_rate': np.random.uniform(0.7, 0.99, n_suppliers).round(2),
            'quality_score': np.random.uniform(70, 100, n_suppliers).round(2),
            'country': np.random.choice(['Brazil', 'USA', 'China', 'Germany', 'Japan'], n_suppliers)
        })
        
        logger.info(f"Generated {n_suppliers} synthetic supplier records")
        return suppliers
    
    @staticmethod
    def generate_inventory_data(products_df: pd.DataFrame) -> pd.DataFrame:
        """Generate synthetic inventory data based on products"""
        np.random.seed(42)
        
        n_products = len(products_df)
        inventory = products_df[['product_id', 'product_category_name']].copy()
        
        inventory['current_stock'] = np.random.randint(0, 500, n_products)
        inventory['reorder_point'] = np.random.randint(20, 100, n_products)
        inventory['max_stock'] = np.random.randint(500, 1000, n_products)
        inventory['warehouse_location'] = np.random.choice(['WH-A', 'WH-B', 'WH-C', 'WH-D'], n_products)
        inventory['last_restocked'] = pd.date_range(end=pd.Timestamp.now(), periods=n_products, freq='D')
        
        # Flag low stock
        inventory['is_low_stock'] = inventory['current_stock'] < inventory['reorder_point']
        
        logger.info(f"Generated inventory data for {n_products} products")
        return inventory
    
    @staticmethod
    def generate_demand_forecast(orders_df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """Generate demand forecast based on historical orders"""
        # Group orders by date
        orders_df['order_date'] = pd.to_datetime(orders_df['order_purchase_timestamp']).dt.date
        daily_orders = orders_df.groupby('order_date').size().reset_index(name='order_count')
        daily_orders['order_date'] = pd.to_datetime(daily_orders['order_date'])

        # Simple moving average forecast
        ma_window = 7
        daily_orders['forecast'] = daily_orders['order_count'].rolling(window=ma_window).mean()

        # Generate future dates
        last_date = daily_orders['order_date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')

        # Use last moving average as forecast
        last_forecast = daily_orders['forecast'].dropna().iloc[-1]

        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecasted_orders': [last_forecast] * periods
        })

        logger.info(f"Generated {periods}-day demand forecast")
        return forecast_df

    @staticmethod
    def generate_shipping_data(orders_df: pd.DataFrame) -> pd.DataFrame:
        """Generate synthetic shipping and logistics data"""
        np.random.seed(42)

        n_orders = len(orders_df)
        shipping_data = orders_df[['order_id']].copy()

        shipping_data['carrier'] = np.random.choice(
            ['FedEx', 'UPS', 'DHL', 'USPS', 'Local Courier'],
            n_orders,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        )
        shipping_data['shipping_cost'] = np.random.uniform(5, 50, n_orders).round(2)
        shipping_data['package_weight_kg'] = np.random.uniform(0.5, 25, n_orders).round(2)
        shipping_data['tracking_events'] = np.random.randint(3, 15, n_orders)
        shipping_data['delivery_attempts'] = np.random.choice([1, 2, 3], n_orders, p=[0.85, 0.12, 0.03])

        logger.info(f"Generated shipping data for {n_orders} orders")
        return shipping_data

    @staticmethod
    def generate_warehouse_data(n_warehouses: int = 10) -> pd.DataFrame:
        """Generate synthetic warehouse data"""
        np.random.seed(42)

        warehouses = pd.DataFrame({
            'warehouse_id': [f'WH-{str(i).zfill(3)}' for i in range(n_warehouses)],
            'warehouse_name': [f'Distribution Center {chr(65+i)}' for i in range(n_warehouses)],
            'location': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_warehouses),
            'capacity': np.random.randint(10000, 100000, n_warehouses),
            'current_utilization': np.random.uniform(0.5, 0.95, n_warehouses).round(2),
            'staff_count': np.random.randint(10, 100, n_warehouses),
            'operational_cost_daily': np.random.uniform(1000, 10000, n_warehouses).round(2)
        })

        logger.info(f"Generated {n_warehouses} warehouse records")
        return warehouses
