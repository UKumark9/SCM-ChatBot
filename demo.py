#!/usr/bin/env python3
"""
Quick Start Demo Script
Demonstrates key features of the SCM Chatbot without full setup
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.analytics import (
    DelayAnalytics, RevenueAnalytics, InventoryAnalytics,
    DemandForecasting, SupplierAnalytics
)
from data.data_loader import DataSynthesizer
from agents.scm_agent import SimpleAgent


def create_sample_data():
    """Create sample data for demo"""
    print("📊 Creating sample data...")
    
    # Sample orders
    np.random.seed(42)
    n_orders = 1000
    
    orders = pd.DataFrame({
        'order_id': [f'O{i:04d}' for i in range(n_orders)],
        'customer_id': [f'C{i%500:04d}' for i in range(n_orders)],
        'customer_state': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR'], n_orders),
        'order_status': np.random.choice(['delivered', 'shipped', 'processing'], n_orders, p=[0.8, 0.15, 0.05]),
        'is_delayed': np.random.choice([True, False], n_orders, p=[0.35, 0.65]),
        'delivery_delay_days': np.random.randint(-2, 15, n_orders),
        'order_purchase_timestamp': pd.date_range(start='2024-01-01', periods=n_orders, freq='H')
    })
    
    # Sample order items
    order_items = pd.DataFrame({
        'order_id': [f'O{i:04d}' for i in range(n_orders)],
        'product_id': [f'P{i%200:04d}' for i in range(n_orders)],
        'price': np.random.uniform(20, 500, n_orders).round(2),
        'shipping_charges': np.random.uniform(5, 50, n_orders).round(2)
    })
    
    # Sample products
    products = pd.DataFrame({
        'product_id': [f'P{i:04d}' for i in range(200)],
        'product_category_name': np.random.choice(
            ['electronics', 'furniture', 'books', 'toys', 'clothing'], 200
        ),
        'product_weight_g': np.random.uniform(100, 5000, 200).round(0),
        'product_length_cm': np.random.uniform(10, 100, 200).round(0),
        'product_width_cm': np.random.uniform(10, 100, 200).round(0),
        'product_height_cm': np.random.uniform(5, 50, 200).round(0)
    })
    
    # Generate synthetic data
    suppliers = DataSynthesizer.generate_supplier_data(n_suppliers=50)
    inventory = DataSynthesizer.generate_inventory_data(products)
    
    print("✅ Sample data created")
    return orders, order_items, products, suppliers, inventory


def run_demo():
    """Run interactive demo"""
    print("\n" + "="*60)
    print("🤖 SCM Chatbot - Quick Start Demo")
    print("="*60)
    print("\nThis demo uses sample data to showcase chatbot capabilities.")
    print("For full functionality, run: python main.py\n")
    
    # Create data
    orders, order_items, products, suppliers, inventory = create_sample_data()
    
    # Initialize analytics
    print("\n📈 Initializing analytics modules...")
    analytics_tools = {
        'delay': DelayAnalytics(orders),
        'revenue': RevenueAnalytics(order_items, orders),
        'inventory': InventoryAnalytics(inventory),
        'forecast': DemandForecasting(orders),
        'supplier': SupplierAnalytics(suppliers)
    }
    print("✅ Analytics ready")
    
    # Initialize simple agent
    print("\n🤖 Initializing chatbot agent...")
    agent = SimpleAgent(analytics_tools)
    print("✅ Agent ready")
    
    # Demo queries
    print("\n" + "="*60)
    print("📝 Demo Queries")
    print("="*60)
    
    demo_queries = [
        "What is the delivery delay rate?",
        "Show me revenue statistics",
        "How many products are low in stock?",
        "What's the demand forecast?",
        "Tell me about supplier performance"
    ]
    
    for query in demo_queries:
        print(f"\n🧑 User: {query}")
        response = agent.query(query)
        print(f"🤖 Assistant:\n{response}\n")
        print("-" * 60)
    
    # Interactive mode
    print("\n" + "="*60)
    print("💬 Interactive Mode")
    print("="*60)
    print("\nYou can now ask your own questions!")
    print("Type 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            user_input = input("🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for trying the demo!")
                break
            
            if not user_input:
                continue
            
            response = agent.query(user_input)
            print(f"\n🤖 Assistant:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for trying the demo!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("\nFor full installation, please run: ./setup.sh")
        sys.exit(1)
