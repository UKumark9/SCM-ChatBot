"""
Main Application File - FIXED for Python 3.14
"""

import sys
from pathlib import Path
import logging
import argparse
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("🚀 SCM Chatbot Starting...")

# Setup SIMPLE logging (no config.dictConfig needed)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    logger.warning("⚠️  GROQ_API_KEY not set!")


class SCMChatbotApp:
    """Main SCM Chatbot Application"""
    
    def __init__(self):
        self.orders = None
        self.customers = None
        self.products = None
        self.order_items = None
        self.payments = None
        self.analytics = None
        
        logger.info("Initializing SCM Chatbot...")
    
    def load_data(self, data_path: str = "train"):
        """Load and preprocess CSV data"""
        logger.info(f"Loading {data_path} data...")
    
        try:
            import pandas as pd
            from datetime import datetime
        
            base_path = Path(f"data/{data_path}")
        
        # Load raw data
            self.customers = pd.read_csv(base_path / "df_Customers.csv")
            self.orders = pd.read_csv(base_path / "df_Orders.csv")
            self.order_items = pd.read_csv(base_path / "df_OrderItems.csv")
            self.payments = pd.read_csv(base_path / "df_Payments.csv")
            self.products = pd.read_csv(base_path / "df_Products.csv")
        
            logger.info(f"✅ Loaded {len(self.customers):,} customers")
            logger.info(f"✅ Loaded {len(self.orders):,} orders")
            logger.info(f"✅ Loaded {len(self.order_items):,} order items")
            logger.info(f"✅ Loaded {len(self.payments):,} payments")
            logger.info(f"✅ Loaded {len(self.products):,} products")
        
        # PROCESS ORDERS DATA
            logger.info("Processing orders data...")
        
        # Convert date columns to datetime
            date_cols = ['order_purchase_timestamp', 'order_approved_at', 
                         'order_delivered_carrier_date', 'order_delivered_customer_date',
                      'order_estimated_delivery_date']
        
            for col in date_cols:
                if col in self.orders.columns:
                    self.orders[col] = pd.to_datetime(self.orders[col], errors='coerce')
        
        # Calculate delay fields
            if 'order_delivered_customer_date' in self.orders.columns and \
            'order_estimated_delivery_date' in self.orders.columns:
            
                self.orders['delay_days'] = (
                    self.orders['order_delivered_customer_date'] - 
                    self.orders['order_estimated_delivery_date']
                ).dt.days
            
            # Mark as delayed if delivered after estimated date
                self.orders['is_delayed'] = self.orders['delay_days'] > 0
            
            # For orders not yet delivered, mark as not delayed
                self.orders['is_delayed'] = self.orders['is_delayed'].fillna(False)
                self.orders['delay_days'] = self.orders['delay_days'].fillna(0)
            else:
            # Fallback: create dummy columns
                self.orders['is_delayed'] = False
                self.orders['delay_days'] = 0
        
        # Add month column for time-based analysis
            if 'order_purchase_timestamp' in self.orders.columns:
                self.orders['order_month'] = self.orders['order_purchase_timestamp'].dt.to_period('M')
        
        # Merge customer state into orders
            if 'customer_id' in self.orders.columns and 'customer_id' in self.customers.columns:
                customer_state_map = self.customers.set_index('customer_id')['customer_state'].to_dict()
                self.orders['customer_state'] = self.orders['customer_id'].map(customer_state_map)
        
            logger.info("✅ Data processing complete")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize_analytics(self):
        """Initialize analytics"""
        logger.info("Initializing analytics...")
    
        try:
            from tools.analytics import SCMAnalytics
        
            class DataWrapper:
                def __init__(self, orders, customers, products, order_items, payments):
                    self.orders = orders
                    self.customers = customers
                    self.products = products
                    self.order_items = order_items
                    self.payments = payments
            
                def get_summary_statistics(self):
                    """Get summary statistics for the report"""
                    return {
                        "total_orders": len(self.orders),
                        "total_customers": len(self.customers),
                        "total_products": len(self.products),
                        "total_order_items": len(self.order_items),
                        "total_payments": len(self.payments),
                        "date_range": {
                            "start": str(self.orders['order_purchase_timestamp'].min()),
                            "end": str(self.orders['order_purchase_timestamp'].max())
                        }
                    }
        
            data_wrapper = DataWrapper(
                self.orders, self.customers, self.products,
                self.order_items, self.payments
            )
        
            self.analytics = SCMAnalytics(data_wrapper)
            logger.info("✅ Analytics initialized")
            return True
        
        except Exception as e:
            logger.error(f"⚠️  Analytics failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def setup(self, data_path: str = "train"):
        """Setup application"""
        if not self.load_data(data_path):
            return False
        
        self.initialize_analytics()
        
        logger.info("✅ Setup complete!")
        return True
    
    def query(self, user_input: str) -> str:
        """Process query"""
        try:
            user_input_lower = user_input.lower()
            
            if not self.analytics:
                return "Analytics not initialized. Please check data loading."
            
            if 'delay' in user_input_lower:
                result = self.analytics.analyze_delivery_delays()
                return f"""📊 Delivery Analysis:
- Total Orders: {result['total_orders']:,}
- Delayed Orders: {result['delayed_orders']:,}
- Delay Rate: {result['delay_rate_percentage']:.2f}%
- Average Delay: {result['average_delay_days']:.1f} days"""
            
            elif 'revenue' in user_input_lower:
                result = self.analytics.analyze_revenue_trends()
                return f"""💰 Revenue Analysis:
- Total Revenue: ${result['total_revenue']:,.2f}
- Average Order Value: ${result['average_order_value']:.2f}
- Monthly Growth: {result['average_monthly_growth_rate']:.2f}%"""
            
            elif 'forecast' in user_input_lower or 'demand' in user_input_lower:
                result = self.analytics.forecast_demand(periods=30)
                return f"""📈 Demand Forecast (30 days):
- Historical Avg: {result['historical_average']:.1f} items/day
- MAPE: {result['model_metrics']['mape']:.2f}%
- Trend: {result['trend']}
- R²: {result['model_metrics']['r_squared']:.3f}"""
            
            elif 'product' in user_input_lower:
                result = self.analytics.analyze_product_performance()
                return f"""📦 Product Analysis:
- Unique Products: {result['total_unique_products']:,}
- Total Items Sold: {result['total_items_sold']:,}
- Average Price: ${result['average_product_price']:.2f}"""
            
            elif 'customer' in user_input_lower:
                result = self.analytics.analyze_customer_behavior()
                return f"""👥 Customer Analysis:
- Total Customers: {result['total_customers']:,}
- Active Customers: {result['active_customers']:,}
- Avg Orders/Customer: {result['average_orders_per_customer']:.2f}
- Repeat Rate: {result['repeat_customer_rate']:.1f}%"""
            
            elif 'report' in user_input_lower or 'comprehensive' in user_input_lower:
                result = self.analytics.generate_comprehensive_report()
                return f"""📋 Comprehensive SCM Report

DELIVERY PERFORMANCE:
- Delay Rate: {result['delivery_analysis']['delay_rate_percentage']:.2f}%
- Avg Delay: {result['delivery_analysis']['average_delay_days']:.1f} days

REVENUE METRICS:
- Total Revenue: ${result['revenue_analysis']['total_revenue']:,.2f}
- Avg Order Value: ${result['revenue_analysis']['average_order_value']:.2f}

PRODUCTS:
- Unique Products: {result['product_analysis']['total_unique_products']:,}
- Total Sold: {result['product_analysis']['total_items_sold']:,}

CUSTOMERS:
- Active Customers: {result['customer_analysis']['active_customers']:,}
- Repeat Rate: {result['customer_analysis']['repeat_customer_rate']:.1f}%"""
            
            else:
                return """🤖 I can help with:

📊 Delivery Analysis - "What is the delivery delay rate?"
💰 Revenue Trends - "Show me revenue analysis"  
📈 Demand Forecast - "Forecast demand for 30 days"
📦 Product Performance - "Analyze product performance"
👥 Customer Behavior - "Analyze customer behavior"
📋 Full Report - "Generate comprehensive report"

What would you like to know?"""
                
        except Exception as e:
            logger.error(f"Query error: {e}")
            return f"❌ Error: {str(e)}"
    
    def run_cli(self):
        """CLI mode"""
        print("\n" + "="*60)
        print("🤖 SCM Chatbot - Interactive CLI")
        print("="*60)
        print("\nType 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("\n🧑 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                response = self.query(user_input)
                print(f"\n🤖 Bot:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
    
    def run_ui(self):
        """Gradio UI"""
        try:
            import gradio as gr
            
            def chat(message, history):
                return self.query(message)
            
            demo = gr.ChatInterface(
                fn=chat,
                title="🤖 SCM Intelligent Chatbot",
                description="Ask questions about your supply chain data",
                examples=[
                    "What is the delivery delay rate?",
                    "Show me revenue trends",
                    "Forecast demand for next 30 days",
                    "Analyze product performance",
                    "Generate a comprehensive report"
                ],
            )
            
            print("\n" + "="*60)
            print("🌐 Starting Web Interface...")
            print("="*60)
            print("\n📱 Open: http://localhost:7860")
            print("🛑 Press Ctrl+C to stop\n")
            
            demo.launch(server_port=7860, share=False)
            
        except Exception as e:
            logger.error(f"UI error: {e}")
            print("\n❌ UI failed. Try CLI: python main.py --mode cli")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SCM Chatbot')
    parser.add_argument('--mode', choices=['cli', 'ui'], default='ui',
                       help='cli or ui (default: ui)')
    parser.add_argument('--data', choices=['train', 'test'], default='train',
                       help='train or test (default: train)')
    
    args = parser.parse_args()
    
    app = SCMChatbotApp()
    
    if not app.setup(data_path=args.data):
        print("\n❌ Setup failed!")
        return
    
    if args.mode == 'cli':
        app.run_cli()
    else:
        app.run_ui()


if __name__ == "__main__":
    main()