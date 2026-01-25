"""
LangChain Agent Orchestrator
Coordinates specialized agents and tools for SCM queries
"""

import logging
from typing import Dict, List, Optional, Any
import json

try:
    from langchain_core.tools import Tool
    from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda
    from langchain_groq import ChatGroq
except ImportError:
    logging.warning("LangChain not installed")

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple specialized agents for SCM operations"""
    
    def __init__(self, llm, analytics_engine, rag_module, inventory_data=None, supplier_data=None):
        self.llm = llm
        self.analytics = analytics_engine
        self.rag = rag_module
        self.inventory_data = inventory_data
        self.supplier_data = supplier_data
        self.tools = self._create_tools()
        self.conversation_history = []
    
    def _create_tools(self) -> List[Tool]:
        """Create specialized tools for different SCM tasks"""
        tools = [
            Tool(
                name="DeliveryDelayAnalysis",
                func=self._delay_analysis_tool,
                description="""Use this tool to analyze delivery delays and performance.
                Input should be a question about delays, late deliveries, or delivery performance.
                Returns statistics about delayed orders, delay rates, and patterns."""
            ),
            Tool(
                name="RevenueAnalysis",
                func=self._revenue_analysis_tool,
                description="""Use this tool for revenue and sales analysis.
                Input should be a question about sales, revenue, or financial performance.
                Returns revenue statistics, trends, and growth rates."""
            ),
            Tool(
                name="ProductPerformance",
                func=self._product_performance_tool,
                description="""Use this tool to analyze product sales and performance.
                Input should be a question about products, categories, or best sellers.
                Returns product sales data, top products, and category performance."""
            ),
            Tool(
                name="CustomerAnalysis",
                func=self._customer_analysis_tool,
                description="""Use this tool for customer behavior analysis.
                Input should be a question about customers, ordering patterns, or customer value.
                Returns customer statistics and behavior patterns."""
            ),
            Tool(
                name="DemandForecast",
                func=self._demand_forecast_tool,
                description="""Use this tool to forecast future demand.
                Input should be a question about future sales, demand prediction, or forecasting.
                Returns demand forecast with predictions and confidence metrics."""
            ),
            Tool(
                name="InventoryRiskAssessment",
                func=self._inventory_risk_tool,
                description="""Use this tool to assess inventory risks.
                Input should be a question about stock levels, inventory risks, or out-of-stock items.
                Returns inventory risk assessment and recommendations."""
            ),
            Tool(
                name="SupplierPerformance",
                func=self._supplier_performance_tool,
                description="""Use this tool to evaluate supplier performance.
                Input should be a question about suppliers, delivery performance, or supplier quality.
                Returns supplier performance metrics and rankings."""
            ),
            Tool(
                name="RAGSearch",
                func=self._rag_search_tool,
                description="""Use this tool to search the supply chain knowledge base.
                Input should be a specific question about orders, products, or historical data.
                Returns relevant information from the database."""
            ),
            Tool(
                name="ComprehensiveReport",
                func=self._comprehensive_report_tool,
                description="""Use this tool to generate a comprehensive SCM report.
                Input should be a request for overall summary or comprehensive analysis.
                Returns a complete report with all key metrics."""
            )
        ]
        
        return tools
    
    def _delay_analysis_tool(self, query: str) -> str:
        """Tool for delivery delay analysis"""
        try:
            result = self.analytics.analyze_delivery_delays()
            
            response = f"""
📊 DELIVERY DELAY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Orders: {result['total_orders']:,}
Delayed Orders: {result['delayed_orders']:,}
Delay Rate: {result['delay_rate_percentage']:.2f}%
Average Delay: {result['average_delay_days']:.2f} days
Maximum Delay: {result['max_delay_days']:.2f} days
Median Delay: {result['median_delay_days']:.2f} days

Key Insights:
- {'🔴 High delay rate - requires attention' if result['delay_rate_percentage'] > 50 else '🟢 Acceptable delay rate'}
- Top delayed states: {', '.join(list(result['delays_by_state'].keys())[:3])}
"""
            return response
        except Exception as e:
            logger.error(f"Error in delay analysis tool: {str(e)}")
            return f"Error analyzing delays: {str(e)}"
    
    def _revenue_analysis_tool(self, query: str) -> str:
        """Tool for revenue analysis"""
        try:
            result = self.analytics.analyze_revenue_trends()
            
            response = f"""
💰 REVENUE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Revenue: ${result['total_revenue']:,.2f}
Average Order Value: ${result['average_order_value']:.2f}
Average Monthly Growth: {result['average_monthly_growth_rate']:.2f}%

Performance Highlights:
- Best Month: {result['highest_revenue_month']}
- Weakest Month: {result['lowest_revenue_month']}
- Growth Trend: {'📈 Positive' if result['average_monthly_growth_rate'] > 0 else '📉 Negative'}

Top Revenue States: {', '.join(list(result['revenue_by_state'].keys())[:3])}
"""
            return response
        except Exception as e:
            logger.error(f"Error in revenue analysis tool: {str(e)}")
            return f"Error analyzing revenue: {str(e)}"
    
    def _product_performance_tool(self, query: str) -> str:
        """Tool for product performance analysis"""
        try:
            result = self.analytics.analyze_product_performance()
            
            response = f"""
📦 PRODUCT PERFORMANCE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Unique Products: {result['total_unique_products']:,}
Total Items Sold: {result['total_items_sold']:,}
Average Product Price: ${result['average_product_price']:.2f}

Market Insights:
- Wide product variety across multiple categories
- Strong sales performance across the board
"""
            return response
        except Exception as e:
            logger.error(f"Error in product analysis tool: {str(e)}")
            return f"Error analyzing products: {str(e)}"
    
    def _customer_analysis_tool(self, query: str) -> str:
        """Tool for customer behavior analysis"""
        try:
            result = self.analytics.analyze_customer_behavior()
            
            response = f"""
👥 CUSTOMER BEHAVIOR ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Customers: {result['total_customers']:,}
Active Customers: {result['active_customers']:,}
Avg Orders per Customer: {result['average_orders_per_customer']:.2f}
Repeat Customer Rate: {result['repeat_customer_rate']:.2f}%
Avg Customer Lifetime Value: ${result['average_customer_lifetime_value']:.2f}

Customer Insights:
- {'🟢 Strong repeat purchase rate' if result['repeat_customer_rate'] > 30 else '🟡 Moderate repeat rate'}
- Geographic distribution across multiple states
"""
            return response
        except Exception as e:
            logger.error(f"Error in customer analysis tool: {str(e)}")
            return f"Error analyzing customers: {str(e)}"
    
    def _demand_forecast_tool(self, query: str) -> str:
        """Tool for demand forecasting"""
        try:
            result = self.analytics.forecast_demand(periods=30)
            
            # Get next 7 days forecast for display
            forecast_items = list(result['forecast'].items())[:7]
            forecast_display = '\n'.join([f"  {date}: {qty:.0f} units" 
                                        for date, qty in forecast_items])
            
            response = f"""
📈 DEMAND FORECAST (Next 30 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Forecast Period: {result['forecast_periods']} days
Historical Average: {result['historical_average']:.2f} units/day
Trend: {result['trend'].upper()}

Model Performance:
- MAPE: {result['model_metrics']['mape']:.2f}%
- RMSE: {result['model_metrics']['rmse']:.2f}
- R²: {result['model_metrics']['r_squared']:.4f}

Next 7 Days Forecast:
{forecast_display}

Recommendation: {'📊 Plan for increased demand' if result['trend'] == 'increasing' else '📉 Optimize inventory levels'}
"""
            return response
        except Exception as e:
            logger.error(f"Error in demand forecast tool: {str(e)}")
            return f"Error forecasting demand: {str(e)}"
    
    def _inventory_risk_tool(self, query: str) -> str:
        """Tool for inventory risk assessment"""
        try:
            if self.inventory_data is None:
                return "Inventory data not available. Please load inventory data first."
            
            result = self.analytics.detect_inventory_risks(self.inventory_data)
            
            response = f"""
⚠️ INVENTORY RISK ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Products: {result['total_products']:,}
Low Stock Items: {result['low_stock_items']:,}
Below Reorder Level: {result['items_below_reorder_level']:,}

Risk Status: {'🔴 HIGH RISK' if result['items_below_reorder_level'] > 10 else '🟢 LOW RISK'}

Recommendations:
{chr(10).join(['• ' + rec for rec in result['recommendations']])}

Warehouse Distribution: {result['warehouse_distribution']}
"""
            return response
        except Exception as e:
            logger.error(f"Error in inventory risk tool: {str(e)}")
            return f"Error assessing inventory: {str(e)}"
    
    def _supplier_performance_tool(self, query: str) -> str:
        """Tool for supplier performance evaluation"""
        try:
            if self.supplier_data is None:
                return "Supplier data not available. Please load supplier data first."
            
            result = self.analytics.analyze_supplier_performance(self.supplier_data)
            
            top_suppliers_text = '\n'.join([
                f"  {i+1}. {sup['supplier_name']}: {sup['on_time_delivery_rate']*100:.1f}% on-time"
                for i, sup in enumerate(result['top_suppliers'])
            ])
            
            response = f"""
🏭 SUPPLIER PERFORMANCE EVALUATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Suppliers: {result['total_suppliers']}
Avg On-Time Delivery: {result['average_on_time_delivery']:.2f}%
Avg Quality Rating: {result['average_quality_rating']:.2f}/5.0
Avg Lead Time: {result['average_lead_time']:.2f} days

Top Performing Suppliers:
{top_suppliers_text}

Underperforming: {result['underperforming_suppliers']} suppliers need attention

Status: {'🟢 Overall good performance' if result['average_on_time_delivery'] > 85 else '🟡 Room for improvement'}
"""
            return response
        except Exception as e:
            logger.error(f"Error in supplier performance tool: {str(e)}")
            return f"Error analyzing suppliers: {str(e)}"
    
    def _rag_search_tool(self, query: str) -> str:
        """Tool for RAG-based knowledge base search"""
        try:
            context = self.rag.retrieve_context(query)
            
            if "No relevant context found" in context:
                return "I couldn't find specific information about that in the database. Please try rephrasing your question or ask about general statistics."
            
            # Use LLM to generate a natural response from the context
            prompt = f"""Based on the following information from the supply chain database, 
            answer the user's question concisely and accurately.

Context:
{context}

Question: {query}

Answer:"""
            
            try:
                response = self.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            except:
                # Fallback to returning context directly
                return f"Retrieved Information:\n{context}"
                
        except Exception as e:
            logger.error(f"Error in RAG search tool: {str(e)}")
            return f"Error searching knowledge base: {str(e)}"
    
    def _comprehensive_report_tool(self, query: str) -> str:
        """Tool for generating comprehensive reports"""
        try:
            report = self.analytics.generate_comprehensive_report()
            
            response = f"""
📋 COMPREHENSIVE SCM REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {report['generated_at']}

SUMMARY STATISTICS
• Total Customers: {report['summary_statistics']['total_customers']:,}
• Total Orders: {report['summary_statistics']['total_orders']:,}
• Total Revenue: ${report['summary_statistics']['total_revenue']:,.2f}
• Delay Rate: {report['summary_statistics']['delay_rate']:.2f}%

DELIVERY PERFORMANCE
• Delayed Orders: {report['delivery_analysis']['delayed_orders']:,}
• Average Delay: {report['delivery_analysis']['average_delay_days']:.2f} days

FINANCIAL PERFORMANCE  
• Average Order Value: ${report['revenue_analysis']['average_order_value']:.2f}
• Monthly Growth: {report['revenue_analysis']['average_monthly_growth_rate']:.2f}%

CUSTOMER INSIGHTS
• Active Customers: {report['customer_analysis']['active_customers']:,}
• Repeat Rate: {report['customer_analysis']['repeat_customer_rate']:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            return response
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            return f"Error generating report: {str(e)}"
    
    def route_query(self, query: str) -> str:
        """Route query to appropriate tool based on content"""
        try:
            query_lower = query.lower()
            
            # Simple keyword-based routing
            if any(word in query_lower for word in ['delay', 'late', 'delivery time', 'shipping']):
                return self._delay_analysis_tool(query)
            elif any(word in query_lower for word in ['revenue', 'sales', 'money', 'profit', 'financial']):
                return self._revenue_analysis_tool(query)
            elif any(word in query_lower for word in ['product', 'item', 'category', 'best seller']):
                return self._product_performance_tool(query)
            elif any(word in query_lower for word in ['customer', 'buyer', 'client', 'repeat']):
                return self._customer_analysis_tool(query)
            elif any(word in query_lower for word in ['forecast', 'predict', 'future', 'demand']):
                return self._demand_forecast_tool(query)
            elif any(word in query_lower for word in ['inventory', 'stock', 'warehouse', 'storage']):
                return self._inventory_risk_tool(query)
            elif any(word in query_lower for word in ['supplier', 'vendor', 'provider']):
                return self._supplier_performance_tool(query)
            elif any(word in query_lower for word in ['report', 'summary', 'overview', 'comprehensive']):
                return self._comprehensive_report_tool(query)
            else:
                # Default to RAG search for specific queries
                return self._rag_search_tool(query)
                
        except Exception as e:
            logger.error(f"Error routing query: {str(e)}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def process_query(self, query: str) -> str:
        """Process a user query and return response"""
        try:
            logger.info(f"Processing query: {query}")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": query})
            
            # Route and process query
            response = self.route_query(query)
            
            # Add response to history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep only last 10 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
