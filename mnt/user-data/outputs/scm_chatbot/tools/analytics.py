"""
Analytics Tools Module
Specialized analytics functions for supply chain insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DelayAnalytics:
    """Analytics for delivery delays"""
    
    def __init__(self, orders_df: pd.DataFrame):
        self.orders = orders_df
    
    def get_delay_summary(self) -> Dict:
        """Get overall delay statistics"""
        total_orders = len(self.orders)
        delayed_orders = self.orders['is_delayed'].sum()
        delay_rate = (delayed_orders / total_orders * 100) if total_orders > 0 else 0
        
        avg_delay = self.orders[self.orders['is_delayed']]['delivery_delay_days'].mean()
        max_delay = self.orders[self.orders['is_delayed']]['delivery_delay_days'].max()
        
        return {
            "total_orders": int(total_orders),
            "delayed_orders": int(delayed_orders),
            "on_time_orders": int(total_orders - delayed_orders),
            "delay_rate_percent": round(float(delay_rate), 2),
            "avg_delay_days": round(float(avg_delay), 2) if not pd.isna(avg_delay) else 0,
            "max_delay_days": int(max_delay) if not pd.isna(max_delay) else 0
        }
    
    def get_delays_by_state(self) -> pd.DataFrame:
        """Analyze delays by customer state"""
        merged = self.orders.copy()
        
        state_delays = merged.groupby('customer_state').agg({
            'is_delayed': ['sum', 'count', 'mean']
        }).round(2)
        
        state_delays.columns = ['delayed_count', 'total_orders', 'delay_rate']
        state_delays['delay_rate'] = (state_delays['delay_rate'] * 100).round(2)
        state_delays = state_delays.sort_values('delay_rate', ascending=False)
        
        return state_delays.head(10)
    
    def get_delays_by_month(self) -> pd.DataFrame:
        """Analyze delivery delays by month"""
        self.orders['order_month'] = pd.to_datetime(
            self.orders['order_purchase_timestamp']
        ).dt.to_period('M')
        
        monthly_delays = self.orders.groupby('order_month').agg({
            'is_delayed': ['sum', 'count', 'mean']
        }).round(2)
        
        monthly_delays.columns = ['delayed_count', 'total_orders', 'delay_rate']
        monthly_delays['delay_rate'] = (monthly_delays['delay_rate'] * 100).round(2)
        
        return monthly_delays


class RevenueAnalytics:
    """Analytics for revenue and sales"""
    
    def __init__(self, order_items_df: pd.DataFrame, orders_df: pd.DataFrame = None):
        self.order_items = order_items_df
        self.orders = orders_df
    
    def get_revenue_summary(self) -> Dict:
        """Get overall revenue statistics"""
        total_revenue = self.order_items['price'].sum()
        total_orders = self.order_items['order_id'].nunique()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        total_shipping = self.order_items['shipping_charges'].sum()
        
        return {
            "total_revenue": round(float(total_revenue), 2),
            "total_orders": int(total_orders),
            "avg_order_value": round(float(avg_order_value), 2),
            "total_shipping_charges": round(float(total_shipping), 2),
            "net_revenue": round(float(total_revenue - total_shipping), 2)
        }
    
    def get_revenue_by_category(self, products_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze revenue by product category"""
        merged = self.order_items.merge(products_df, on='product_id', how='left')
        
        category_revenue = merged.groupby('product_category_name').agg({
            'price': ['sum', 'count', 'mean']
        }).round(2)
        
        category_revenue.columns = ['total_revenue', 'order_count', 'avg_price']
        category_revenue = category_revenue.sort_values('total_revenue', ascending=False)
        
        return category_revenue.head(10)
    
    def get_monthly_revenue(self) -> pd.DataFrame:
        """Analyze revenue trends by month"""
        if self.orders is not None:
            merged = self.order_items.merge(self.orders[['order_id', 'order_purchase_timestamp']], 
                                          on='order_id', how='left')
            merged['order_month'] = pd.to_datetime(
                merged['order_purchase_timestamp']
            ).dt.to_period('M')
            
            monthly_revenue = merged.groupby('order_month').agg({
                'price': ['sum', 'count', 'mean']
            }).round(2)
            
            monthly_revenue.columns = ['total_revenue', 'order_count', 'avg_order_value']
            
            return monthly_revenue
        
        return pd.DataFrame()


class InventoryAnalytics:
    """Analytics for inventory management"""
    
    def __init__(self, inventory_df: pd.DataFrame):
        self.inventory = inventory_df
    
    def get_inventory_summary(self) -> Dict:
        """Get overall inventory statistics"""
        total_products = len(self.inventory)
        low_stock_items = self.inventory['is_low_stock'].sum()
        
        avg_stock = self.inventory['current_stock'].mean()
        total_stock_value = self.inventory['current_stock'].sum()
        
        return {
            "total_products": int(total_products),
            "low_stock_items": int(low_stock_items),
            "low_stock_rate_percent": round(float(low_stock_items / total_products * 100), 2),
            "avg_stock_level": round(float(avg_stock), 2),
            "total_stock_units": int(total_stock_value)
        }
    
    def get_low_stock_products(self, top_n: int = 20) -> pd.DataFrame:
        """Get products with low stock levels"""
        low_stock = self.inventory[self.inventory['is_low_stock']].copy()
        low_stock['urgency_score'] = (
            low_stock['reorder_point'] - low_stock['current_stock']
        ) / low_stock['reorder_point']
        
        return low_stock.sort_values('urgency_score', ascending=False).head(top_n)
    
    def get_inventory_by_warehouse(self) -> pd.DataFrame:
        """Analyze inventory distribution by warehouse"""
        warehouse_inv = self.inventory.groupby('warehouse_location').agg({
            'current_stock': ['sum', 'count', 'mean'],
            'is_low_stock': 'sum'
        }).round(2)
        
        warehouse_inv.columns = ['total_stock', 'product_count', 'avg_stock', 'low_stock_count']
        
        return warehouse_inv


class DemandForecasting:
    """Demand forecasting analytics"""
    
    def __init__(self, orders_df: pd.DataFrame):
        self.orders = orders_df
    
    def calculate_moving_average(self, window: int = 7) -> pd.DataFrame:
        """Calculate moving average forecast"""
        daily_orders = self.orders.groupby(
            pd.to_datetime(self.orders['order_purchase_timestamp']).dt.date
        ).size().reset_index(name='order_count')
        
        daily_orders.columns = ['date', 'order_count']
        daily_orders['date'] = pd.to_datetime(daily_orders['date'])
        daily_orders = daily_orders.sort_values('date')
        
        daily_orders['ma_forecast'] = daily_orders['order_count'].rolling(
            window=window
        ).mean()
        
        return daily_orders
    
    def forecast_next_n_days(self, n_days: int = 30) -> Dict:
        """Forecast demand for next n days"""
        ma_data = self.calculate_moving_average()
        last_ma = ma_data['ma_forecast'].dropna().iloc[-1]
        
        forecast = {
            "forecast_period_days": n_days,
            "avg_daily_orders": round(float(last_ma), 2),
            "total_forecasted_orders": round(float(last_ma * n_days), 0),
            "forecast_method": "7-day moving average"
        }
        
        return forecast
    
    def calculate_forecast_accuracy(self, actual_df: pd.DataFrame, 
                                    forecast_df: pd.DataFrame) -> Dict:
        """Calculate forecast accuracy metrics (MAPE, RMSE)"""
        actual = actual_df['order_count'].values
        forecast = forecast_df['ma_forecast'].dropna().values
        
        # Align lengths
        min_len = min(len(actual), len(forecast))
        actual = actual[-min_len:]
        forecast = forecast[-min_len:]
        
        # Calculate MAPE
        mape = np.mean(np.abs((actual - forecast) / actual)) * 100
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((actual - forecast) ** 2))
        
        return {
            "mape": round(float(mape), 2),
            "rmse": round(float(rmse), 2),
            "samples": int(min_len)
        }


class SupplierAnalytics:
    """Analytics for supplier performance"""
    
    def __init__(self, suppliers_df: pd.DataFrame):
        self.suppliers = suppliers_df
    
    def get_supplier_summary(self) -> Dict:
        """Get overall supplier statistics"""
        total_suppliers = len(self.suppliers)
        avg_rating = self.suppliers['supplier_rating'].mean()
        avg_on_time = self.suppliers['on_time_delivery_rate'].mean()
        
        return {
            "total_suppliers": int(total_suppliers),
            "avg_supplier_rating": round(float(avg_rating), 2),
            "avg_on_time_delivery_rate": round(float(avg_on_time), 2),
            "top_rated_suppliers": int((self.suppliers['supplier_rating'] >= 4.5).sum())
        }
    
    def get_top_suppliers(self, top_n: int = 10) -> pd.DataFrame:
        """Get top performing suppliers"""
        # Calculate composite score
        self.suppliers['performance_score'] = (
            self.suppliers['supplier_rating'] * 0.4 +
            self.suppliers['on_time_delivery_rate'] * 5 * 0.4 +
            self.suppliers['quality_score'] / 20 * 0.2
        )
        
        return self.suppliers.sort_values(
            'performance_score', ascending=False
        ).head(top_n)
    
    def get_supplier_risk_analysis(self) -> pd.DataFrame:
        """Identify at-risk suppliers"""
        at_risk = self.suppliers[
            (self.suppliers['on_time_delivery_rate'] < 0.85) |
            (self.suppliers['supplier_rating'] < 3.5)
        ].copy()
        
        at_risk['risk_level'] = 'Medium'
        at_risk.loc[
            (at_risk['on_time_delivery_rate'] < 0.75) |
            (at_risk['supplier_rating'] < 3.0),
            'risk_level'
        ] = 'High'
        
        return at_risk.sort_values(['risk_level', 'on_time_delivery_rate'])
