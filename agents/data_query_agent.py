"""
Data Query Agent - Specialized agent for querying raw data
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
    logger.warning("LangChain not available for Data Query Agent")


class DataQueryAgent:
    """Specialized agent for querying and retrieving specific data records"""

    def __init__(self, data_wrapper, llm_client=None, use_langchain: bool = True, rag_module=None):
        """
        Initialize Data Query Agent

        Args:
            data_wrapper: Object with orders, customers, products dataframes
            llm_client: LLM client
            use_langchain: Whether to use LangChain framework
            rag_module: RAG module for semantic search (optional)
        """
        self.data = data_wrapper
        self.llm_client = llm_client
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.rag_module = rag_module
        self.agent_executor = None

        if self.use_langchain and llm_client:
            self._initialize_langchain_agent()

        logger.info(f"Data Query Agent initialized (LangChain: {self.use_langchain}, RAG: {rag_module is not None})")

    def _initialize_langchain_agent(self):
        """Initialize LangChain agent"""
        try:
            tools = [
                Tool(
                    name="QueryOrders",
                    func=self._query_orders,
                    description="Query order records by ID or filters"
                ),
                Tool(
                    name="QueryCustomers",
                    func=self._query_customers,
                    description="Query customer records by ID or location"
                ),
                Tool(
                    name="QueryProducts",
                    func=self._query_products,
                    description="Query product records by ID or category"
                ),
                Tool(
                    name="GetDataSummary",
                    func=self._get_data_summary,
                    description="Get summary of available data and record counts"
                ),
            ]

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Data Query Agent.
Your expertise is in retrieving specific data records from orders, customers, and products.

Use the available tools to answer specific data queries."""),
                ("human", "{input}"),
            ])

            agent = create_tool_calling_agent(self.llm_client, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True
            )

            logger.info("Data Query Agent LangChain executor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Data Query agent: {e}")
            self.use_langchain = False

    def _query_orders(self, query: str = "") -> str:
        """Query orders data"""
        try:
            total = len(self.data.orders)
            sample = self.data.orders.head(3)
            return f"""Orders Data:
- Total Orders: {total:,}
- Sample Orders:
{sample[['order_id', 'customer_id', 'order_purchase_timestamp']].to_string(index=False) if 'order_id' in sample.columns else 'Columns not found'}"""
        except Exception as e:
            return f"Error querying orders: {e}"

    def _query_customers(self, query: str = "") -> str:
        """Query customers data"""
        try:
            total = len(self.data.customers)
            states = self.data.customers['customer_state'].value_counts().head(5) if 'customer_state' in self.data.customers.columns else None

            response = f"""Customer Data:
- Total Customers: {total:,}"""

            if states is not None:
                response += "\n- Top 5 States:\n"
                for state, count in states.items():
                    response += f"  {state}: {count:,} customers\n"

            return response
        except Exception as e:
            return f"Error querying customers: {e}"

    def _query_products(self, query: str = "") -> str:
        """Query products data"""
        try:
            total = len(self.data.products)
            sample = self.data.products.head(3)
            return f"""Product Data:
- Total Products: {total:,}
- Sample Products:
{sample.to_string(index=False)}"""
        except Exception as e:
            return f"Error querying products: {e}"

    def _get_data_summary(self, query: str = "") -> str:
        """Get data summary"""
        try:
            summary = self.data.get_summary_statistics()
            return f"""Data Summary:
- Total Orders: {summary['total_orders']:,}
- Total Customers: {summary['total_customers']:,}
- Total Products: {summary['total_products']:,}
- Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}"""
        except Exception as e:
            return f"Error getting data summary: {e}"

    def query(self, user_query: str) -> Dict[str, Any]:
        """Process data query"""
        try:
            # Try RAG context retrieval first
            rag_context = None
            used_rag = False
            if self.rag_module:
                try:
                    rag_context = self.rag_module.retrieve_context(user_query)
                    if rag_context and len(rag_context.strip()) > 0:
                        used_rag = True
                        logger.info("✅ RAG context retrieved for data query")
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
                    'agent': 'Data Query Agent (LangChain)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

            # Fallback to rule-based
            else:
                query_lower = user_query.lower()

                if 'order' in query_lower:
                    response = self._query_orders()
                elif 'customer' in query_lower:
                    response = self._query_customers()
                elif 'product' in query_lower:
                    response = self._query_products()
                else:
                    response = self._get_data_summary()

                # Append RAG context if available
                if used_rag:
                    response += f"\n\n📚 **Additional Context from Documents:**\n{rag_context[:500]}..."

                return {
                    'response': response,
                    'agent': 'Data Query Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

        except Exception as e:
            logger.error(f"Data Query Agent error: {e}")
            return {
                'response': f"Error processing data query: {e}",
                'agent': 'Data Query Agent',
                'success': False,
                'used_rag': False
            }
