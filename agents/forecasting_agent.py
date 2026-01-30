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
                    description="Forecast overall demand for the next 30 days"
                ),
                Tool(
                    name="ForecastDemand60Days",
                    func=lambda x: self._forecast_demand(60),
                    description="Forecast overall demand for the next 60 days"
                ),
                Tool(
                    name="ForecastDemand90Days",
                    func=lambda x: self._forecast_demand(90),
                    description="Forecast overall demand for the next 90 days"
                ),
                Tool(
                    name="ForecastProductDemand",
                    func=self._forecast_product_demand,
                    description="Forecast demand for a specific product. Input format: 'product_id:PRODUCT_ID,periods:NUMBER' (e.g., 'product_id:12345,periods:30')"
                ),
            ]

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Demand Forecasting Agent.
Your expertise is in predicting future demand, analyzing trends, and helping with inventory planning.

IMPORTANT INSTRUCTIONS:
- Answer ONLY what the user specifically asks for
- Be concise and direct - don't provide extra information unless requested
- If asked for a specific forecast period, provide only that forecast
- If asked for "analysis" or "detailed forecast", provide comprehensive details
- Always include trend direction and key numbers

Available forecasting tools:
1. ForecastDemand30Days/60Days/90Days - For overall demand across all products
2. ForecastProductDemand - For product-specific demand forecasting

RESPONSE GUIDELINES:
- "Forecast demand for 30 days" → Provide forecast with trend and historical avg
- "What will demand be?" → Provide simple forecast answer
- "Detailed forecast analysis" → Include all metrics and insights
- "Forecast for product X" → Use product-specific tool

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

    def _forecast_product_demand(self, query: str = "") -> str:
        """Forecast demand for a specific product"""
        try:
            # Parse query to extract product_id and periods
            product_id = None
            periods = 30  # Default

            if query:
                parts = query.split(',')
                for part in parts:
                    part = part.strip()
                    if part.startswith("product_id:"):
                        product_id = part.replace("product_id:", "").strip()
                    elif part.startswith("periods:"):
                        try:
                            periods = int(part.replace("periods:", "").strip())
                        except ValueError:
                            periods = 30

            if not product_id:
                return "Error: Product ID is required for product-level forecasting. Use format: 'product_id:PRODUCT_ID,periods:NUMBER'"

            # Get forecast from analytics engine
            result = self.analytics.forecast_demand(
                product_id=product_id,
                periods=periods
            )

            response = f"""Product Demand Forecast:

📦 **Product**: {product_id}
📅 **Forecast Period**: {periods} days

📊 **Historical Performance:**
- Historical Average: {result['historical_average']:.1f} units/day
- Trend: {result['trend'].title()}

📈 **Forecast Quality:**
- Model Accuracy (MAPE): {result['model_metrics']['mape']:.2f}%
- R² Score: {result['model_metrics']['r_squared']:.3f}
- RMSE: {result['model_metrics']['rmse']:.2f}

💡 **Insights:**
"""
            if result['trend'] == 'increasing':
                response += "- Demand is growing. Consider increasing inventory levels.\n"
            elif result['trend'] == 'decreasing':
                response += "- Demand is declining. May need to adjust procurement.\n"
            else:
                response += "- Demand is stable. Maintain current inventory strategy.\n"

            if result['model_metrics']['mape'] < 15:
                response += "- High forecast accuracy. Reliable for planning.\n"
            elif result['model_metrics']['mape'] < 30:
                response += "- Moderate forecast accuracy. Use with caution.\n"
            else:
                response += "- Low forecast accuracy. Consider additional data sources.\n"

            return response

        except Exception as e:
            logger.error(f"Error in product demand forecasting: {e}")
            return f"Error forecasting product demand: {e}"

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

                # Append RAG context if available and meaningful
                if used_rag and rag_context and len(rag_context.strip()) > 20 and "no relevant" not in rag_context.lower():
                    response += f"\n\n📚 **Document Context:**\n{rag_context[:400]}"
                    if len(rag_context) > 400:
                        response += "..."

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
