"""
Analytics Module for SCM Chatbot
Provides various analytical tools for supply chain insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

logger = logging.getLogger(__name__)


class SCMAnalytics:
    """Supply Chain Management Analytics Engine"""
    
    def __init__(self, data_processor, feature_store=None):
        self.data_processor = data_processor
        self.orders = data_processor.orders
        self.order_items = data_processor.order_items
        self.products = data_processor.products
        self.payments = data_processor.payments
        self.customers = data_processor.customers
        self.feature_store = feature_store
    
    def analyze_delivery_delays(self) -> Dict:
        """Analyze delivery delay patterns"""
        try:
            if self.feature_store:
                cached = self.feature_store.get('analytics', 'delivery_delays')
                if cached:
                    logger.info("Cache hit: analytics/delivery_delays")
                    return cached

            logger.info("Analyzing delivery delays...")
            
            delayed_orders = self.orders[self.orders['is_delayed'] == True]
            
            analysis = {
                "total_orders": len(self.orders),
                "delayed_orders": len(delayed_orders),
                "delay_rate_percentage": (len(delayed_orders) / len(self.orders)) * 100,
                "average_delay_days": delayed_orders['delay_days'].mean(),
                "max_delay_days": delayed_orders['delay_days'].max(),
                "median_delay_days": delayed_orders['delay_days'].median(),
                "delays_by_state": self.orders.groupby('customer_state')['is_delayed'].mean().to_dict(),
                "delays_by_month": self.orders.groupby('order_month')['is_delayed'].mean().to_dict()
            }
            
            logger.info(f"Delay analysis completed: {analysis['delay_rate_percentage']:.2f}% delay rate")

            if self.feature_store:
                self.feature_store.set('analytics', 'delivery_delays', analysis, ttl=1800)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing delivery delays: {str(e)}")
            raise

    def analyze_product_delays(self, product_id: Optional[str] = None, category: Optional[str] = None) -> Dict:
       """Analyze delivery delays at product or category level"""
       try:
           cache_key = f"product_delays_{product_id or 'all'}_{category or 'all'}"
           if self.feature_store:
               cached = self.feature_store.get('analytics', cache_key)
               if cached:
                   logger.info(f"Cache hit: analytics/{cache_key}")
                   return cached

           logger.info(f"Analyzing product-level delivery delays (product_id={product_id}, category={category})...")

           # Merge orders with order items and products
           order_products = self.orders.merge(
               self.order_items,
               on='order_id',
               how='inner'
           ).merge(
               self.products,
               on='product_id',
               how='left'
           )

           logger.info(f"Merged data has {len(order_products)} rows")

           # Filter by product or category if specified
           if product_id:
               filtered_data = order_products[order_products['product_id'] == product_id]
               filter_label = f"Product {product_id}"
           elif category:
               if 'product_category_name' in order_products.columns:
                   filtered_data = order_products[order_products['product_category_name'] == category]
                   filter_label = f"Category {category}"
               else:
                   return {"error": "Product category information not available"}
           else:
               filtered_data = order_products
               filter_label = "All Products"

           if len(filtered_data) == 0:
               return {
                   "error": f"No data found for {filter_label}",
                   "filter": filter_label
               }

           # Calculate delays
           delayed_orders = filtered_data[filtered_data['is_delayed'] == True]

           analysis = {
               "filter": filter_label,
               "product_id": product_id,
               "category": category,
               "total_orders": len(filtered_data),
               "delayed_orders": len(delayed_orders),
               "delay_rate_percentage": (len(delayed_orders) / len(filtered_data)) * 100 if len(filtered_data) > 0 else 0,
               "average_delay_days": float(delayed_orders['delay_days'].mean()) if len(delayed_orders) > 0 else 0,
               "max_delay_days": float(delayed_orders['delay_days'].max()) if len(delayed_orders) > 0 else 0,
               "median_delay_days": float(delayed_orders['delay_days'].median()) if len(delayed_orders) > 0 else 0
           }

           # If analyzing all products, add top delayed products/categories
           if not product_id and not category:
               # Top delayed products
               logger.info("Calculating top delayed products...")
               product_delays = order_products.groupby('product_id').agg({
                   'is_delayed': ['sum', 'count', 'mean']
               }).reset_index()

               # Handle multi-level columns from groupby
               product_delays.columns = ['product_id', 'delayed_count', 'total_count', 'delay_rate']

               logger.info(f"Found {len(product_delays)} unique products")

               # Filter products with minimum 5 orders
               product_delays_filtered = product_delays[product_delays['total_count'] >= 5].copy()
               logger.info(f"Products with 5+ orders: {len(product_delays_filtered)}")

               # Sort by delay rate
               product_delays_filtered = product_delays_filtered.sort_values('delay_rate', ascending=False)
               top_delayed_products = product_delays_filtered.head(10)

               logger.info(f"Top delayed products:\n{top_delayed_products}")
               analysis['top_delayed_products'] = top_delayed_products.to_dict('records')

               # Top delayed categories
               if 'product_category_name' in order_products.columns:
                   logger.info("Calculating top delayed categories...")
                   category_delays = order_products.groupby('product_category_name').agg({
                       'is_delayed': ['sum', 'count', 'mean']
                   }).reset_index()

                   category_delays.columns = ['category', 'delayed_count', 'total_count', 'delay_rate']

                   # Filter categories with minimum 10 orders
                   category_delays_filtered = category_delays[category_delays['total_count'] >= 10].copy()
                   logger.info(f"Categories with 10+ orders: {len(category_delays_filtered)}")

                   # Sort by delay rate
                   category_delays_filtered = category_delays_filtered.sort_values('delay_rate', ascending=False)
                   top_delayed_categories = category_delays_filtered.head(10)

                   logger.info(f"Top delayed categories:\n{top_delayed_categories}")
                   analysis['top_delayed_categories'] = top_delayed_categories.to_dict('records')

           logger.info(f"Product delay analysis completed: {analysis['delay_rate_percentage']:.2f}% delay rate for {filter_label}")

           if self.feature_store:
               self.feature_store.set('analytics', cache_key, analysis, ttl=1800)

           return analysis

       except Exception as e:
           logger.error(f"Error analyzing product delays: {str(e)}", exc_info=True)
           return {
               "error": f"Error analyzing product delays: {str(e)}",
               "filter": "All Products" if not product_id and not category else (product_id or category)
           }
        
    def analyze_revenue_trends(self) -> Dict:
        """Analyze revenue and sales trends"""
        try:
            if self.feature_store:
                cached = self.feature_store.get('analytics', 'revenue_trends')
                if cached:
                    logger.info("Cache hit: analytics/revenue_trends")
                    return cached

            logger.info("Analyzing revenue trends...")
            
            # Merge orders with payments
            orders_payments = self.orders.merge(
                self.payments.groupby('order_id')['payment_value'].sum().reset_index(),
                on='order_id',
                how='left'
            )
            
            # Monthly revenue
            orders_payments['year_month'] = orders_payments['order_purchase_timestamp'].dt.to_period('M')
            monthly_revenue = orders_payments.groupby('year_month')['payment_value'].sum()
            
            # Calculate growth rate
            revenue_list = monthly_revenue.values
            if len(revenue_list) > 1:
                growth_rates = [(revenue_list[i] - revenue_list[i-1]) / revenue_list[i-1] * 100 
                               for i in range(1, len(revenue_list))]
                avg_growth_rate = np.mean(growth_rates)
            else:
                avg_growth_rate = 0
            
            analysis = {
                "total_revenue": orders_payments['payment_value'].sum(),
                "average_order_value": orders_payments['payment_value'].mean(),
                "monthly_revenue": {str(k): float(v) for k, v in monthly_revenue.to_dict().items()},
                "average_monthly_growth_rate": avg_growth_rate,
                "highest_revenue_month": str(monthly_revenue.idxmax()),
                "lowest_revenue_month": str(monthly_revenue.idxmin()),
                "revenue_by_state": orders_payments.groupby('customer_state')['payment_value'].sum().to_dict()
            }
            
            logger.info(f"Revenue analysis completed: Total revenue ${analysis['total_revenue']:,.2f}")

            if self.feature_store:
                self.feature_store.set('analytics', 'revenue_trends', analysis, ttl=3600)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {str(e)}")
            raise
    
    def analyze_product_performance(self) -> Dict:
        """Analyze product sales performance"""
        try:
            if self.feature_store:
                cached = self.feature_store.get('analytics', 'product_performance')
                if cached:
                    logger.info("Cache hit: analytics/product_performance")
                    return cached

            logger.info("Analyzing product performance...")
            
            # Merge order items with products
            product_sales = self.order_items.merge(
                self.products,
                on='product_id',
                how='left'
            )
            
            # Top selling products
            top_products = product_sales.groupby('product_id').agg({
                'order_id': 'count',
                'price': 'sum'
            }).sort_values('order_id', ascending=False).head(10)
            
            # Product category analysis
            if 'product_category_name' in product_sales.columns:
                category_sales = product_sales.groupby('product_category_name').agg({
                    'order_id': 'count',
                    'price': 'sum'
                }).sort_values('price', ascending=False)
            else:
                category_sales = None
            
            analysis = {
                "total_unique_products": len(product_sales['product_id'].unique()),
                "total_items_sold": len(product_sales),
                "average_product_price": product_sales['price'].mean(),
                "top_selling_products": top_products.to_dict(),
                "category_performance": category_sales.to_dict() if category_sales is not None else {}
            }
            
            logger.info(f"Product analysis completed: {analysis['total_unique_products']} unique products")

            if self.feature_store:
                self.feature_store.set('analytics', 'product_performance', analysis, ttl=3600)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing product performance: {str(e)}")
            raise
    
    def analyze_customer_behavior(self) -> Dict:
        """Analyze customer ordering patterns"""
        try:
            if self.feature_store:
                cached = self.feature_store.get('analytics', 'customer_behavior')
                if cached:
                    logger.info("Cache hit: analytics/customer_behavior")
                    return cached

            logger.info("Analyzing customer behavior...")
            
            # Orders per customer
            customer_orders = self.orders.groupby('customer_id').agg({
                'order_id': 'count',
                'customer_state': 'first'
            }).rename(columns={'order_id': 'order_count'})
            
            # Customer lifetime value
            customer_value = self.orders.merge(
                self.payments.groupby('order_id')['payment_value'].sum().reset_index(),
                on='order_id',
                how='left'
            ).groupby('customer_id')['payment_value'].sum()
            
            analysis = {
                "total_customers": len(self.customers),
                "active_customers": len(customer_orders),
                "average_orders_per_customer": customer_orders['order_count'].mean(),
                "repeat_customer_rate": (customer_orders['order_count'] > 1).mean() * 100,
                "average_customer_lifetime_value": customer_value.mean(),
                "customers_by_state": customer_orders.groupby('customer_state').size().to_dict(),
                "top_spending_customers": customer_value.nlargest(10).to_dict()
            }
            
            logger.info(f"Customer analysis completed: {analysis['active_customers']} active customers")

            if self.feature_store:
                self.feature_store.set('analytics', 'customer_behavior', analysis, ttl=3600)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing customer behavior: {str(e)}")
            raise
    
    def forecast_demand(self, product_id: Optional[str] = None, periods: int = 30) -> Dict:
        """Forecast demand for products"""
        try:
            logger.info(f"Forecasting demand for {periods} periods...")
            
            # Prepare time series data
            if product_id:
                product_sales = self.order_items[
                    self.order_items['product_id'] == product_id
                ].merge(self.orders[['order_id', 'order_purchase_timestamp']], on='order_id')
            else:
                product_sales = self.order_items.merge(
                    self.orders[['order_id', 'order_purchase_timestamp']], 
                    on='order_id'
                )
            
            # Group by date
            product_sales['date'] = pd.to_datetime(product_sales['order_purchase_timestamp']).dt.date
            daily_sales = product_sales.groupby('date').size().reset_index(name='quantity')
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])
            daily_sales = daily_sales.sort_values('date')
            
            # Create time-based features
            daily_sales['days_since_start'] = (daily_sales['date'] - daily_sales['date'].min()).dt.days
            
            # Simple linear regression forecast
            X = daily_sales[['days_since_start']].values
            y = daily_sales['quantity'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future periods
            last_day = daily_sales['days_since_start'].max()
            future_days = np.array([[last_day + i] for i in range(1, periods + 1)])
            predictions = model.predict(future_days)
            
            # Calculate error metrics
            y_pred_train = model.predict(X)
            mape = mean_absolute_percentage_error(y, y_pred_train) * 100
            rmse = np.sqrt(mean_squared_error(y, y_pred_train))
            
            forecast_dates = [daily_sales['date'].max() + timedelta(days=i) for i in range(1, periods + 1)]
            
            analysis = {
                "product_id": product_id if product_id else "all_products",
                "forecast_periods": periods,
                "historical_average": daily_sales['quantity'].mean(),
                "forecast": {str(date): float(max(0, pred)) for date, pred in zip(forecast_dates, predictions)},
                "model_metrics": {
                    "mape": float(mape),
                    "rmse": float(rmse),
                    "r_squared": float(model.score(X, y))
                },
                "trend": "increasing" if model.coef_[0] > 0 else "decreasing"
            }
            
            logger.info(f"Demand forecast completed with MAPE: {mape:.2f}%")
            return analysis
            
        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            raise
    
    def detect_inventory_risks(self, inventory_data: pd.DataFrame, 
                              low_stock_threshold: int = 100) -> Dict:
        """Detect inventory-related risks"""
        try:
            logger.info("Detecting inventory risks...")
            
            # Low stock items
            low_stock = inventory_data[
                inventory_data['current_stock'] < low_stock_threshold
            ]
            
            # Items below reorder level
            below_reorder = inventory_data[
                inventory_data['current_stock'] < inventory_data['reorder_level']
            ]
            
            analysis = {
                "total_products": len(inventory_data),
                "low_stock_items": len(low_stock),
                "items_below_reorder_level": len(below_reorder),
                "risk_products": low_stock['product_id'].tolist(),
                "warehouse_distribution": inventory_data.groupby('warehouse_location')['current_stock'].sum().to_dict(),
                "recommendations": []
            }
            
            if len(below_reorder) > 0:
                analysis["recommendations"].append(
                    f"Immediate action required: {len(below_reorder)} items below reorder level"
                )
            
            logger.info(f"Inventory risk analysis completed: {len(low_stock)} low stock items")
            return analysis
            
        except Exception as e:
            logger.error(f"Error detecting inventory risks: {str(e)}")
            raise
    
    def analyze_supplier_performance(self, supplier_data: pd.DataFrame) -> Dict:
        """Analyze supplier performance metrics"""
        try:
            logger.info("Analyzing supplier performance...")
            
            # Top performing suppliers
            top_suppliers = supplier_data.nlargest(5, 'on_time_delivery_rate')
            
            # Underperforming suppliers
            poor_suppliers = supplier_data[
                supplier_data['on_time_delivery_rate'] < 0.85
            ]
            
            analysis = {
                "total_suppliers": len(supplier_data),
                "average_on_time_delivery": supplier_data['on_time_delivery_rate'].mean() * 100,
                "average_quality_rating": supplier_data['quality_rating'].mean(),
                "average_lead_time": supplier_data['average_lead_time_days'].mean(),
                "top_suppliers": top_suppliers[['supplier_id', 'supplier_name', 'on_time_delivery_rate']].to_dict('records'),
                "underperforming_suppliers": len(poor_suppliers),
                "suppliers_by_location": supplier_data.groupby('location').size().to_dict()
            }
            
            logger.info(f"Supplier analysis completed: {analysis['total_suppliers']} suppliers analyzed")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing supplier performance: {str(e)}")
            raise
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate a comprehensive SCM analytics report"""
        try:
            logger.info("Generating comprehensive SCM report...")
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary_statistics": self.data_processor.get_summary_statistics(),
                "delivery_analysis": self.analyze_delivery_delays(),
                "revenue_analysis": self.analyze_revenue_trends(),
                "product_analysis": self.analyze_product_performance(),
                "customer_analysis": self.analyze_customer_behavior()
            }
            
            logger.info("Comprehensive report generation completed")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            raise
