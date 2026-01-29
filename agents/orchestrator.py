"""
Agent Orchestrator - Central controller for multi-agent SCM system
Routes queries to specialized agents based on intent
"""

import logging
from typing import Dict, Any, Optional, List
import os

logger = logging.getLogger(__name__)

try:
    from langchain_groq import ChatGroq
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available for Orchestrator")

from agents.delay_agent import DelayAgent
from agents.analytics_agent import AnalyticsAgent
from agents.forecasting_agent import ForecastingAgent
from agents.data_query_agent import DataQueryAgent


class AgentOrchestrator:
    """
    Central orchestrator that manages multiple specialized agents
    Routes queries to the appropriate agent based on intent analysis
    """

    def __init__(self, analytics_engine, data_wrapper, rag_module=None, use_langchain: bool = True):
        """
        Initialize Agent Orchestrator

        Args:
            analytics_engine: SCMAnalytics instance
            data_wrapper: Data wrapper with orders, customers, products
            rag_module: RAG module for semantic search (optional)
            use_langchain: Whether to use LangChain agentic framework
        """
        self.analytics = analytics_engine
        self.data = data_wrapper
        self.rag = rag_module
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.conversation_history = []

        # Initialize LLM client
        self.llm_client = None
        if self.use_langchain:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                try:
                    self.llm_client = ChatGroq(
                        model="llama-3.3-70b-versatile",
                        temperature=0.1,
                        api_key=api_key
                    )
                    logger.info("LLM client initialized for Orchestrator")
                except Exception as e:
                    logger.error(f"Failed to initialize LLM client: {e}")
                    self.use_langchain = False
            else:
                logger.warning("GROQ_API_KEY not found, LangChain agents disabled")
                self.use_langchain = False

        # Initialize specialized agents with RAG
        self.delay_agent = DelayAgent(
            analytics_engine=analytics_engine,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module
        )

        self.analytics_agent = AnalyticsAgent(
            analytics_engine=analytics_engine,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module
        )

        self.forecasting_agent = ForecastingAgent(
            analytics_engine=analytics_engine,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module
        )

        self.data_query_agent = DataQueryAgent(
            data_wrapper=data_wrapper,
            llm_client=self.llm_client,
            use_langchain=self.use_langchain,
            rag_module=rag_module
        )

        logger.info(f"Agent Orchestrator initialized (LangChain Mode: {self.use_langchain}, RAG: {rag_module is not None})")
        logger.info(f"  - Delay Agent: Ready")
        logger.info(f"  - Analytics Agent: Ready")
        logger.info(f"  - Forecasting Agent: Ready")
        logger.info(f"  - Data Query Agent: Ready")

    def analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine which agent(s) should handle it
        Supports multi-intent detection for compound queries

        Args:
            query: User's query string

        Returns:
            Dictionary with agent assignment(s) and confidence
        """
        query_lower = query.lower()

        intent = {
            'agent': None,
            'agents': [],  # NEW: List of agents for multi-intent queries
            'confidence': 0.0,
            'keywords': [],
            'multi_intent': False  # NEW: Flag for compound queries
        }

        # Delay-related keywords
        delay_keywords = ['delay', 'late', 'on-time', 'on time', 'delivery', 'shipped', 'arrived']
        delay_score = sum(1 for kw in delay_keywords if kw in query_lower)

        # Analytics keywords
        analytics_keywords = ['revenue', 'sales', 'profit', 'customer', 'product', 'performance']
        analytics_score = sum(1 for kw in analytics_keywords if kw in query_lower)

        # Forecasting keywords
        forecast_keywords = ['forecast', 'predict', 'future', 'demand', 'trend', 'projection']
        forecast_score = sum(1 for kw in forecast_keywords if kw in query_lower)

        # Data query keywords
        data_keywords = ['show', 'list', 'get', 'find', 'order id', 'customer id', 'record']
        data_score = sum(1 for kw in data_keywords if kw in query_lower)

        # Comprehensive report keywords
        comprehensive_keywords = ['comprehensive', 'report', 'overview', 'summary', 'all', 'everything']
        comprehensive_score = sum(1 for kw in comprehensive_keywords if kw in query_lower)

        # Determine which agent(s) to use
        scores = {
            'delay': delay_score,
            'analytics': analytics_score,
            'forecasting': forecast_score,
            'data_query': data_score,
            'comprehensive': comprehensive_score
        }

        max_score = max(scores.values())

        # NEW: Multi-intent detection
        # If multiple agents have scores >= threshold (e.g., 2), it's a compound query
        MULTI_INTENT_THRESHOLD = 2
        high_scoring_agents = [agent for agent, score in scores.items()
                               if score >= MULTI_INTENT_THRESHOLD and agent != 'comprehensive']

        if len(high_scoring_agents) > 1:
            # Multi-intent query detected
            intent['multi_intent'] = True
            intent['agents'] = high_scoring_agents
            intent['agent'] = 'multi_agent'  # Special marker
            intent['confidence'] = 0.8
            logger.info(f"Multi-intent query detected: {high_scoring_agents}")
        elif max_score == 0:
            # Default to analytics for general queries
            intent['agent'] = 'analytics'
            intent['agents'] = ['analytics']
            intent['confidence'] = 0.5
        else:
            # Single intent - get agent with highest score
            intent['agent'] = max(scores.items(), key=lambda x: x[1])[0]
            intent['agents'] = [intent['agent']]
            intent['confidence'] = max_score / 10.0  # Normalize confidence

        logger.info(f"Intent analysis: {intent['agent']} (confidence: {intent['confidence']:.2f}, agents: {intent['agents']})")

        return intent

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Route query to appropriate specialized agent(s)
        Supports multi-intent queries that require multiple agents

        Args:
            query: User's query

        Returns:
            Response dictionary from the agent(s)
        """
        try:
            # Analyze intent
            intent = self.analyze_intent(query)

            # NEW: Handle multi-intent queries
            if intent.get('multi_intent', False) or intent['agent'] == 'multi_agent':
                result = self._handle_multi_intent_query(query, intent['agents'])
            # Route to appropriate agent for single intent
            elif intent['agent'] == 'delay':
                result = self.delay_agent.query(query)
            elif intent['agent'] == 'forecasting':
                result = self.forecasting_agent.query(query)
            elif intent['agent'] == 'data_query':
                result = self.data_query_agent.query(query)
            elif intent['agent'] == 'comprehensive':
                # For comprehensive queries, gather from multiple agents
                result = self._handle_comprehensive_query(query)
            else:
                # Default to analytics agent
                result = self.analytics_agent.query(query)

            # Add metadata
            result['intent'] = intent
            result['orchestrator'] = 'Multi-Agent System' if self.use_langchain else 'Rule-Based Router'

            # Store in history
            self.conversation_history.append({
                'query': query,
                'response': result,
                'intent': intent
            })

            return result

        except Exception as e:
            logger.error(f"Error routing query: {e}")
            import traceback
            traceback.print_exc()
            return {
                'response': f"Error processing query: {e}",
                'agent': 'Orchestrator',
                'success': False
            }

    def _handle_multi_intent_query(self, query: str, agents: List[str]) -> Dict[str, Any]:
        """
        Handle multi-intent queries that require multiple specific agents

        Args:
            query: User's query
            agents: List of agent names to invoke

        Returns:
            Combined response from all relevant agents
        """
        try:
            logger.info(f"Handling multi-intent query - invoking agents: {agents}")

            results = {}
            agents_used = []

            # Route to each relevant agent
            if 'delay' in agents:
                logger.info("Calling Delay Agent for multi-intent query")
                results['delay'] = self.delay_agent.query(query)
                agents_used.append('delay')

            if 'analytics' in agents:
                logger.info("Calling Analytics Agent for multi-intent query")
                results['analytics'] = self.analytics_agent.query(query)
                agents_used.append('analytics')

            if 'forecasting' in agents:
                logger.info("Calling Forecasting Agent for multi-intent query")
                results['forecasting'] = self.forecasting_agent.query(query)
                agents_used.append('forecasting')

            if 'data_query' in agents:
                logger.info("Calling Data Query Agent for multi-intent query")
                results['data_query'] = self.data_query_agent.query(query)
                agents_used.append('data_query')

            # Combine results in logical order
            combined_response_parts = []

            # Section headers based on agent type
            section_headers = {
                'delay': '📊 DELIVERY PERFORMANCE',
                'analytics': '💰 REVENUE & ANALYTICS',
                'forecasting': '📈 DEMAND FORECAST',
                'data_query': '📋 DATA QUERY RESULTS'
            }

            # Track which agents used RAG
            agents_with_rag = []

            for agent_name in agents_used:
                if agent_name in results and results[agent_name].get('success', True):
                    combined_response_parts.append(f"{section_headers.get(agent_name, agent_name.upper())}\n{results[agent_name].get('response', 'No response')}")

                    # Track RAG usage
                    if results[agent_name].get('used_rag', False):
                        agents_with_rag.append(agent_name)

            # Build final response
            combined_response = "\n\n".join(combined_response_parts)

            # Add agent execution summary at the end
            agent_summary = "\n\n" + "─"*60 + "\n"
            agent_summary += f"🤖 **Agents Executed:** {', '.join([a.capitalize() for a in agents_used])}\n"
            if agents_with_rag:
                agent_summary += f"📚 **RAG Used By:** {', '.join([a.capitalize() for a in agents_with_rag])}\n"
            agent_summary += "─"*60

            combined_response += agent_summary

            return {
                'response': combined_response,
                'agent': f'Multi-Agent Orchestrator ({len(agents_used)} agents)',
                'success': True,
                'agents_used': agents_used,
                'agents_with_rag': agents_with_rag,
                'individual_results': results
            }

        except Exception as e:
            logger.error(f"Error in multi-intent query: {e}")
            import traceback
            traceback.print_exc()
            return {
                'response': f"Error processing multi-intent query: {e}",
                'agent': 'Orchestrator',
                'success': False
            }

    def _handle_comprehensive_query(self, query: str) -> Dict[str, Any]:
        """Handle comprehensive queries that need multiple agents"""
        try:
            logger.info("Handling comprehensive query - gathering data from all agents")

            # Gather analytics from all agents
            delay_result = self.delay_agent.query("Get delivery delay statistics")
            analytics_result = self.analytics_agent.query("Get revenue and customer analysis")
            forecast_result = self.forecasting_agent.query("Forecast demand for 30 days")

            # Combine results
            comprehensive_response = f"""🔍 Comprehensive Supply Chain Analysis

📊 DELIVERY PERFORMANCE
{delay_result.get('response', 'N/A')}

💰 REVENUE & ANALYTICS
{analytics_result.get('response', 'N/A')}

📈 DEMAND FORECAST
{forecast_result.get('response', 'N/A')}
"""

            return {
                'response': comprehensive_response,
                'agent': 'Multi-Agent Orchestrator (Comprehensive)',
                'success': True,
                'agents_used': ['delay', 'analytics', 'forecasting']
            }

        except Exception as e:
            logger.error(f"Error in comprehensive query: {e}")
            return {
                'response': f"Error generating comprehensive report: {e}",
                'agent': 'Orchestrator',
                'success': False
            }

    def query(self, user_query: str, show_agent: bool = True) -> str:
        """
        Main query interface - routes to appropriate agent and formats response

        Args:
            user_query: User's question
            show_agent: Whether to show agent info in response

        Returns:
            Formatted response string
        """
        try:
            # Route query
            result = self.route_query(user_query)

            # Format response
            response_text = result.get('response', 'No response generated')

            # Add agent info if requested
            if show_agent:
                agent_info = self._build_agent_info(
                    agent=result.get('agent', 'Unknown'),
                    orchestrator=result.get('orchestrator', 'Unknown'),
                    intent=result.get('intent', {}),
                    success=result.get('success', True),
                    result=result  # Pass full result for RAG and multi-agent info
                )
                response_text += agent_info

            return response_text

        except Exception as e:
            logger.error(f"Error in orchestrator query: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ Error processing your query: {str(e)}"

    def _build_agent_info(self, agent: str, orchestrator: str, intent: Dict, success: bool, result: Dict = None) -> str:
        """Build agent execution info footer with RAG and multi-agent details"""
        info = f"\n\n{'─' * 60}\n"
        info += f"🤖 **Agent**: {agent}\n"

        # Show individual agents if multi-agent query
        if result and 'agents_used' in result:
            agents_list = result['agents_used']
            info += f"👥 **Agents Executed**: {', '.join([a.title() for a in agents_list])}\n"

            # Show which agents used RAG
            if 'agents_with_rag' in result and result['agents_with_rag']:
                rag_agents = result['agents_with_rag']
                info += f"📚 **RAG Used By**: {', '.join([a.title() for a in rag_agents])}\n"
        elif result and result.get('used_rag', False):
            # Single agent that used RAG
            info += f"📚 **RAG**: Enabled (context retrieved from documents)\n"

        info += f"🎯 **Orchestrator**: {orchestrator}\n"

        # Show intent details
        if intent.get('multi_intent', False):
            info += f"📊 **Intent**: Multi-Intent Query (agents: {', '.join(intent.get('agents', []))})\n"
        else:
            info += f"📊 **Intent**: {intent.get('agent', 'unknown').title()} (confidence: {intent.get('confidence', 0.0):.2f})\n"

        info += f"✅ **Status**: {'Success' if success else 'Failed'}\n"
        info += f"{'─' * 60}"
        return info

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
