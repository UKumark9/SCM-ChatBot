"""
LangChain Agent Orchestrator
Central controller for the SCM chatbot using agentic AI
"""

import logging
from typing import Dict, List, Any
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from langchain_groq import ChatGroq
    from langchain_core.tools import Tool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.messages import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available. Install with: pip install langchain langchain-groq langchain-core")


class SCMAgent:
    """Supply Chain Management Agent with LangChain"""
    
    def __init__(self, config: Dict, analytics_tools: Dict, rag_module: Any = None):
        """
        Initialize SCM Agent
        
        Args:
            config: Configuration dictionary
            analytics_tools: Dictionary of analytics tool instances
            rag_module: RAG module for document retrieval
        """
        self.config = config
        self.analytics_tools = analytics_tools
        self.rag_module = rag_module
        self.chat_history = []
        
        if not LANGCHAIN_AVAILABLE:
            logger.error("LangChain is not available")
            self.agent = None
            self.llm = None
            return
        
        # Initialize LLM
        self.llm = ChatGroq(
            model=config.get('model_name', 'llama3-70b-8192'),
            temperature=config.get('temperature', 0.1),
            api_key=config.get('api_key')
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent_executor = self._create_agent()
        
        logger.info("SCM Agent initialized successfully")
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from analytics modules"""
        tools = []
        
        # Delay Analysis Tool
        if 'delay' in self.analytics_tools:
            tools.append(Tool(
                name="DelayAnalysis",
                func=lambda x: str(self.analytics_tools['delay'].get_delay_summary()),
                description="Get delivery delay statistics including total delayed orders, delay rate, and average delay days. Use this when users ask about delivery delays, late orders, or on-time performance."
            ))
        
        # Revenue Analysis Tool
        if 'revenue' in self.analytics_tools:
            tools.append(Tool(
                name="RevenueAnalysis",
                func=lambda x: str(self.analytics_tools['revenue'].get_revenue_summary()),
                description="Get revenue statistics including total revenue, order count, and average order value. Use this when users ask about sales, revenue, or financial performance."
            ))
        
        # Inventory Analysis Tool
        if 'inventory' in self.analytics_tools:
            tools.append(Tool(
                name="InventoryAnalysis",
                func=lambda x: str(self.analytics_tools['inventory'].get_inventory_summary()),
                description="Get inventory statistics including total products, low stock items, and stock levels. Use this when users ask about inventory, stock levels, or warehouse management."
            ))
        
        # Demand Forecasting Tool
        if 'forecast' in self.analytics_tools:
            tools.append(Tool(
                name="DemandForecast",
                func=lambda x: str(self.analytics_tools['forecast'].forecast_next_n_days(30)),
                description="Get demand forecast for next 30 days including average daily orders. Use this when users ask about future demand, sales predictions, or forecasting."
            ))
        
        # Supplier Analysis Tool
        if 'supplier' in self.analytics_tools:
            tools.append(Tool(
                name="SupplierAnalysis",
                func=lambda x: str(self.analytics_tools['supplier'].get_supplier_summary()),
                description="Get supplier performance statistics including ratings and on-time delivery rates. Use this when users ask about suppliers, vendor performance, or procurement."
            ))
        
        # RAG Retrieval Tool
        if self.rag_module:
            def rag_search(query: str) -> str:
                results = self.rag_module.retrieve(query, top_k=3)
                if results:
                    context = "\n\n".join([r['document']['text'] for r in results[:3]])
                    return f"Retrieved context:\n{context}"
                return "No relevant information found"
            
            tools.append(Tool(
                name="KnowledgeBase",
                func=rag_search,
                description="Search the knowledge base for specific order, product, or customer information. Use this when users ask about specific IDs or need detailed information about orders or products."
            ))
        
        logger.info(f"Created {len(tools)} tools for the agent")
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create LangChain agent with tools"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent Supply Chain Management assistant with expertise in logistics, inventory, and analytics.

You have access to various tools to analyze supply chain data. When users ask questions:
1. Understand the user's intent and determine which tool(s) to use
2. Use the appropriate tools to gather information
3. Synthesize the information into clear, actionable insights
4. Provide specific numbers and metrics when available
5. Be concise but comprehensive in your responses

Available tools:
{tools}

Tool descriptions:
{tool_names}

Always cite specific metrics and data points in your answers. If you don't have enough information, say so clearly.
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.config.get('verbose', True),
            max_iterations=self.config.get('max_iterations', 10),
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def query(self, user_input: str) -> str:
        """
        Process user query through the agent
        
        Args:
            user_input: User's question or request
            
        Returns:
            Agent's response
        """
        if not self.agent_executor:
            return "Error: Agent not initialized. Please install LangChain dependencies."
        
        try:
            # Invoke agent
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=response['output']))
            
            # Limit chat history size
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
            
            return response['output']
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def reset_history(self):
        """Clear chat history"""
        self.chat_history = []
        logger.info("Chat history cleared")


class SimpleAgent:
    """Simplified agent without LangChain dependencies (fallback)"""
    
    def __init__(self, analytics_tools: Dict):
        self.analytics_tools = analytics_tools
        logger.info("Simple agent initialized (fallback mode)")
    
    def query(self, user_input: str) -> str:
        """Simple rule-based query processing"""
        user_input_lower = user_input.lower()
        
        try:
            # Delay queries
            if any(word in user_input_lower for word in ['delay', 'late', 'delivery']):
                if 'delay' in self.analytics_tools:
                    result = self.analytics_tools['delay'].get_delay_summary()
                    return self._format_delay_response(result)
            
            # Revenue queries
            elif any(word in user_input_lower for word in ['revenue', 'sales', 'money', 'earnings']):
                if 'revenue' in self.analytics_tools:
                    result = self.analytics_tools['revenue'].get_revenue_summary()
                    return self._format_revenue_response(result)
            
            # Inventory queries
            elif any(word in user_input_lower for word in ['inventory', 'stock', 'warehouse']):
                if 'inventory' in self.analytics_tools:
                    result = self.analytics_tools['inventory'].get_inventory_summary()
                    return self._format_inventory_response(result)
            
            # Forecast queries
            elif any(word in user_input_lower for word in ['forecast', 'predict', 'future', 'demand']):
                if 'forecast' in self.analytics_tools:
                    result = self.analytics_tools['forecast'].forecast_next_n_days(30)
                    return self._format_forecast_response(result)
            
            # Supplier queries
            elif any(word in user_input_lower for word in ['supplier', 'vendor', 'procurement']):
                if 'supplier' in self.analytics_tools:
                    result = self.analytics_tools['supplier'].get_supplier_summary()
                    return self._format_supplier_response(result)
            
            else:
                return "I can help you with: delays, revenue, inventory, demand forecasting, and supplier analysis. What would you like to know?"
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _format_delay_response(self, data: Dict) -> str:
        return f"""📦 Delivery Delay Analysis:
• Total Orders: {data['total_orders']:,}
• Delayed Orders: {data['delayed_orders']:,}
• On-Time Orders: {data['on_time_orders']:,}
• Delay Rate: {data['delay_rate_percent']}%
• Average Delay: {data['avg_delay_days']} days
• Maximum Delay: {data['max_delay_days']} days"""
    
    def _format_revenue_response(self, data: Dict) -> str:
        return f"""💰 Revenue Analysis:
• Total Revenue: ${data['total_revenue']:,.2f}
• Total Orders: {data['total_orders']:,}
• Average Order Value: ${data['avg_order_value']:,.2f}
• Total Shipping: ${data['total_shipping_charges']:,.2f}
• Net Revenue: ${data['net_revenue']:,.2f}"""
    
    def _format_inventory_response(self, data: Dict) -> str:
        return f"""📊 Inventory Analysis:
• Total Products: {data['total_products']:,}
• Low Stock Items: {data['low_stock_items']:,}
• Low Stock Rate: {data['low_stock_rate_percent']}%
• Average Stock Level: {data['avg_stock_level']:.0f} units
• Total Stock: {data['total_stock_units']:,} units"""
    
    def _format_forecast_response(self, data: Dict) -> str:
        return f"""🔮 Demand Forecast:
• Forecast Period: {data['forecast_period_days']} days
• Average Daily Orders: {data['avg_daily_orders']:.0f}
• Total Forecasted Orders: {data['total_forecasted_orders']:.0f}
• Method: {data['forecast_method']}"""
    
    def _format_supplier_response(self, data: Dict) -> str:
        return f"""🏭 Supplier Analysis:
• Total Suppliers: {data['total_suppliers']:,}
• Average Rating: {data['avg_supplier_rating']:.2f}/5.0
• Average On-Time Rate: {data['avg_on_time_delivery_rate']*100:.1f}%
• Top Rated Suppliers: {data['top_rated_suppliers']:,}"""
