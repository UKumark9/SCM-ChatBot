"""
Delay Agent - Specialized agent for delivery delay analysis
Part of the SCM Chatbot Agentic Architecture
"""

import logging
from typing import Dict, Any, List
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
            ]

            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Delivery Delay Analysis Agent.
Your expertise is in analyzing delivery performance, identifying delay patterns, and providing insights.

When users ask about delays:
1. Use GetDelayStatistics for overall delay metrics
2. Use GetStateDelays for geographic analysis
3. Use GetDelayTrends for temporal patterns

Provide clear, actionable insights with specific numbers."""),
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

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Process delay-related query

        Args:
            user_query: User's question about delays

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Try RAG context retrieval first
            rag_context = None
            used_rag = False
            if self.rag_module:
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

                if 'state' in query_lower or 'where' in query_lower:
                    response = self._get_state_delays()
                elif 'trend' in query_lower or 'over time' in query_lower:
                    response = self._get_delay_trends()
                else:
                    response = self._get_delay_statistics()

                # Append RAG context if available
                if used_rag:
                    response += f"\n\n📚 **Additional Context from Documents:**\n{rag_context[:500]}..."

                return {
                    'response': response,
                    'agent': 'Delay Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

        except Exception as e:
            logger.error(f"Delay Agent error: {e}")
            return {
                'response': f"Error processing delay query: {e}",
                'agent': 'Delay Agent',
                'success': False,
                'used_rag': False
            }
