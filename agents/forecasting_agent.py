"""
Forecasting Agent - Specialized agent for demand forecasting
Part of the SCM Chatbot Agentic Architecture
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from langchain_groq import ChatGroq
    from langchain_core.tools import Tool
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available for Forecasting Agent")


class ForecastingAgent:
    """Specialized agent for demand forecasting and predictions"""

    def __init__(self, analytics_engine, llm_client=None, use_langchain: bool = True, rag_module=None):
        """
        Initialize Forecasting Agent

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

        logger.info(f"Forecasting Agent initialized (LangChain: {self.use_langchain}, RAG: {rag_module is not None})")

    def _initialize_langchain_agent(self):
        """Initialize LangChain agent"""
        try:
            tools = [
                Tool(
                    name="ForecastDemand30Days",
                    func=lambda x: self._forecast_demand(30),
                    description="Forecast demand for the next 30 days"
                ),
                Tool(
                    name="ForecastDemand60Days",
                    func=lambda x: self._forecast_demand(60),
                    description="Forecast demand for the next 60 days"
                ),
                Tool(
                    name="ForecastDemand90Days",
                    func=lambda x: self._forecast_demand(90),
                    description="Forecast demand for the next 90 days"
                ),
            ]

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Demand Forecasting Agent.
Your expertise is in predicting future demand, analyzing trends, and helping with inventory planning.

Use forecasting tools to provide accurate predictions and actionable insights."""),
                ("human", "{input}"),
            ])

            agent = create_tool_calling_agent(self.llm_client, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True
            )

            logger.info("Forecasting Agent LangChain executor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Forecasting agent: {e}")
            self.use_langchain = False

    def _forecast_demand(self, periods: int = 30) -> str:
        """Forecast demand for specified periods"""
        try:
            result = self.analytics.forecast_demand(periods=periods)
            return f"""Demand Forecast ({periods} days):
- Historical Average: {result['historical_average']:.1f} items/day
- Trend: {result['trend'].title()}
- Model Accuracy (MAPE): {result['model_metrics']['mape']:.2f}%
- R² Score: {result['model_metrics']['r_squared']:.3f}
- Forecast Method: {result.get('forecast_method', 'Statistical')}"""
        except Exception as e:
            return f"Error forecasting demand: {e}"

    def query(self, user_query: str) -> Dict[str, Any]:
        """Process forecasting query"""
        try:
            # Try RAG context retrieval first
            rag_context = None
            used_rag = False
            if self.rag_module:
                try:
                    rag_context = self.rag_module.retrieve_context(user_query)
                    if rag_context and len(rag_context.strip()) > 0:
                        used_rag = True
                        logger.info("✅ RAG context retrieved for forecasting query")
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
                    'agent': 'Forecasting Agent (LangChain)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

            # Fallback to rule-based
            else:
                # Extract period from query
                query_lower = user_query.lower()

                if '60' in query_lower or 'two month' in query_lower:
                    periods = 60
                elif '90' in query_lower or 'three month' in query_lower:
                    periods = 90
                else:
                    periods = 30

                response = self._forecast_demand(periods)

                # Append RAG context if available
                if used_rag:
                    response += f"\n\n📚 **Additional Context from Documents:**\n{rag_context[:500]}..."

                return {
                    'response': response,
                    'agent': 'Forecasting Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

        except Exception as e:
            logger.error(f"Forecasting Agent error: {e}")
            return {
                'response': f"Error processing forecast query: {e}",
                'agent': 'Forecasting Agent',
                'success': False,
                'used_rag': False
            }
