"""
Analytics Agent - Specialized agent for revenue and performance analytics
Part of the SCM Chatbot Agentic Architecture
"""

import logging
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from langchain_groq import ChatGroq
    from langchain_core.tools import Tool
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available for Analytics Agent")


class AnalyticsAgent:
    """Specialized agent for revenue and performance analytics"""

    def __init__(self, analytics_engine, llm_client=None, use_langchain: bool = True, rag_module=None):
        """
        Initialize Analytics Agent

        Args:
            analytics_engine: SCMAnalytics instance
            llm_client: LLM client
            use_langchain: Whether to use LangChain framework
            rag_module: RAG module for semantic search (optional)
        """
        self.analytics = analytics_engine
        self.llm_client = llm_client
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.rag_module = rag_module
        self.agent_executor = None

        if self.use_langchain and llm_client:
            self._initialize_langchain_agent()

        logger.info(f"Analytics Agent initialized (LangChain: {self.use_langchain}, RAG: {rag_module is not None})")

    def _initialize_langchain_agent(self):
        """Initialize LangChain agent"""
        try:
            tools = [
                Tool(
                    name="GetRevenueAnalysis",
                    func=self._get_revenue_analysis,
                    description="Get revenue statistics including total revenue, average order value, and growth rate"
                ),
                Tool(
                    name="GetProductPerformance",
                    func=self._get_product_performance,
                    description="Get product performance metrics including top products and sales volumes"
                ),
                Tool(
                    name="GetCustomerBehavior",
                    func=self._get_customer_behavior,
                    description="Get customer behavior analysis including repeat rate and lifetime value"
                ),
            ]

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Analytics Agent for revenue and performance analysis.
Your expertise is in analyzing sales, products, and customer behavior.

IMPORTANT INSTRUCTIONS:
- Answer ONLY what the user specifically asks for
- Be concise and direct - don't provide extra information unless requested
- If asked for one metric (e.g., "total revenue"), provide ONLY that metric
- If asked for "analysis" or "statistics", provide comprehensive details
- Always include specific numbers with proper context

RESPONSE GUIDELINES:
- "What is total revenue?" → Answer with just the total revenue
- "Show revenue analysis" → Provide comprehensive revenue statistics
- "How many customers?" → Answer with just the count
- "Analyze customer behavior" → Provide detailed customer insights

Extract only the relevant information from tool results to answer the specific question."""),
                ("human", "{input}"),
            ])

            agent = create_tool_calling_agent(self.llm_client, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True
            )

            logger.info("Analytics Agent LangChain executor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Analytics agent: {e}")
            self.use_langchain = False

    def _get_revenue_analysis(self, query: str = "") -> str:
        """Get revenue analysis"""
        try:
            result = self.analytics.analyze_revenue_trends()
            return f"""Revenue Analysis:
- Total Revenue: ${result['total_revenue']:,.2f}
- Average Order Value: ${result['average_order_value']:.2f}
- Monthly Growth Rate: {result['average_monthly_growth_rate']:.2f}%
- Highest Revenue Month: {result.get('highest_revenue_month', 'N/A')}
- Lowest Revenue Month: {result.get('lowest_revenue_month', 'N/A')}"""
        except Exception as e:
            return f"Error getting revenue analysis: {e}"

    def _get_product_performance(self, query: str = "") -> str:
        """Get product performance"""
        try:
            result = self.analytics.analyze_product_performance()
            return f"""Product Performance:
- Unique Products: {result['total_unique_products']:,}
- Total Items Sold: {result['total_items_sold']:,}
- Average Product Price: ${result['average_product_price']:.2f}"""
        except Exception as e:
            return f"Error getting product performance: {e}"

    def _get_customer_behavior(self, query: str = "") -> str:
        """Get customer behavior analysis"""
        try:
            result = self.analytics.analyze_customer_behavior()
            return f"""Customer Behavior:
- Total Customers: {result['total_customers']:,}
- Active Customers: {result['active_customers']:,}
- Average Orders per Customer: {result['average_orders_per_customer']:.2f}
- Repeat Customer Rate: {result['repeat_customer_rate']:.1f}%
- Average Customer Lifetime Value: ${result['average_customer_lifetime_value']:.2f}"""
        except Exception as e:
            return f"Error getting customer behavior: {e}"

    def query(self, user_query: str) -> Dict[str, Any]:
        """Process analytics query"""
        try:
            # Try RAG context retrieval first
            rag_context = None
            used_rag = False
            if self.rag_module:
                try:
                    rag_context = self.rag_module.retrieve_context(user_query)
                    if rag_context and len(rag_context.strip()) > 0:
                        used_rag = True
                        logger.info("✅ RAG context retrieved for analytics query")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # If using LangChain agent
            if self.use_langchain and self.agent_executor:
                # Augment query with RAG context if available
                if used_rag:
                    augmented_query = f"Context from documents:\n{rag_context}\n\nUser query: {user_query}"
                else:
                    augmented_query = user_query

                response = self.agent_executor.invoke({"input": augmented_query})
                return {
                    'response': response['output'],
                    'agent': 'Analytics Agent (LangChain)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

            # Fallback to rule-based
            else:
                query_lower = user_query.lower()

                if any(word in query_lower for word in ['product', 'item', 'inventory']):
                    response = self._get_product_performance()
                elif any(word in query_lower for word in ['customer', 'buyer', 'client']):
                    response = self._get_customer_behavior()
                else:
                    response = self._get_revenue_analysis()

                # Append RAG context if available and meaningful
                if used_rag and rag_context and len(rag_context.strip()) > 20 and "no relevant" not in rag_context.lower():
                    response += f"\n\n📚 **Document Context:**\n{rag_context[:400]}"
                    if len(rag_context) > 400:
                        response += "..."

                return {
                    'response': response,
                    'agent': 'Analytics Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

        except Exception as e:
            logger.error(f"Analytics Agent error: {e}")
            return {
                'response': f"Error processing analytics query: {e}",
                'agent': 'Analytics Agent',
                'success': False,
                'used_rag': False
            }
