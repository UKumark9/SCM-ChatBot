"""
Data Processing Module for SCM Chatbot
Handles data loading, preprocessing, and transformation
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles all data processing operations for the SCM chatbot"""
    
    def __init__(self, data_paths: Dict[str, Dict[str, str]]):
        self.data_paths = data_paths
        self.customers = None
        self.orders = None
        self.order_items = None
        self.payments = None
        self.products = None
        
    def load_data(self, dataset_type: str = "train") -> None:
        """Load all datasets from CSV files"""
        try:
            logger.info(f"Loading {dataset_type} datasets...")
            paths = self.data_paths[dataset_type]
            
            self.customers = pd.read_csv(paths["customers"])
            self.orders = pd.read_csv(paths["orders"])
            self.order_items = pd.read_csv(paths["order_items"])
            self.payments = pd.read_csv(paths["payments"])
            self.products = pd.read_csv(paths["products"])
            
            logger.info(f"Successfully loaded {dataset_type} datasets")
            logger.info(f"Customers: {len(self.customers)}, Orders: {len(self.orders)}, "
                       f"OrderItems: {len(self.order_items)}, Payments: {len(self.payments)}, "
                       f"Products: {len(self.products)}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def preprocess_data(self) -> None:
        """Preprocess and clean all datasets"""
        try:
            logger.info("Preprocessing data...")
            
            # Process Orders
            self.orders['order_purchase_timestamp'] = pd.to_datetime(
                self.orders['order_purchase_timestamp'], errors='coerce'
            )
            self.orders['order_approved_at'] = pd.to_datetime(
                self.orders['order_approved_at'], errors='coerce'
            )
            self.orders['order_delivered_customer_date'] = pd.to_datetime(
                self.orders['order_delivered_customer_date'], errors='coerce'
            )
            self.orders['order_estimated_delivery_date'] = pd.to_datetime(
                self.orders['order_estimated_delivery_date'], errors='coerce'
            )
            
            # Calculate delivery delay
            self.orders['actual_delivery_days'] = (
                self.orders['order_delivered_customer_date'] - 
                self.orders['order_purchase_timestamp']
            ).dt.days
            
            self.orders['estimated_delivery_days'] = (
                self.orders['order_estimated_delivery_date'] - 
                self.orders['order_purchase_timestamp']
            ).dt.days
            
            self.orders['delay_days'] = (
                self.orders['actual_delivery_days'] - 
                self.orders['estimated_delivery_days']
            )
            
            self.orders['is_delayed'] = self.orders['delay_days'] > 0
            
            # Extract time features
            self.orders['order_year'] = self.orders['order_purchase_timestamp'].dt.year
            self.orders['order_month'] = self.orders['order_purchase_timestamp'].dt.month
            self.orders['order_day'] = self.orders['order_purchase_timestamp'].dt.day
            self.orders['order_weekday'] = self.orders['order_purchase_timestamp'].dt.dayofweek
            
            # Process Products
            if 'product_name_length' in self.products.columns:
                self.products['product_name_length'] = self.products['product_name_length'].fillna(0)
            
            if 'product_description_length' in self.products.columns:
                self.products['product_description_length'] = self.products['product_description_length'].fillna(0)
            
            # Process Payments
            if 'payment_value' in self.payments.columns:
                self.payments['payment_value'] = pd.to_numeric(
                    self.payments['payment_value'], errors='coerce'
                ).fillna(0)
            
            logger.info("Data preprocessing completed successfully")
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
    
    def create_merged_dataset(self) -> pd.DataFrame:
        """Create a comprehensive merged dataset for analytics"""
        try:
            logger.info("Creating merged dataset...")
            
            # Merge orders with customers
            merged = self.orders.merge(
                self.customers, 
                on='customer_id', 
                how='left'
            )
            
            # Merge with order items
            merged = merged.merge(
                self.order_items,
                on='order_id',
                how='left'
            )
            
            # Merge with products
            merged = merged.merge(
                self.products,
                on='product_id',
                how='left'
            )
            
            # Merge with payments
            payment_summary = self.payments.groupby('order_id').agg({
                'payment_value': 'sum',
                'payment_type': lambda x: ', '.join(x.unique())
            }).reset_index()
            
            merged = merged.merge(
                payment_summary,
                on='order_id',
                how='left'
            )
            
            logger.info(f"Merged dataset created with {len(merged)} records")
            return merged
            
        except Exception as e:
            logger.error(f"Error creating merged dataset: {str(e)}")
            raise
    
    def get_summary_statistics(self) -> Dict:
        """Generate summary statistics for the dataset"""
        try:
            stats = {
                "total_customers": len(self.customers),
                "total_orders": len(self.orders),
                "total_products": len(self.products),
                "total_order_items": len(self.order_items),
                "delayed_orders": self.orders['is_delayed'].sum() if 'is_delayed' in self.orders.columns else 0,
                "delay_rate": (self.orders['is_delayed'].mean() * 100) if 'is_delayed' in self.orders.columns else 0,
                "average_delay_days": self.orders[self.orders['is_delayed']]['delay_days'].mean() if 'is_delayed' in self.orders.columns else 0,
                "total_revenue": self.payments['payment_value'].sum() if 'payment_value' in self.payments.columns else 0,
                "average_order_value": self.payments.groupby('order_id')['payment_value'].sum().mean() if 'payment_value' in self.payments.columns else 0,
                "date_range": {
                    "start": str(self.orders['order_purchase_timestamp'].min()),
                    "end": str(self.orders['order_purchase_timestamp'].max())
                } if 'order_purchase_timestamp' in self.orders.columns else None
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error generating summary statistics: {str(e)}")
            raise
    
    def generate_synthetic_inventory_data(self) -> pd.DataFrame:
        """Generate synthetic inventory data for products"""
        try:
            logger.info("Generating synthetic inventory data...")
            
            inventory_data = []
            
            for _, product in self.products.iterrows():
                inventory_data.append({
                    'product_id': product['product_id'],
                    'current_stock': np.random.randint(50, 500),
                    'reorder_level': np.random.randint(100, 200),
                    'warehouse_location': np.random.choice(['WH-A', 'WH-B', 'WH-C', 'WH-D']),
                    'last_restocked': datetime.now() - timedelta(days=np.random.randint(1, 30)),
                    'supplier_id': f"SUP-{np.random.randint(1000, 9999)}"
                })
            
            inventory_df = pd.DataFrame(inventory_data)
            logger.info(f"Generated inventory data for {len(inventory_df)} products")
            
            return inventory_df
            
        except Exception as e:
            logger.error(f"Error generating inventory data: {str(e)}")
            raise
    
    def generate_synthetic_supplier_data(self) -> pd.DataFrame:
        """Generate synthetic supplier performance data"""
        try:
            logger.info("Generating synthetic supplier data...")
            
            supplier_ids = [f"SUP-{i:04d}" for i in range(1000, 1020)]
            
            supplier_data = []
            
            for supplier_id in supplier_ids:
                supplier_data.append({
                    'supplier_id': supplier_id,
                    'supplier_name': f"Supplier {supplier_id.split('-')[1]}",
                    'on_time_delivery_rate': np.random.uniform(0.75, 0.98),
                    'quality_rating': np.random.uniform(3.5, 5.0),
                    'total_orders': np.random.randint(100, 1000),
                    'average_lead_time_days': np.random.randint(5, 20),
                    'location': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Brasília', 'Curitiba'])
                })
            
            supplier_df = pd.DataFrame(supplier_data)
            logger.info(f"Generated supplier data for {len(supplier_df)} suppliers")
            
            return supplier_df
            
        except Exception as e:
            logger.error(f"Error generating supplier data: {str(e)}")
            raise


def load_and_prepare_data(data_paths: Dict[str, Dict[str, str]], 
                         dataset_type: str = "train") -> Tuple[DataProcessor, pd.DataFrame]:
    """Convenience function to load and prepare all data"""
    processor = DataProcessor(data_paths)
    processor.load_data(dataset_type)
    processor.preprocess_data()
    merged_data = processor.create_merged_dataset()
    
    return processor, merged_data
