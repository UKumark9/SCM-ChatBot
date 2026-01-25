"""
Test Suite for SCM Chatbot
Comprehensive testing for all components
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_loader import SCMDataLoader, DataSynthesizer
from tools.analytics import (
    DelayAnalytics, RevenueAnalytics, InventoryAnalytics,
    DemandForecasting, SupplierAnalytics
)


class TestDataLoader:
    """Test data loading and preprocessing"""
    
    def test_synthetic_supplier_data(self):
        """Test supplier data generation"""
        suppliers = DataSynthesizer.generate_supplier_data(n_suppliers=50)
        
        assert len(suppliers) == 50
        assert 'supplier_id' in suppliers.columns
        assert 'supplier_rating' in suppliers.columns
        assert suppliers['supplier_rating'].between(3.0, 5.0).all()
    
    def test_synthetic_inventory_data(self):
        """Test inventory data generation"""
        # Create sample products
        products = pd.DataFrame({
            'product_id': ['P1', 'P2', 'P3'],
            'product_category_name': ['toys', 'books', 'electronics']
        })
        
        inventory = DataSynthesizer.generate_inventory_data(products)
        
        assert len(inventory) == 3
        assert 'current_stock' in inventory.columns
        assert 'is_low_stock' in inventory.columns
    
    def test_demand_forecast_generation(self):
        """Test demand forecast generation"""
        # Create sample orders
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        orders = pd.DataFrame({
            'order_id': [f'O{i}' for i in range(30)],
            'order_purchase_timestamp': dates,
            'order_status': 'delivered'
        })
        
        forecast = DataSynthesizer.generate_demand_forecast(orders, periods=7)
        
        assert len(forecast) == 7
        assert 'forecasted_orders' in forecast.columns


class TestDelayAnalytics:
    """Test delay analytics functions"""
    
    @pytest.fixture
    def sample_orders(self):
        """Create sample orders data"""
        return pd.DataFrame({
            'order_id': ['O1', 'O2', 'O3', 'O4'],
            'order_status': ['delivered', 'delivered', 'delivered', 'delivered'],
            'is_delayed': [True, False, True, False],
            'delivery_delay_days': [5, 0, 3, 0],
            'customer_state': ['SP', 'RJ', 'SP', 'MG']
        })
    
    def test_delay_summary(self, sample_orders):
        """Test delay summary calculation"""
        analytics = DelayAnalytics(sample_orders)
        summary = analytics.get_delay_summary()
        
        assert summary['total_orders'] == 4
        assert summary['delayed_orders'] == 2
        assert summary['delay_rate_percent'] == 50.0
        assert summary['avg_delay_days'] == 4.0
    
    def test_delays_by_state(self, sample_orders):
        """Test delay analysis by state"""
        analytics = DelayAnalytics(sample_orders)
        state_delays = analytics.get_delays_by_state()
        
        assert 'delay_rate' in state_delays.columns
        assert len(state_delays) > 0


class TestRevenueAnalytics:
    """Test revenue analytics functions"""
    
    @pytest.fixture
    def sample_order_items(self):
        """Create sample order items data"""
        return pd.DataFrame({
            'order_id': ['O1', 'O1', 'O2', 'O3'],
            'product_id': ['P1', 'P2', 'P3', 'P1'],
            'price': [100.0, 50.0, 75.0, 100.0],
            'shipping_charges': [10.0, 5.0, 8.0, 10.0]
        })
    
    def test_revenue_summary(self, sample_order_items):
        """Test revenue summary calculation"""
        analytics = RevenueAnalytics(sample_order_items)
        summary = analytics.get_revenue_summary()
        
        assert summary['total_revenue'] == 325.0
        assert summary['total_orders'] == 3
        assert summary['avg_order_value'] > 0
        assert summary['total_shipping_charges'] == 33.0


class TestInventoryAnalytics:
    """Test inventory analytics functions"""
    
    @pytest.fixture
    def sample_inventory(self):
        """Create sample inventory data"""
        return pd.DataFrame({
            'product_id': ['P1', 'P2', 'P3', 'P4'],
            'current_stock': [5, 50, 100, 15],
            'reorder_point': [20, 30, 50, 25],
            'is_low_stock': [True, False, False, True],
            'warehouse_location': ['WH-A', 'WH-A', 'WH-B', 'WH-B']
        })
    
    def test_inventory_summary(self, sample_inventory):
        """Test inventory summary calculation"""
        analytics = InventoryAnalytics(sample_inventory)
        summary = analytics.get_inventory_summary()
        
        assert summary['total_products'] == 4
        assert summary['low_stock_items'] == 2
        assert summary['low_stock_rate_percent'] == 50.0
    
    def test_low_stock_products(self, sample_inventory):
        """Test low stock products retrieval"""
        analytics = InventoryAnalytics(sample_inventory)
        low_stock = analytics.get_low_stock_products(top_n=10)
        
        assert len(low_stock) == 2
        assert 'urgency_score' in low_stock.columns


class TestDemandForecasting:
    """Test demand forecasting functions"""
    
    @pytest.fixture
    def sample_orders(self):
        """Create sample orders for forecasting"""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        return pd.DataFrame({
            'order_id': [f'O{i}' for i in range(30)],
            'order_purchase_timestamp': dates,
            'order_status': 'delivered'
        })
    
    def test_moving_average(self, sample_orders):
        """Test moving average calculation"""
        forecaster = DemandForecasting(sample_orders)
        ma_data = forecaster.calculate_moving_average(window=7)
        
        assert 'ma_forecast' in ma_data.columns
        assert len(ma_data) > 0
    
    def test_forecast_next_days(self, sample_orders):
        """Test future forecast"""
        forecaster = DemandForecasting(sample_orders)
        forecast = forecaster.forecast_next_n_days(n_days=7)
        
        assert forecast['forecast_period_days'] == 7
        assert 'avg_daily_orders' in forecast
        assert 'total_forecasted_orders' in forecast


class TestSupplierAnalytics:
    """Test supplier analytics functions"""
    
    @pytest.fixture
    def sample_suppliers(self):
        """Create sample suppliers data"""
        return pd.DataFrame({
            'supplier_id': ['S1', 'S2', 'S3'],
            'supplier_name': ['Supplier 1', 'Supplier 2', 'Supplier 3'],
            'supplier_rating': [4.5, 3.8, 4.9],
            'on_time_delivery_rate': [0.95, 0.75, 0.98],
            'quality_score': [90, 75, 95],
            'country': ['Brazil', 'USA', 'Germany']
        })
    
    def test_supplier_summary(self, sample_suppliers):
        """Test supplier summary calculation"""
        analytics = SupplierAnalytics(sample_suppliers)
        summary = analytics.get_supplier_summary()
        
        assert summary['total_suppliers'] == 3
        assert 'avg_supplier_rating' in summary
        assert 'avg_on_time_delivery_rate' in summary
    
    def test_top_suppliers(self, sample_suppliers):
        """Test top suppliers retrieval"""
        analytics = SupplierAnalytics(sample_suppliers)
        top = analytics.get_top_suppliers(top_n=2)
        
        assert len(top) <= 2
        assert 'performance_score' in top.columns
    
    def test_supplier_risk_analysis(self, sample_suppliers):
        """Test supplier risk analysis"""
        analytics = SupplierAnalytics(sample_suppliers)
        at_risk = analytics.get_supplier_risk_analysis()
        
        assert 'risk_level' in at_risk.columns


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_end_to_end_analytics(self):
        """Test complete analytics workflow"""
        # Generate test data
        orders = pd.DataFrame({
            'order_id': ['O1', 'O2'],
            'customer_id': ['C1', 'C2'],
            'order_status': ['delivered', 'delivered'],
            'is_delayed': [True, False],
            'delivery_delay_days': [5, 0],
            'customer_state': ['SP', 'RJ'],
            'order_purchase_timestamp': pd.date_range(start='2024-01-01', periods=2)
        })
        
        order_items = pd.DataFrame({
            'order_id': ['O1', 'O2'],
            'product_id': ['P1', 'P2'],
            'price': [100.0, 150.0],
            'shipping_charges': [10.0, 15.0]
        })
        
        # Test delay analytics
        delay_analytics = DelayAnalytics(orders)
        delay_summary = delay_analytics.get_delay_summary()
        assert 'delay_rate_percent' in delay_summary
        
        # Test revenue analytics
        revenue_analytics = RevenueAnalytics(order_items, orders)
        revenue_summary = revenue_analytics.get_revenue_summary()
        assert 'total_revenue' in revenue_summary


def run_tests():
    """Run all tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()
