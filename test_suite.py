"""
Comprehensive Test Suite for SCM Chatbot
Tests all major components and functionalities
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.data_processor import DataProcessor
from modules.analytics import SCMAnalytics
from utils.helpers import (
    format_number, format_percentage, format_currency,
    validate_query, CacheManager, PerformanceMonitor
)


class TestDataProcessor:
    """Test data processing functionality"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return {
            "train": {
                "customers": "test_customers.csv",
                "orders": "test_orders.csv",
                "order_items": "test_order_items.csv",
                "payments": "test_payments.csv",
                "products": "test_products.csv"
            }
        }
    
    def test_data_processor_initialization(self, sample_data):
        """Test DataProcessor initialization"""
        processor = DataProcessor(sample_data)
        assert processor is not None
        assert processor.customers is None  # Not loaded yet
    
    def test_create_sample_datasets(self, tmp_path):
        """Test creating sample datasets for testing"""
        # Create sample customers
        customers = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003'],
            'customer_zip_code_prefix': [12345, 23456, 34567],
            'customer_city': ['City1', 'City2', 'City3'],
            'customer_state': ['SP', 'RJ', 'MG']
        })
        
        # Create sample orders
        orders = pd.DataFrame({
            'order_id': ['O001', 'O002', 'O003'],
            'customer_id': ['C001', 'C002', 'C003'],
            'order_status': ['delivered', 'delivered', 'shipped'],
            'order_purchase_timestamp': [
                datetime.now() - timedelta(days=10),
                datetime.now() - timedelta(days=8),
                datetime.now() - timedelta(days=5)
            ],
            'order_approved_at': [
                datetime.now() - timedelta(days=10),
                datetime.now() - timedelta(days=8),
                datetime.now() - timedelta(days=5)
            ],
            'order_delivered_customer_date': [
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=3),
                None
            ],
            'order_estimated_delivery_date': [
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=2),
                datetime.now() + timedelta(days=2)
            ]
        })
        
        assert len(customers) == 3
        assert len(orders) == 3
    
    def test_synthetic_inventory_generation(self):
        """Test synthetic inventory data generation"""
        products = pd.DataFrame({
            'product_id': [f'P{i:03d}' for i in range(10)]
        })
        
        processor = DataProcessor({})
        processor.products = products
        
        inventory = processor.generate_synthetic_inventory_data()
        
        assert len(inventory) == len(products)
        assert 'current_stock' in inventory.columns
        assert 'reorder_level' in inventory.columns
        assert 'warehouse_location' in inventory.columns
    
    def test_synthetic_supplier_generation(self):
        """Test synthetic supplier data generation"""
        processor = DataProcessor({})
        supplier_data = processor.generate_synthetic_supplier_data()
        
        assert len(supplier_data) > 0
        assert 'supplier_id' in supplier_data.columns
        assert 'on_time_delivery_rate' in supplier_data.columns
        assert 'quality_rating' in supplier_data.columns


class TestAnalytics:
    """Test analytics functionality"""
    
    @pytest.fixture
    def sample_processor(self):
        """Create sample data processor"""
        processor = DataProcessor({})
        
        # Create sample orders with delays
        processor.orders = pd.DataFrame({
            'order_id': [f'O{i:03d}' for i in range(100)],
            'customer_id': [f'C{i%10:03d}' for i in range(100)],
            'customer_state': ['SP'] * 50 + ['RJ'] * 30 + ['MG'] * 20,
            'order_status': ['delivered'] * 100,
            'order_purchase_timestamp': [
                datetime.now() - timedelta(days=i) for i in range(100)
            ],
            'is_delayed': [True] * 60 + [False] * 40,
            'delay_days': [i % 10 for i in range(60)] + [0] * 40,
            'order_month': [(datetime.now() - timedelta(days=i)).month for i in range(100)]
        })
        
        # Create sample payments
        processor.payments = pd.DataFrame({
            'order_id': [f'O{i:03d}' for i in range(100)],
            'payment_value': np.random.uniform(50, 500, 100)
        })
        
        # Create sample products
        processor.products = pd.DataFrame({
            'product_id': [f'P{i:03d}' for i in range(50)],
            'product_category_name': ['Category1'] * 25 + ['Category2'] * 25
        })
        
        # Create sample order items
        processor.order_items = pd.DataFrame({
            'order_id': [f'O{i%100:03d}' for i in range(200)],
            'product_id': [f'P{i%50:03d}' for i in range(200)],
            'price': np.random.uniform(20, 200, 200)
        })
        
        # Create sample customers
        processor.customers = pd.DataFrame({
            'customer_id': [f'C{i:03d}' for i in range(10)],
            'customer_state': ['SP', 'RJ', 'MG', 'SP', 'RJ', 'MG', 'SP', 'RJ', 'MG', 'SP']
        })
        
        return processor
    
    def test_delay_analysis(self, sample_processor):
        """Test delivery delay analysis"""
        analytics = SCMAnalytics(sample_processor)
        result = analytics.analyze_delivery_delays()
        
        assert 'total_orders' in result
        assert 'delayed_orders' in result
        assert 'delay_rate_percentage' in result
        assert result['delay_rate_percentage'] >= 0
        assert result['delay_rate_percentage'] <= 100
    
    def test_revenue_analysis(self, sample_processor):
        """Test revenue analysis"""
        analytics = SCMAnalytics(sample_processor)
        result = analytics.analyze_revenue_trends()
        
        assert 'total_revenue' in result
        assert 'average_order_value' in result
        assert result['total_revenue'] > 0
    
    def test_product_performance(self, sample_processor):
        """Test product performance analysis"""
        analytics = SCMAnalytics(sample_processor)
        result = analytics.analyze_product_performance()
        
        assert 'total_unique_products' in result
        assert 'total_items_sold' in result
        assert result['total_items_sold'] > 0
    
    def test_demand_forecast(self, sample_processor):
        """Test demand forecasting"""
        analytics = SCMAnalytics(sample_processor)
        result = analytics.forecast_demand(periods=7)
        
        assert 'forecast' in result
        assert 'model_metrics' in result
        assert 'mape' in result['model_metrics']
        assert len(result['forecast']) == 7


class TestUtilities:
    """Test utility functions"""
    
    def test_format_number(self):
        """Test number formatting"""
        assert format_number(1234.56) == "1,234.56"
        assert format_number(1000000) == "1,000,000.00"
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        assert format_percentage(50.5) == "50.50%"
        assert format_percentage(100) == "100.00%"
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(1000) == "$1,000.00"
    
    def test_validate_query(self):
        """Test query validation"""
        valid, msg = validate_query("What are the delays?")
        assert valid == True
        
        valid, msg = validate_query("")
        assert valid == False
        
        valid, msg = validate_query("<script>alert('xss')</script>")
        assert valid == False
    
    def test_cache_manager(self):
        """Test cache functionality"""
        cache = CacheManager(ttl=1)
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test expiration
        import time
        time.sleep(2)
        assert cache.get("key1") is None
        
        # Test clear
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key2") is None
    
    def test_performance_monitor(self):
        """Test performance monitoring"""
        monitor = PerformanceMonitor()
        
        # Record some metrics
        monitor.record_query_time(0.5)
        monitor.record_query_time(1.0)
        monitor.record_error()
        
        metrics = monitor.get_metrics()
        
        assert metrics['total_queries'] == 2
        assert metrics['total_errors'] == 1
        assert metrics['average_response_time'] == 0.75
        assert metrics['error_rate'] == 50.0


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_query_flow(self):
        """Test complete query processing flow"""
        # This would test the full flow from query to response
        # Skipped in this example as it requires full system initialization
        pass
    
    def test_rag_integration(self):
        """Test RAG system integration"""
        # This would test the RAG system
        # Skipped as it requires embeddings model
        pass


def run_tests():
    """Run all tests"""
    pytest.main([__file__, '-v', '--cov=../', '--cov-report=html'])


if __name__ == "__main__":
    run_tests()
