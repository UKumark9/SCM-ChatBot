"""
Delay Agent - Specialized agent for delivery delay analysis
Part of the SCM Chatbot Agentic Architecture
"""

import logging
from typing import Dict, Any, List
import pandas as pd
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
    logger.warning("LangChain not available for Delay Agent")


class DelayAgent:
    """Specialized agent for analyzing delivery delays"""

    def __init__(self, analytics_engine, llm_client=None, use_langchain: bool = True, rag_module=None):
        """
        Initialize Delay Agent

        Args:
            analytics_engine: SCMAnalytics instance
            llm_client: LLM client (Groq or ChatGroq)
            use_langchain: Whether to use LangChain agent framework
            rag_module: RAG module for semantic search (optional)
        """
        self.analytics = analytics_engine
        self.llm_client = llm_client
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.rag_module = rag_module
        self.agent_executor = None

        if self.use_langchain and llm_client:
            self._initialize_langchain_agent()

        logger.info(f"Delay Agent initialized (LangChain: {self.use_langchain}, RAG: {rag_module is not None})")

    def _initialize_langchain_agent(self):
        """Initialize LangChain agent with tools"""
        try:
            # Create specialized tools for delay analysis
            tools = [
                Tool(
                    name="GetDelayStatistics",
                    func=self._get_delay_statistics,
                    description="Get overall delivery delay statistics including delay rate, average delay days, and total delayed orders"
                ),
                Tool(
                    name="GetStateDelays",
                    func=self._get_state_delays,
                    description="Get delivery delays broken down by state/region"
                ),
                Tool(
                    name="GetDelayTrends",
                    func=self._get_delay_trends,
                    description="Get delay trends over time (monthly or weekly)"
                ),
                Tool(
                    name="GetProductDelays",
                    func=self._get_product_delays,
                    description="Get delivery delays at product or category level. Useful for product-specific delay analysis. Input format: 'product_id:PRODUCT_ID' or 'category:CATEGORY_NAME' or leave empty for all products"
                ),
            ]

            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Delivery Delay Analysis Agent.
Your expertise is in analyzing delivery performance, identifying delay patterns, and providing insights.

CRITICAL: Determine if the user is asking about:
1. **POLICY/PROCEDURES** (severity levels, definitions, guidelines, classifications, protocols)
   → If the input contains "Context from documents:", USE THAT CONTEXT to answer
   → DO NOT query database tools for policy questions
   → Extract and present the information from the provided document context

2. **DATA/STATISTICS** (actual delays, counts, rates, trends from current operations)
   → Use the available tools to query real operational data

IMPORTANT INSTRUCTIONS:
- Answer ONLY what the user specifically asks for
- Be concise and direct - don't provide extra information unless requested
- If asked for one metric (e.g., "delay rate"), provide ONLY that metric
- If asked for multiple things or "show statistics", then provide comprehensive details
- Always include the specific number/percentage with proper context

When users ask about DATA/STATISTICS:
1. Use GetDelayStatistics for overall delay metrics
2. Use GetStateDelays for geographic analysis
3. Use GetDelayTrends for temporal patterns
4. Use GetProductDelays for product-level or category-level delay analysis

RESPONSE GUIDELINES:
- "What is the delay rate?" → Answer with just the delay rate percentage
- "Show delay statistics" → Provide comprehensive statistics
- "How many delayed orders?" → Answer with just the count
- "Analyze delays" → Provide analysis with multiple metrics
- "What are severity levels?" → Use the document context if provided, otherwise explain you need policy documents

Extract only the relevant information from tool results to answer the specific question."""),
                ("human", "{input}"),
            ])

            # Create agent
            agent = create_tool_calling_agent(self.llm_client, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True
            )

            logger.info("Delay Agent LangChain executor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LangChain agent: {e}")
            self.use_langchain = False

    def _get_delay_statistics(self, query: str = "") -> str:
        """Get overall delay statistics"""
        try:
            result = self.analytics.analyze_delivery_delays()
            return f"""Delay Statistics:
- Total Orders: {result['total_orders']:,}
- Delayed Orders: {result['delayed_orders']:,}
- Delay Rate: {result['delay_rate_percentage']:.2f}%
- On-Time Rate: {100 - result['delay_rate_percentage']:.2f}%
- Average Delay: {result['average_delay_days']:.1f} days
- Max Delay: {result['max_delay_days']:.0f} days
- Median Delay: {result['median_delay_days']:.1f} days"""
        except Exception as e:
            return f"Error getting delay statistics: {e}"

    def _get_state_delays(self, query: str = "") -> str:
        """Get delays by state"""
        try:
            result = self.analytics.analyze_delivery_delays()
            delays_by_state = result.get('delays_by_state', {})

            if not delays_by_state:
                return "No state-level delay data available"

            # Sort by delay rate
            sorted_states = sorted(
                [(state, rate * 100) for state, rate in delays_by_state.items()],
                key=lambda x: x[1],
                reverse=True
            )

            response = "Delays by State (Top 10):\n"
            for i, (state, rate) in enumerate(sorted_states[:10], 1):
                response += f"{i}. {state}: {rate:.1f}% delay rate\n"

            return response
        except Exception as e:
            return f"Error getting state delays: {e}"

    def _get_delay_trends(self, query: str = "") -> str:
        """Get delay trends over time"""
        try:
            result = self.analytics.analyze_delivery_delays()
            return f"""Delay Trends:
- Current Delay Rate: {result['delay_rate_percentage']:.2f}%
- Average Delay Duration: {result['average_delay_days']:.1f} days
- Trend: {'Improving' if result['delay_rate_percentage'] < 10 else 'Needs Attention'}"""
        except Exception as e:
            return f"Error getting delay trends: {e}"

    def _get_product_delays(self, query: str = "") -> str:
        """Get product-level delay analysis"""
        try:
            # Parse query to extract product_id or category
            product_id = None
            category = None

            if query:
                query_str = query.strip()
                query_lower = query_str.lower()

                # Structured format (from LangChain agent)
                if query_str.startswith("product_id:"):
                    product_id = query_str.replace("product_id:", "").strip()
                elif query_str.startswith("category:"):
                    category = query_str.replace("category:", "").strip()
                # Natural language parsing
                else:
                    # Try to extract specific category names from common categories
                    categories = ['electronics', 'furniture', 'clothing', 'toys', 'books',
                                 'sports', 'home', 'garden', 'automotive', 'food']
                    for cat in categories:
                        if cat in query_lower:
                            category = cat.title()
                            logger.info(f"Detected category: {category}")
                            break

                    # If still no match, check for "product X" pattern
                    if not category and not product_id:
                        import re
                        product_match = re.search(r'product\s+([A-Za-z0-9_-]+)', query_lower)
                        if product_match:
                            product_id = product_match.group(1)
                            logger.info(f"Detected product_id: {product_id}")

            # Get analysis from analytics engine
            result = self.analytics.analyze_product_delays(
                product_id=product_id,
                category=category
            )

            # Check for errors
            if 'error' in result:
                return result['error']

            # Format response
            response = f"""Product-Level Delay Analysis ({result['filter']}):

**Overall Statistics:**
- Total Orders: {result['total_orders']:,}
- Delayed Orders: {result['delayed_orders']:,}
- Delay Rate: {result['delay_rate_percentage']:.2f}%
- On-Time Rate: {100 - result['delay_rate_percentage']:.2f}%
- Average Delay: {result['average_delay_days']:.1f} days
- Max Delay: {result['max_delay_days']:.1f} days"""

            # Add top delayed products if analyzing all products
            if 'top_delayed_products' in result:
                response += "\n\n🔴 **Top 5 Delayed Products:**\n"
                for i, product in enumerate(result['top_delayed_products'][:5], 1):
                    response += f"{i}. Product {product['product_id']}: {product['delay_rate']*100:.1f}% delay rate ({product['delayed_count']}/{product['total_count']} orders)\n"

            # Add top delayed categories if available
            if 'top_delayed_categories' in result:
                response += "\n\n**Top 5 Delayed Categories:**\n"
                for i, cat in enumerate(result['top_delayed_categories'][:5], 1):
                    response += f"{i}. {cat['category']}: {cat['delay_rate']*100:.1f}% delay rate ({cat['delayed_count']}/{cat['total_count']} orders)\n"

            return response

        except Exception as e:
            logger.error(f"Error in product delay analysis: {e}")
            return f"Error getting product delays: {e}"

    def query(self, user_query: str, classification: Dict = None) -> Dict[str, Any]:
        """
        Process delay-related query

        Args:
            user_query: User's question about delays
            classification: Optional query classification (policy/data/mixed)

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Determine if should use RAG based on classification
            should_use_rag = classification.get('use_rag', True) if classification else True
            should_use_database = classification.get('use_database', True) if classification else True

            logger.info(f"Delay Agent - Use RAG: {should_use_rag} | Use Database: {should_use_database}")

            # Try RAG context retrieval if classification allows it
            rag_context = None
            used_rag = False
            if self.rag_module and should_use_rag:
                try:
                    rag_context = self.rag_module.retrieve_context(user_query)
                    if rag_context and len(rag_context.strip()) > 0:
                        used_rag = True
                        logger.info("✅ RAG context retrieved for delay query")
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
                    'agent': 'Delay Agent (LangChain)' + (' + RAG' if used_rag else ''),
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
                            'agent': 'Delay Agent (Rule-Based) + RAG',
                            'success': True,
                            'used_rag': True,
                            'classification': classification
                        }
                    else:
                        return {
                            'response': "No policy documents found for this query. Please rephrase or ask a data question.",
                            'agent': 'Delay Agent (Rule-Based)',
                            'success': True,
                            'used_rag': False,
                            'classification': classification
                        }

                # NEW: If classification says this is DATA ONLY or default - skip policy check
                # PRIORITY: Check for product-level DATA queries
                if 'product' in query_lower or 'category' in query_lower or 'item' in query_lower:
                    response = self._get_product_delays(user_query)
                # Geographic queries
                elif 'state' in query_lower or 'where' in query_lower or 'geographic' in query_lower:
                    response = self._get_state_delays()
                elif 'trend' in query_lower or 'over time' in query_lower:
                    response = self._get_delay_trends()
                else:
                    # Get the full statistics for other queries
                    result = self.analytics.analyze_delivery_delays()

                    # Specific questions - return only what's asked
                    if 'what is the delay rate' in query_lower or 'delay rate?' in query_lower:
                        response = f"The current delivery delay rate is **{result['delay_rate_percentage']:.2f}%**"
                    elif 'on-time rate' in query_lower or 'on time rate' in query_lower:
                        on_time = 100 - result['delay_rate_percentage']
                        response = f"The on-time delivery rate is **{on_time:.2f}%**"
                    elif 'how many delayed' in query_lower or 'number of delayed' in query_lower:
                        response = f"There are **{result['delayed_orders']:,}** delayed orders out of **{result['total_orders']:,}** total orders"
                    elif 'average delay' in query_lower or 'mean delay' in query_lower:
                        response = f"The average delay duration is **{result['average_delay_days']:.1f} days**"
                    elif 'maximum delay' in query_lower or 'max delay' in query_lower or 'worst delay' in query_lower:
                        response = f"The maximum delay is **{result['max_delay_days']:.0f} days**"
                    elif 'median delay' in query_lower:
                        response = f"The median delay is **{result['median_delay_days']:.1f} days**"
                    # Comprehensive questions - return full statistics
                    elif 'statistics' in query_lower or 'show all' in query_lower or 'comprehensive' in query_lower or 'analyze' in query_lower or 'overview' in query_lower:
                        response = self._get_delay_statistics()
                    # Default - give rate and on-time as minimum useful answer
                    else:
                        response = f"""**Delivery Performance:**
- Delay Rate: {result['delay_rate_percentage']:.2f}%
- On-Time Rate: {100 - result['delay_rate_percentage']:.2f}%

*Ask for "delay statistics" for more details*"""

                # Append RAG context only if classification allows it (mixed queries)
                if used_rag and should_use_rag and rag_context and len(rag_context.strip()) > 20 and "no relevant" not in rag_context.lower():
                    # Only append if this is a mixed query (both RAG and database)
                    if classification and classification.get('query_type') == 'mixed':
                        # Use UIFormatter for better RAG context formatting
                        formatted_rag = UIFormatter.format_rag_context(rag_context)
                        response += f"\n\n{formatted_rag}"

                return {
                    'response': response,
                    'agent': 'Delay Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag,
                    'classification': classification
                }

        except Exception as e:
            logger.error(f"Delay Agent error: {e}")
            return {
                'response': f"Error processing delay query: {e}",
                'agent': 'Delay Agent',
                'success': False,
                'used_rag': False
            }
