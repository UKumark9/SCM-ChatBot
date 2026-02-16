"""
Analytics Agent - Specialized agent for revenue and performance analytics
Part of the SCM Chatbot Agentic Architecture
"""

import logging
import io
import base64
from typing import Dict, Any, Optional
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ui_formatter import UIFormatter

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

CRITICAL: Determine if the user is asking about:
1. **POLICY/PROCEDURES** (guidelines, definitions, classifications, protocols, processes)
   → If the input contains "Context from documents:", USE THAT CONTEXT to answer
   → DO NOT query database tools for policy questions
   → Extract and present the information from the provided document context

2. **DATA/STATISTICS** (actual revenue, sales, customer counts, performance metrics)
   → Use the available tools to query real operational data

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
- "What is the policy for X?" → Use the document context if provided

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

    # ── Chart generation ──────────────────────────────────────────────────────

    def _generate_chart_base64(self, fig) -> Optional[str]:
        """Encode a matplotlib figure to base64 PNG string."""
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return encoded
        except Exception as e:
            logger.error(f"Chart encoding error: {e}")
            plt.close(fig)
            return None

    def _chart_revenue(self) -> Optional[str]:
        """Monthly revenue line chart."""
        try:
            result = self.analytics.analyze_revenue_trends()
            monthly = result.get('monthly_revenue', {})
            if not monthly:
                return None

            labels = sorted(monthly.keys())
            values = [monthly[k] / 1000 for k in labels]  # convert to thousands

            fig, ax = plt.subplots(figsize=(9, 3.8))
            fig.patch.set_facecolor('#1e293b')
            ax.set_facecolor('#0f172a')

            ax.plot(range(len(labels)), values, color='#6366f1', linewidth=2.2,
                    marker='o', markersize=4, markerfacecolor='#818cf8')
            ax.fill_between(range(len(labels)), values, alpha=0.15, color='#6366f1')

            # x-axis labels — show every 3rd to avoid crowding
            step = max(1, len(labels) // 8)
            ax.set_xticks(range(0, len(labels), step))
            ax.set_xticklabels([labels[i] for i in range(0, len(labels), step)],
                               rotation=35, ha='right', fontsize=7.5, color='#94a3b8')
            ax.tick_params(axis='y', labelcolor='#94a3b8', labelsize=8)
            ax.set_ylabel('Revenue (K $)', color='#94a3b8', fontsize=8.5)
            ax.set_title('Monthly Revenue', color='#e2e8f0', fontsize=10, fontweight='bold', pad=8)
            ax.spines[:].set_color('#334155')
            ax.grid(axis='y', color='#334155', alpha=0.5, linewidth=0.6)
            ax.tick_params(colors='#475569')
            fig.tight_layout()
            return self._generate_chart_base64(fig)
        except Exception as e:
            logger.error(f"Revenue chart error: {e}")
            return None

    def _chart_products(self) -> Optional[str]:
        """Top product categories horizontal bar chart."""
        try:
            result = self.analytics.analyze_product_performance()
            cat_perf = result.get('category_performance', {})
            price_data = cat_perf.get('price', {})
            if not price_data:
                return None

            # Sort and take top 10
            sorted_cats = sorted(price_data.items(), key=lambda x: x[1], reverse=True)[:10]
            labels = [str(k)[:22] for k, _ in sorted_cats]
            values = [v / 1000 for _, v in sorted_cats]

            fig, ax = plt.subplots(figsize=(9, 4.2))
            fig.patch.set_facecolor('#1e293b')
            ax.set_facecolor('#0f172a')

            bars = ax.barh(range(len(labels)), values, color='#6366f1', height=0.65)
            # Gradient-like effect: lighter shade on top bar
            if bars:
                bars[0].set_color('#818cf8')

            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels[::-1] if False else labels,
                               fontsize=7.5, color='#94a3b8')
            ax.invert_yaxis()
            ax.tick_params(axis='x', labelcolor='#94a3b8', labelsize=8)
            ax.set_xlabel('Revenue (K $)', color='#94a3b8', fontsize=8.5)
            ax.set_title('Top Categories by Revenue', color='#e2e8f0',
                         fontsize=10, fontweight='bold', pad=8)
            ax.spines[:].set_color('#334155')
            ax.grid(axis='x', color='#334155', alpha=0.5, linewidth=0.6)
            fig.tight_layout()
            return self._generate_chart_base64(fig)
        except Exception as e:
            logger.error(f"Products chart error: {e}")
            return None

    def _chart_customers(self) -> Optional[str]:
        """Customers by state bar chart."""
        try:
            result = self.analytics.analyze_customer_behavior()
            by_state = result.get('customers_by_state', {})
            if not by_state:
                return None

            sorted_states = sorted(by_state.items(), key=lambda x: x[1], reverse=True)[:12]
            labels = [str(k) for k, _ in sorted_states]
            values = [v for _, v in sorted_states]

            fig, ax = plt.subplots(figsize=(9, 3.8))
            fig.patch.set_facecolor('#1e293b')
            ax.set_facecolor('#0f172a')

            bar_colors = ['#818cf8' if i == 0 else '#6366f1' for i in range(len(labels))]
            ax.bar(range(len(labels)), values, color=bar_colors, width=0.65)

            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize=8, color='#94a3b8')
            ax.tick_params(axis='y', labelcolor='#94a3b8', labelsize=8)
            ax.set_ylabel('Customers', color='#94a3b8', fontsize=8.5)
            ax.set_title('Customers by State', color='#e2e8f0',
                         fontsize=10, fontweight='bold', pad=8)
            ax.spines[:].set_color('#334155')
            ax.grid(axis='y', color='#334155', alpha=0.5, linewidth=0.6)
            fig.tight_layout()
            return self._generate_chart_base64(fig)
        except Exception as e:
            logger.error(f"Customers chart error: {e}")
            return None

    def _get_chart_for_query(self, query_lower: str) -> Optional[str]:
        """Return appropriate chart based on query keywords."""
        if any(w in query_lower for w in ['product', 'item', 'inventory', 'category']):
            return self._chart_products()
        elif any(w in query_lower for w in ['customer', 'buyer', 'client', 'state']):
            return self._chart_customers()
        else:
            return self._chart_revenue()

    def query(self, user_query: str, classification: Dict = None) -> Dict[str, Any]:
        """Process analytics query"""
        try:
            # Determine if should use RAG based on classification
            should_use_rag = classification.get('use_rag', True) if classification else True
            should_use_database = classification.get('use_database', True) if classification else True

            logger.info(f"Analytics Agent - Use RAG: {should_use_rag} | Use Database: {should_use_database}")

            # Try RAG context retrieval if classification allows it
            rag_context = None
            used_rag = False
            if self.rag_module and should_use_rag:
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

                # Generate chart for data queries (skip for policy-only)
                chart_b64 = None
                is_policy = classification and classification.get('query_type') == 'policy'
                if not is_policy and should_use_database:
                    chart_b64 = self._get_chart_for_query(user_query.lower())

                return {
                    'response': response['output'],
                    'chart_base64': chart_b64,
                    'agent': 'Analytics Agent (LangChain)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

            # Fallback to rule-based
            else:
                query_lower = user_query.lower()

                # NEW: If classification says this is a POLICY ONLY question
                if classification and classification.get('query_type') == 'policy':
                    if used_rag and rag_context and len(rag_context.strip()) > 20:
                        response = UIFormatter.synthesize_rag_response(user_query, rag_context, self.llm_client)

                        return {
                            'response': response,
                            'chart_base64': None,
                            'agent': 'Analytics Agent (Rule-Based) + RAG',
                            'success': True,
                            'used_rag': True,
                            'classification': classification
                        }
                    else:
                        return {
                            'response': "No policy documents found for this query. Please rephrase or ask a data question.",
                            'chart_base64': None,
                            'agent': 'Analytics Agent (Rule-Based)',
                            'success': True,
                            'used_rag': False,
                            'classification': classification
                        }

                # NEW: If classification says this is DATA ONLY or default - skip policy check
                # Data/statistics queries
                if any(word in query_lower for word in ['product', 'item', 'inventory']):
                    response = self._get_product_performance()
                elif any(word in query_lower for word in ['customer', 'buyer', 'client']):
                    response = self._get_customer_behavior()
                else:
                    response = self._get_revenue_analysis()

                # Generate chart for data queries
                chart_b64 = self._get_chart_for_query(query_lower)

                # Append RAG context only if classification allows it (mixed queries)
                if used_rag and should_use_rag and rag_context and len(rag_context.strip()) > 20 and "no relevant" not in rag_context.lower():
                    # Only append if this is a mixed query (both RAG and database)
                    if classification and classification.get('query_type') == 'mixed':
                        # Use UIFormatter for better RAG context formatting
                        formatted_rag = UIFormatter.format_rag_context(rag_context)
                        response += f"\n\n{formatted_rag}"

                return {
                    'response': response,
                    'chart_base64': chart_b64,
                    'agent': 'Analytics Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag,
                    'classification': classification
                }

        except Exception as e:
            logger.error(f"Analytics Agent error: {e}")
            return {
                'response': f"Error processing analytics query: {e}",
                'agent': 'Analytics Agent',
                'success': False,
                'used_rag': False
            }
