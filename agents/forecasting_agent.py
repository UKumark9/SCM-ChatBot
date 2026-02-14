"""
Forecasting Agent — SARIMA demand, revenue, delay-rate, and category forecasting.
Part of the SCM Chatbot Agentic Architecture.

Supported forecast types:
  - Demand forecast        : weekly order volume (15-20% walk-forward MAPE)
  - Revenue forecast       : weekly payment_value sum
  - Delivery delay rate    : weekly % of late deliveries
  - Category-level demand  : weekly orders for the top product category

Linear regression and Prophet have been removed:
  - Linear regression MAPE was 110%+ (daily sparse data, zero-division).
  - SARIMA on weekly aggregated data achieves 15-20% walk-forward MAPE
    (genuine seasonal dips in e-commerce data without external regressors
    set a practical floor; simple_differencing=False prevents divergent forecasts).
"""

import re
import logging
from typing import Dict, Any, Optional
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
    logger.warning("LangChain not available for Forecasting Agent")


class ForecastingAgent:
    """Demand forecasting agent — SARIMA time series only."""

    def __init__(self, analytics_engine, llm_client=None, use_langchain: bool = True,
                 rag_module=None, forecasting_engine=None):
        self.analytics          = analytics_engine
        self.llm_client         = llm_client
        self.use_langchain      = use_langchain and LANGCHAIN_AVAILABLE
        self.rag_module         = rag_module
        self.forecasting_engine = forecasting_engine
        self.agent_executor     = None
        self._pending_chart: Optional[str] = None    # primary chart (line)
        self._pending_charts: Optional[list] = None  # all charts (line + bar + pie)

        if self.use_langchain and llm_client:
            self._initialize_langchain_agent()

        logger.info(
            f"Forecasting Agent initialized "
            f"(LangChain: {self.use_langchain}, "
            f"RAG: {rag_module is not None}, "
            f"SARIMA Engine: {forecasting_engine is not None})"
        )

    def _initialize_langchain_agent(self):
        """Initialize LangChain agent with all SARIMA forecast tools."""
        try:
            tools = [
                # ── Demand forecast tools ────────────────────────────────────
                Tool(
                    name="ForecastSARIMA30",
                    func=lambda x: self._forecast_sarima("30"),
                    description=(
                        "Forecast order demand for the next 30 days using SARIMA "
                        "time series model. Weekly aggregation, 95% confidence intervals."
                    ),
                ),
                Tool(
                    name="ForecastSARIMA60",
                    func=lambda x: self._forecast_sarima("60"),
                    description=(
                        "Forecast order demand for the next 60 days using SARIMA "
                        "time series model."
                    ),
                ),
                Tool(
                    name="ForecastSARIMA90",
                    func=lambda x: self._forecast_sarima("90"),
                    description=(
                        "Forecast order demand for the next 90 days using SARIMA "
                        "time series model."
                    ),
                ),
                # ── Revenue forecast tools ───────────────────────────────────
                Tool(
                    name="ForecastRevenue30",
                    func=lambda x: self._forecast_revenue("30"),
                    description=(
                        "Forecast weekly revenue (payment value in R$) for the next "
                        "30 days using SARIMA time series model."
                    ),
                ),
                Tool(
                    name="ForecastRevenue60",
                    func=lambda x: self._forecast_revenue("60"),
                    description=(
                        "Forecast weekly revenue for the next 60 days using SARIMA."
                    ),
                ),
                Tool(
                    name="ForecastRevenue90",
                    func=lambda x: self._forecast_revenue("90"),
                    description=(
                        "Forecast weekly revenue for the next 90 days using SARIMA."
                    ),
                ),
                # ── Delay rate forecast tools ────────────────────────────────
                Tool(
                    name="ForecastDelayRate30",
                    func=lambda x: self._forecast_delay_rate("30"),
                    description=(
                        "Forecast the weekly delivery delay rate (% of late orders) "
                        "for the next 30 days using SARIMA time series model."
                    ),
                ),
                Tool(
                    name="ForecastDelayRate60",
                    func=lambda x: self._forecast_delay_rate("60"),
                    description=(
                        "Forecast the weekly delivery delay rate for the next 60 days."
                    ),
                ),
                Tool(
                    name="ForecastDelayRate90",
                    func=lambda x: self._forecast_delay_rate("90"),
                    description=(
                        "Forecast the weekly delivery delay rate for the next 90 days."
                    ),
                ),
                # ── Category demand forecast tools ───────────────────────────
                Tool(
                    name="ForecastCategoryDemand30",
                    func=lambda x: self._forecast_category("30"),
                    description=(
                        "Forecast weekly demand for the top product category "
                        "for the next 30 days using SARIMA time series model."
                    ),
                ),
                Tool(
                    name="ForecastCategoryDemand60",
                    func=lambda x: self._forecast_category("60"),
                    description=(
                        "Forecast weekly demand for the top product category "
                        "for the next 60 days using SARIMA."
                    ),
                ),
                Tool(
                    name="ForecastCategoryDemand90",
                    func=lambda x: self._forecast_category("90"),
                    description=(
                        "Forecast weekly demand for the top product category "
                        "for the next 90 days using SARIMA."
                    ),
                ),
                # ── All-categories comparison tools ──────────────────────────
                Tool(
                    name="ForecastAllCategories30",
                    func=lambda x: self._forecast_all_categories("30"),
                    description=(
                        "Forecast weekly demand for each of the top 5 product categories "
                        "for the next 30 days. Returns a comparison chart and summary table."
                    ),
                ),
                Tool(
                    name="ForecastAllCategories60",
                    func=lambda x: self._forecast_all_categories("60"),
                    description=(
                        "Forecast weekly demand for each of the top 5 product categories "
                        "for the next 60 days. Returns a comparison chart and summary table."
                    ),
                ),
                Tool(
                    name="ForecastAllCategories90",
                    func=lambda x: self._forecast_all_categories("90"),
                    description=(
                        "Forecast weekly demand for each of the top 5 product categories "
                        "for the next 90 days. Returns a comparison chart and summary table."
                    ),
                ),
            ]

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a Demand Forecasting Agent powered by SARIMA.
You use SARIMA (Seasonal AutoRegressive Integrated Moving Average) time series modelling
on weekly-aggregated data. This achieves ~15-20% MAPE vs 100%+ for naive daily baselines.

CRITICAL: Determine if the user is asking about:
1. **POLICY/PROCEDURES** (forecasting methodology, planning guidelines, definitions)
   → If the input contains "Context from documents:", USE THAT CONTEXT to answer.
   → DO NOT call forecasting tools for policy questions.

2. **FORECASTS / DATA** (future demand, revenue, delay rate, or category volumes)
   → Use the appropriate tool below.

TOOL ROUTING — choose the best match:

Demand forecast (order volume):
  - 30-day / default   → ForecastSARIMA30
  - 60-day / 2 months  → ForecastSARIMA60
  - 90-day / quarter   → ForecastSARIMA90

Revenue forecast:
  - 30-day             → ForecastRevenue30
  - 60-day / 2 months  → ForecastRevenue60
  - 90-day / quarter   → ForecastRevenue90

Delivery delay rate forecast:
  - 30-day / default   → ForecastDelayRate30
  - 60-day             → ForecastDelayRate60
  - 90-day             → ForecastDelayRate90

Category demand forecast (single top category):
  - 30-day / default   → ForecastCategoryDemand30
  - 60-day             → ForecastCategoryDemand60
  - 90-day             → ForecastCategoryDemand90

All-categories comparison (top 5 categories, comparison chart + table):
  - 30-day / default   → ForecastAllCategories30
  - 60-day             → ForecastAllCategories60
  - 90-day             → ForecastAllCategories90
  Use when the user says: "each category", "all categories", "per category",
  "compare categories", "category comparison", "breakdown by category"

HORIZON DETECTION:
  "2 months" / "two months"  → 60-day tool
  "3 months" / "quarter"     → 90-day tool
  "next month" / default     → 30-day tool

RESPONSE GUIDELINES:
- Provide trend direction, average forecast, and MAPE in the answer.
- Mention that the chart shows the historical baseline and 95% confidence interval.
- Be concise — surface the most important numbers only unless asked for details.
- "What is the forecasting policy?" → Use the document context if provided."""),
                ("human", "{input}"),
            ])

            agent = create_tool_calling_agent(self.llm_client, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True,
            )
            logger.info("Forecasting Agent LangChain executor initialized (all SARIMA tools)")
        except Exception as e:
            logger.error(f"Failed to initialize Forecasting agent: {e}")
            self.use_langchain = False

    # ── Tool handler methods ──────────────────────────────────────────────────

    def _forecast_sarima(self, query: str = "30") -> str:
        """
        Run SARIMA demand forecast via the forecasting engine.

        The chart is stored in self._pending_chart so it survives the LangChain
        tool → LLM boundary (the LLM never echoes the 50 KB base64 string back,
        so embedding it in the return value would silently discard it).
        """
        self._pending_chart = None
        self._pending_charts = None
        if not self.forecasting_engine:
            return (
                "SARIMA engine not initialised. "
                "Ensure statsmodels is installed: pip install statsmodels"
            )
        try:
            digits  = re.search(r'\d+', str(query))
            periods = int(digits.group()) if digits else 30
            result  = self.forecasting_engine.forecast_sarima(periods=periods)
            if 'error' in result:
                return result['error']
            self._pending_chart = result.get('chart_base64')
            self._pending_charts = result.get('charts_base64')
            return result['summary_text']
        except Exception as e:
            logger.error(f"SARIMA demand forecast error: {e}")
            return f"SARIMA demand forecast error: {e}"

    def _forecast_revenue(self, query: str = "30") -> str:
        """Run SARIMA revenue forecast — charts stored in self._pending_charts."""
        self._pending_chart = None
        self._pending_charts = None
        if not self.forecasting_engine:
            return "SARIMA engine not initialised. pip install statsmodels"
        try:
            digits  = re.search(r'\d+', str(query))
            periods = int(digits.group()) if digits else 30
            result  = self.forecasting_engine.forecast_revenue(periods=periods)
            if 'error' in result:
                return result['error']
            self._pending_chart = result.get('chart_base64')
            self._pending_charts = result.get('charts_base64')
            return result['summary_text']
        except Exception as e:
            logger.error(f"SARIMA revenue forecast error: {e}")
            return f"SARIMA revenue forecast error: {e}"

    def _forecast_delay_rate(self, query: str = "30") -> str:
        """Run SARIMA delay rate forecast — charts stored in self._pending_charts."""
        self._pending_chart = None
        self._pending_charts = None
        if not self.forecasting_engine:
            return "SARIMA engine not initialised. pip install statsmodels"
        try:
            digits  = re.search(r'\d+', str(query))
            periods = int(digits.group()) if digits else 30
            result  = self.forecasting_engine.forecast_delay_rate(periods=periods)
            if 'error' in result:
                return result['error']
            self._pending_chart = result.get('chart_base64')
            self._pending_charts = result.get('charts_base64')
            return result['summary_text']
        except Exception as e:
            logger.error(f"SARIMA delay rate forecast error: {e}")
            return f"SARIMA delay rate forecast error: {e}"

    def _forecast_all_categories(self, query: str = "30") -> str:
        """
        Run SARIMA demand forecast for top 5 categories — charts stored in self._pending_charts.
        Uses fast parameter selection so N independent SARIMA fits remain responsive.
        """
        self._pending_chart = None
        self._pending_charts = None
        if not self.forecasting_engine:
            return "SARIMA engine not initialised. pip install statsmodels"
        try:
            digits  = re.search(r'\d+', str(query))
            periods = int(digits.group()) if digits else 30
            result  = self.forecasting_engine.forecast_top_categories(periods=periods, top_n=5)
            if 'error' in result:
                return result['error']
            self._pending_chart = result.get('chart_base64')
            self._pending_charts = result.get('charts_base64')
            return result['summary_text']
        except Exception as e:
            logger.error(f"SARIMA all-categories forecast error: {e}")
            return f"SARIMA all-categories forecast error: {e}"

    def _forecast_category(self, query: str = "30") -> str:
        """Run SARIMA category demand forecast — charts stored in self._pending_charts."""
        self._pending_chart = None
        self._pending_charts = None
        if not self.forecasting_engine:
            return "SARIMA engine not initialised. pip install statsmodels"
        try:
            digits  = re.search(r'\d+', str(query))
            periods = int(digits.group()) if digits else 30
            result  = self.forecasting_engine.forecast_category(periods=periods)
            if 'error' in result:
                return result['error']
            self._pending_chart = result.get('chart_base64')
            self._pending_charts = result.get('charts_base64')
            return result['summary_text']
        except Exception as e:
            logger.error(f"SARIMA category forecast error: {e}")
            return f"SARIMA category forecast error: {e}"

    # ── Main query method ────────────────────────────────────────────────────

    def query(self, user_query: str, classification: Dict = None) -> Dict[str, Any]:
        """Process a forecasting query — SARIMA only."""
        try:
            should_use_rag      = classification.get('use_rag', True)      if classification else True
            should_use_database = classification.get('use_database', True) if classification else True

            logger.info(f"Forecasting Agent — RAG: {should_use_rag} | DB: {should_use_database}")

            # RAG context retrieval
            rag_context = None
            used_rag    = False
            if self.rag_module and should_use_rag:
                try:
                    rag_context = self.rag_module.retrieve_context(user_query)
                    if rag_context and len(rag_context.strip()) > 0:
                        used_rag = True
                        logger.info("RAG context retrieved for forecasting query")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # ── LangChain path ───────────────────────────────────────────────
            if self.use_langchain and self.agent_executor:
                augmented_query = (
                    f"Context from documents:\n{rag_context}\n\nUser query: {user_query}"
                    if used_rag else user_query
                )

                self._pending_chart = None
                self._pending_charts = None
                response = self.agent_executor.invoke({"input": augmented_query})

                chart_b64  = self._pending_chart
                charts_b64 = self._pending_charts

                return {
                    'response':      response['output'],
                    'chart_base64':  chart_b64,
                    'charts_base64': charts_b64,
                    'agent':         'Forecasting Agent (SARIMA)' + (' + RAG' if used_rag else ''),
                    'success':       True,
                    'used_rag':      used_rag,
                }

            # ── Rule-based path ──────────────────────────────────────────────
            query_lower = user_query.lower()

            # Policy-only questions
            if classification and classification.get('query_type') == 'policy':
                if used_rag and rag_context and len(rag_context.strip()) > 20:
                    return {
                        'response':     UIFormatter.format_rag_context(rag_context),
                        'chart_base64': None,
                        'agent':        'Forecasting Agent (SARIMA) + RAG',
                        'success':      True,
                        'used_rag':     True,
                        'classification': classification,
                    }
                return {
                    'response':     'No policy documents found. Please ask a demand forecasting question.',
                    'chart_base64': None,
                    'agent':        'Forecasting Agent (SARIMA)',
                    'success':      True,
                    'used_rag':     False,
                    'classification': classification,
                }

            # Determine forecast horizon
            if '90' in query_lower or 'three month' in query_lower or 'quarter' in query_lower:
                periods = 90
            elif '60' in query_lower or 'two month' in query_lower:
                periods = 60
            else:
                periods = 30

            # Determine forecast type from query text
            self._pending_chart = None
            self._pending_charts = None
            _all_cat_kw = ['each category', 'all categories', 'per category',
                           'every category', 'category comparison', 'compare categories',
                           'breakdown by category', 'category breakdown',
                           'each product category', 'all product categories']
            if any(kw in query_lower for kw in ['revenue', 'payment', 'sales revenue']):
                response  = self._forecast_revenue(str(periods))
                agent_tag = 'Forecasting Agent (Revenue)'
            elif any(kw in query_lower for kw in ['delay rate', 'late rate', 'on-time rate',
                                                    'delivery rate', 'forecast delay']):
                response  = self._forecast_delay_rate(str(periods))
                agent_tag = 'Forecasting Agent (Delay Rate)'
            elif any(kw in query_lower for kw in _all_cat_kw):
                response  = self._forecast_all_categories(str(periods))
                agent_tag = 'Forecasting Agent (All Categories)'
            elif any(kw in query_lower for kw in ['category', 'product category',
                                                    'top category', 'category demand']):
                response  = self._forecast_category(str(periods))
                agent_tag = 'Forecasting Agent (Category)'
            else:
                response  = self._forecast_sarima(str(periods))
                agent_tag = 'Forecasting Agent (SARIMA)'

            chart_b64  = self._pending_chart
            charts_b64 = self._pending_charts

            # Append RAG context for mixed queries
            if (used_rag and should_use_rag and rag_context
                    and len(rag_context.strip()) > 20
                    and 'no relevant' not in rag_context.lower()
                    and classification
                    and classification.get('query_type') == 'mixed'):
                response += f"\n\n{UIFormatter.format_rag_context(rag_context)}"

            return {
                'response':      response,
                'chart_base64':  chart_b64,
                'charts_base64': charts_b64,
                'agent':         agent_tag + (' + RAG' if used_rag else ''),
                'success':       True,
                'used_rag':      used_rag,
                'classification': classification,
            }

        except Exception as e:
            logger.error(f"Forecasting Agent error: {e}")
            return {
                'response':  f"Error processing forecast query: {e}",
                'agent':     'Forecasting Agent (SARIMA)',
                'success':   False,
                'used_rag':  False,
            }
