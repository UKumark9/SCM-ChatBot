"""
Agent Orchestrator - Central controller for multi-agent SCM system
Routes queries to specialized agents based on intent
"""

import logging
from typing import Dict, Any, Optional, List
import os
import time

from scm_chatbot.agents.delay_agent import DelayAgent
from scm_chatbot.agents.analytics_agent import AnalyticsAgent
from scm_chatbot.agents.forecasting_agent import ForecastingAgent
from scm_chatbot.agents.data_query_agent import DataQueryAgent
from scm_chatbot.agents.query_router import QueryRouter
from scm_chatbot.ui.ui_formatter import UIFormatter
from scm_chatbot.services.intent_classifier import IntentClassifier
from scm_chatbot.llm.guardrails import REFUSAL_MESSAGE, detect_injection

logger = logging.getLogger(__name__)

try:
    from langchain_groq import ChatGroq

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available for Orchestrator")


class AgentOrchestrator:
    """
    Central orchestrator that manages multiple specialized agents
    Routes queries to the appropriate agent based on intent analysis
    """

    def __init__(
        self,
        analytics_engine,
        data_wrapper,
        rag_module=None,
        use_langchain: bool = True,
        feature_store=None,
    ):
        """
        Initialize Agent Orchestrator

        Args:
            analytics_engine: SCMAnalytics instance
            data_wrapper: Data wrapper with orders, customers, products
            rag_module: RAG module for semantic search (optional)
            use_langchain: Whether to use LangChain agentic framework
            feature_store: FeatureStore instance for caching (optional)
        """
        self.analytics = analytics_engine
        self.data = data_wrapper
        self.rag = rag_module
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.feature_store = feature_store
        self.conversation_history = []

        # Initialize Intent Classifier for better query routing
        self.intent_classifier = IntentClassifier()

        # Initialize LLM client
        self.llm_client = None
        if self.use_langchain:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.llm_client = ChatGroq(
                        model="llama-3.3-70b-versatile",
                        temperature=0.1,
                        api_key=api_key,
                    )
                    logger.info("LLM client initialized for Orchestrator")
                except Exception as e:
                    logger.error(f"Failed to initialize LLM client: {e}")
                    self.use_langchain = False
            else:
                logger.warning("GROQ_API_KEY not found, LangChain agents disabled")
                self.use_langchain = False

        # Query routing (SRP: extracted to its own class, see agents/query_router.py)
        self.router = QueryRouter(llm_client=self.llm_client)

        # Pass feature store to analytics engine for caching
        if feature_store and hasattr(analytics_engine, "feature_store"):
            pass  # Already set
        elif feature_store:
            analytics_engine.feature_store = feature_store

        # Initialize specialized agents with RAG
        self.delay_agent = DelayAgent(
            analytics_engine=analytics_engine,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module,
        )

        self.analytics_agent = AnalyticsAgent(
            analytics_engine=analytics_engine,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module,
        )

        # Initialize advanced forecasting engine (SARIMA)
        forecasting_engine = None
        try:
            from scm_chatbot.tools.forecasting_engine import ForecastingEngine

            forecasting_engine = ForecastingEngine(
                orders_df=analytics_engine.orders,
                order_items_df=analytics_engine.order_items,
                payments_df=getattr(analytics_engine, "payments", None),
                products_df=getattr(analytics_engine, "products", None),
                feature_store=feature_store,
            )
            logger.info(
                "Advanced Forecasting Engine initialized (SARIMA — demand, revenue, delay rate, category)"
            )
        except ImportError:
            logger.warning(
                "ForecastingEngine not available (missing statsmodels/prophet)"
            )
        except Exception as e:
            logger.warning(f"ForecastingEngine init failed: {e}")

        self.forecasting_agent = ForecastingAgent(
            analytics_engine=analytics_engine,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module,
            forecasting_engine=forecasting_engine,
        )

        self.data_query_agent = DataQueryAgent(
            data_wrapper=data_wrapper,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module,
        )

        logger.info(
            f"Agent Orchestrator initialized (LangChain Mode: {self.use_langchain}, RAG: {rag_module is not None})"
        )
        logger.info("  - Delay Agent: Ready")
        logger.info("  - Analytics Agent: Ready")
        logger.info("  - Forecasting Agent: Ready")
        logger.info("  - Data Query Agent: Ready")

    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """Thin delegate to QueryRouter (kept for backward compatibility)."""
        return self.router.route(query)

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Route query to appropriate specialized agent(s)
        Supports multi-intent queries that require multiple agents

        Args:
            query: User's query

        Returns:
            Response dictionary from the agent(s)
        """
        matched_pattern = detect_injection(query)
        if matched_pattern:
            logger.warning(
                f"Blocked suspected prompt injection (pattern: {matched_pattern!r})"
            )
            return {
                "response": REFUSAL_MESSAGE,
                "agent": "Guardrail",
                "success": False,
            }

        try:
            # NEW: Use Intent Classifier to determine if this is policy/data/mixed
            classification = self.intent_classifier.classify_query(query)
            logger.info(
                f"Query Classification: {classification['query_type']} | "
                f"Domain: {classification['domain']} | "
                f"Confidence: {classification['confidence']:.2f}"
            )
            logger.info(
                f"  → Use RAG: {classification['use_rag']} | Use Database: {classification['use_database']}"
            )

            # Analyze intent for agent routing
            intent = self.router.route(query)

            # Log which router was responsible
            logger.info(
                f"Final routing: agent={intent['agent']}, "
                f"confidence={intent['confidence']:.2f}, "
                f"routed_by={intent.get('routed_by', 'keyword')}"
            )

            # Add classification to intent
            intent["classification"] = classification

            # NEW: Handle multi-intent queries
            if intent.get("multi_intent", False) or intent["agent"] == "multi_agent":
                result = self._handle_multi_intent_query(query, intent)
            # Route to appropriate agent for single intent
            elif intent["agent"] == "delay":
                result = self.delay_agent.query(query, classification=classification)
            elif intent["agent"] == "forecasting":
                result = self.forecasting_agent.query(
                    query, classification=classification
                )
            elif intent["agent"] == "data_query":
                result = self.data_query_agent.query(
                    query, classification=classification
                )
            elif intent["agent"] == "comprehensive":
                # For comprehensive queries, gather from multiple agents
                result = self._handle_comprehensive_query(query)
            else:
                # Default to analytics agent
                result = self.analytics_agent.query(
                    query, classification=classification
                )

            # Add metadata
            result["intent"] = intent
            result["classification"] = classification
            result["orchestrator"] = (
                "Multi-Agent System" if self.use_langchain else "Rule-Based Router"
            )

            # Store in history
            self.conversation_history.append(
                {
                    "query": query,
                    "response": result,
                    "intent": intent,
                    "classification": classification,
                }
            )

            return result

        except Exception as e:
            logger.error(f"Error routing query: {e}")
            import traceback

            traceback.print_exc()
            return {
                "response": f"Error processing query: {e}",
                "agent": "Orchestrator",
                "success": False,
            }

    def _handle_multi_intent_query(
        self, query: str, intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced multi-intent handler with query decomposition and cross-agent insights

        Args:
            query: User's query
            intent: Intent analysis result with agents, sub-queries, and execution order

        Returns:
            Combined response from all relevant agents with synthesized insights
        """
        try:
            agents = intent.get("agents", [])
            sub_queries = intent.get("sub_queries", {})
            execution_order = intent.get("execution_order", agents)

            logger.info(
                f"Handling multi-intent query - invoking agents in order: {execution_order}"
            )
            logger.info(f"Sub-queries: {sub_queries}")

            results = {}
            agents_used = []
            context_data = {}  # Store intermediate results for context sharing

            # Execute agents in optimal order
            for agent_name in execution_order:
                if agent_name not in agents:
                    continue

                # Get agent-specific query (or use full query if not decomposed)
                agent_query = sub_queries.get(agent_name, query)

                logger.info(f"Calling {agent_name.title()} Agent: '{agent_query}'")

                # Route to appropriate agent
                if agent_name == "delay":
                    results["delay"] = self.delay_agent.query(agent_query)
                    agents_used.append("delay")

                    # Extract delay metrics for cross-agent insights
                    if results["delay"].get("success", True):
                        context_data["delay_rate"] = self._extract_delay_rate(
                            results["delay"].get("response", "")
                        )

                elif agent_name == "analytics":
                    results["analytics"] = self.analytics_agent.query(agent_query)
                    agents_used.append("analytics")

                    # Extract revenue metrics
                    if results["analytics"].get("success", True):
                        context_data["revenue_data"] = self._extract_revenue_data(
                            results["analytics"].get("response", "")
                        )

                elif agent_name == "forecasting":
                    results["forecasting"] = self.forecasting_agent.query(agent_query)
                    agents_used.append("forecasting")

                    # Extract forecast trends
                    if results["forecasting"].get("success", True):
                        context_data["forecast_trend"] = self._extract_forecast_trend(
                            results["forecasting"].get("response", "")
                        )

                elif agent_name == "data_query":
                    results["data_query"] = self.data_query_agent.query(agent_query)
                    agents_used.append("data_query")

            # Combine results in execution order (maintains logical flow)
            combined_response_parts = []

            # Section headers based on agent type — use markdown ## so Gradio renders them
            section_headers = {
                "delay": "## Delivery Performance",
                "analytics": "## Revenue & Analytics",
                "forecasting": "## Demand Forecast",
                "data_query": "## Data Query Results",
            }

            # Track which agents used RAG
            agents_with_rag = []

            # Add results in execution order
            for agent_name in agents_used:
                if agent_name in results and results[agent_name].get("success", True):
                    header = section_headers.get(agent_name, f"## {agent_name.upper()}")
                    body = results[agent_name].get("response", "No response").strip()
                    combined_response_parts.append(f"{header}\n\n{body}")

                    # Track RAG usage
                    if results[agent_name].get("used_rag", False):
                        agents_with_rag.append(agent_name)

            # Build final response with markdown horizontal rules between sections
            combined_response = "\n\n---\n\n".join(combined_response_parts)

            # Generate cross-agent insights if multiple domains analyzed
            if len(agents_used) >= 2:
                cross_insights = self._generate_cross_agent_insights(
                    context_data, agents_used
                )
                if cross_insights:
                    combined_response += "\n\n---\n\n## Cross-Domain Insights\n\n"
                    combined_response += cross_insights

            # Add clean agent execution summary at the end
            agent_summary_parts = [
                f"**Agents:** {', '.join([a.capitalize() for a in agents_used])}"
            ]
            agent_summary_parts.append(
                f"**Order:** {' → '.join([a.capitalize() for a in execution_order if a in agents_used])}"
            )
            if agents_with_rag:
                agent_summary_parts.append(
                    f"**RAG:** {', '.join([a.capitalize() for a in agents_with_rag])}"
                )
            combined_response += "\n\n---\n\n" + " | ".join(agent_summary_parts)

            return {
                "response": combined_response,
                "agent": f"Multi-Agent Orchestrator ({len(agents_used)} agents)",
                "success": True,
                "agents_used": agents_used,
                "agents_with_rag": agents_with_rag,
                "individual_results": results,
            }

        except Exception as e:
            logger.error(f"Error in multi-intent query: {e}")
            import traceback

            traceback.print_exc()
            return {
                "response": f"Error processing multi-intent query: {e}",
                "agent": "Orchestrator",
                "success": False,
            }

    def _extract_delay_rate(self, response: str) -> Optional[float]:
        """Extract delay rate percentage from delay agent response"""
        try:
            import re

            # Look for patterns like "6.28%" or "Delay Rate: 6.28%"
            match = re.search(r"delay rate.*?(\d+\.\d+)%", response.lower())
            if match:
                return float(match.group(1))
        except Exception as e:
            logger.debug(f"Could not extract delay rate: {e}")
        return None

    def _extract_revenue_data(self, response: str) -> Optional[Dict]:
        """Extract revenue metrics from analytics agent response"""
        try:
            import re

            data = {}
            # Look for revenue figures
            revenue_match = re.search(r"revenue.*?\$?([\d,]+)", response.lower())
            if revenue_match:
                data["total_revenue"] = revenue_match.group(1)
            return data if data else None
        except Exception as e:
            logger.debug(f"Could not extract revenue data: {e}")
        return None

    def _extract_forecast_trend(self, response: str) -> Optional[str]:
        """Extract forecast trend from forecasting agent response"""
        try:
            response_lower = response.lower()
            if (
                "increasing" in response_lower
                or "growing" in response_lower
                or "upward" in response_lower
            ):
                return "increasing"
            elif (
                "decreasing" in response_lower
                or "declining" in response_lower
                or "downward" in response_lower
            ):
                return "decreasing"
            elif "stable" in response_lower or "steady" in response_lower:
                return "stable"
        except Exception as e:
            logger.debug(f"Could not extract forecast trend: {e}")
        return None

    def _generate_cross_agent_insights(
        self, context_data: Dict, agents_used: List[str]
    ) -> str:
        """
        Generate insights that span multiple agent domains

        Args:
            context_data: Extracted metrics from agent responses
            agents_used: List of agents that were executed

        Returns:
            Cross-domain insights as formatted string
        """
        try:
            insights = []

            # Delay + Forecasting insight
            if "delay" in agents_used and "forecasting" in agents_used:
                delay_rate = context_data.get("delay_rate")
                forecast_trend = context_data.get("forecast_trend")

                if delay_rate and forecast_trend:
                    if delay_rate > 10 and forecast_trend == "increasing":
                        insights.append(
                            "**Supply Chain Risk**: High delay rate combined with increasing demand "
                            "may lead to customer dissatisfaction. Consider increasing safety stock or "
                            "improving supplier performance."
                        )
                    elif delay_rate < 5 and forecast_trend == "increasing":
                        insights.append(
                            "**Growth Opportunity**: Excellent delivery performance with growing demand. "
                            "Good position to capture market share. Monitor capacity for sustained performance."
                        )
                    elif delay_rate > 10 and forecast_trend == "decreasing":
                        insights.append(
                            "**Performance Issue**: High delays with declining demand may indicate "
                            "operational inefficiencies. Focus on process improvement to retain customers."
                        )

            # Delay + Analytics insight
            if "delay" in agents_used and "analytics" in agents_used:
                delay_rate = context_data.get("delay_rate")
                if delay_rate and delay_rate > 8:
                    insights.append(
                        "**Revenue Impact**: Current delay rate may be affecting customer satisfaction "
                        "and repeat purchase rates. Improving delivery performance could boost revenue."
                    )

            # Analytics + Forecasting insight
            if "analytics" in agents_used and "forecasting" in agents_used:
                forecast_trend = context_data.get("forecast_trend")
                if forecast_trend == "increasing":
                    insights.append(
                        "**Inventory Planning**: Growing demand forecast suggests reviewing inventory "
                        "levels and procurement schedules to avoid stockouts."
                    )
                elif forecast_trend == "decreasing":
                    insights.append(
                        "**Demand Planning**: Declining demand forecast indicates need to adjust "
                        "inventory levels to avoid excess stock and optimize working capital."
                    )

            # Triple agent insight (Delay + Analytics + Forecasting)
            if (
                len(agents_used) >= 3
                and "delay" in agents_used
                and "forecasting" in agents_used
            ):
                insights.append(
                    "**Holistic View**: Analysis spans delivery performance, financial metrics, and "
                    "demand forecasting. Use these combined insights for strategic planning and "
                    "operational optimization."
                )

            if insights:
                return "\n\n".join(insights)
            else:
                return ""

        except Exception as e:
            logger.error(f"Error generating cross-agent insights: {e}")
            return ""

    def _handle_comprehensive_query(self, query: str) -> Dict[str, Any]:
        """Handle comprehensive queries that need multiple agents"""
        try:
            logger.info("Handling comprehensive query - gathering data from all agents")

            # Gather analytics from all agents
            delay_result = self.delay_agent.query("Get delivery delay statistics")
            analytics_result = self.analytics_agent.query(
                "Get revenue and customer analysis"
            )
            forecast_result = self.forecasting_agent.query(
                "Forecast demand for 30 days"
            )

            # Combine results
            comprehensive_response = f"""# Comprehensive Supply Chain Analysis

## Delivery Performance

{delay_result.get('response', 'N/A').strip()}

---

## Revenue & Analytics

{analytics_result.get('response', 'N/A').strip()}

---

## Demand Forecast

{forecast_result.get('response', 'N/A').strip()}
"""

            return {
                "response": comprehensive_response,
                "agent": "Multi-Agent Orchestrator (Comprehensive)",
                "success": True,
                "agents_used": ["delay", "analytics", "forecasting"],
            }

        except Exception as e:
            logger.error(f"Error in comprehensive query: {e}")
            return {
                "response": f"Error generating comprehensive report: {e}",
                "agent": "Orchestrator",
                "success": False,
            }

    def query(
        self, user_query: str, show_agent: bool = True, show_metrics: bool = True
    ) -> str:
        """
        Main query interface - routes to appropriate agent and formats response

        Args:
            user_query: User's question
            show_agent: Whether to show agent info in response
            show_metrics: Whether to show performance metrics

        Returns:
            Formatted response string
        """
        # Import metrics tracker
        try:
            from scm_chatbot.services.metrics_tracker import get_metrics_tracker

            metrics_tracker = get_metrics_tracker()
        except Exception:
            metrics_tracker = None
            show_metrics = False

        # Start metrics tracking
        query_id = None
        start_time = time.time()
        if metrics_tracker:
            query_id = metrics_tracker.start_query(user_query, mode="agentic")
            metrics_tracker.add_data_source(query_id, "analytics_engine")

        try:
            # Route query
            result = self.route_query(user_query)

            # Track agents and RAG usage
            if metrics_tracker and query_id:
                agents_used = result.get("agents_used", [result.get("agent", "")])
                agents_with_rag = result.get("agents_with_rag", [])

                for agent in agents_used:
                    used_rag = agent in agents_with_rag or result.get("used_rag", False)
                    metrics_tracker.add_agent_execution(
                        query_id, agent, used_rag=used_rag
                    )

                if result.get("used_rag") or agents_with_rag:
                    metrics_tracker.add_data_source(query_id, "rag_documents")

            # Calculate hallucination score
            if metrics_tracker and query_id:
                # Assume low hallucination since we're using grounded analytics
                response_text_temp = result.get("response", "No response generated")
                metrics_tracker.calculate_hallucination_score(
                    query_id, response_text_temp, ground_truth_data={"analytics": True}
                )

            # End metrics tracking
            execution_time = time.time() - start_time
            if metrics_tracker and query_id:
                metrics_tracker.end_query(query_id, success=result.get("success", True))

            # Add metrics to result for UIFormatter
            if metrics_tracker and query_id and show_metrics:
                recent = metrics_tracker.get_recent_metrics(limit=1)
                if recent:
                    result["metrics"] = {
                        "execution_time": execution_time,
                        "latency_ms": recent[0].get("latency_ms", 0),
                        "data_sources": recent[0].get("data_sources_used", []),
                        "hallucination_score": recent[0].get("hallucination_score", 0),
                    }
            else:
                result["metrics"] = {"execution_time": execution_time}

            # Use UIFormatter to format the response with better readability
            response_text = UIFormatter.format_response(result)

            return response_text

        except Exception as e:
            logger.error(f"Error in orchestrator query: {e}")
            import traceback

            traceback.print_exc()

            # End metrics tracking with error
            if metrics_tracker and query_id:
                metrics_tracker.end_query(query_id, success=False, error=str(e))

            return f"❌ Error processing your query: {str(e)}"

    def _format_compact_metrics(self, metrics: Dict, single_line: bool = False) -> str:
        """
        Format compact metrics - only show fields with meaningful values

        Args:
            metrics: Metrics dictionary
            single_line: If True, format as pipe-separated single line

        Returns:
            Formatted metrics string
        """
        parts = []

        # Add latency (always show if available)
        if metrics.get("latency_ms"):
            parts.append(f"⏱️ {metrics['latency_ms']:.0f}ms")

        # Add data sources (compact icons only, no label)
        sources = metrics.get("data_sources_used", [])
        if sources and len(sources) > 0:
            source_icons = {"analytics_engine": "📊", "rag_documents": "📚"}
            source_str = "".join([source_icons.get(s, "💾") for s in sources])
            if source_str:
                parts.append(source_str)

        # Hallucination score - only show if Medium or High (Low is expected)
        halluc_score = metrics.get("hallucination_score", 0)
        if halluc_score >= 0.3:  # Only show if Medium or High
            risk_level = "Medium" if halluc_score < 0.6 else "High"
            parts.append(f"🎯 {risk_level}")

        if parts:
            separator = " | " if single_line else "\n"
            return "\n" + separator.join(parts)
        return ""

    def _build_agent_info(
        self,
        agent: str,
        orchestrator: str,
        intent: Dict,
        success: bool,
        result: Dict = None,
    ) -> str:
        """Build compact agent execution info footer"""
        info = f"\n\n{'─' * 60}\n"

        # Extract agent name (remove mode suffix for cleaner display)
        agent_name = agent.split(" (")[0] if "(" in agent else agent

        # Build compact single-line summary
        info += f"🤖 **Agent:** {agent_name}"

        # Add RAG indicator if used
        if result and result.get("used_rag", False):
            info += " | 📚 **RAG**"

        # Add status
        status_icon = "✅" if success else "❌"
        info += f" | {status_icon} **{'Success' if success else 'Failed'}**"

        # Metrics will be appended on next line by query method
        info += f"\n{'─' * 60}"
        return info

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
