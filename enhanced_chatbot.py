"""
Enhanced SCM Chatbot with RAG and LLM Integration
Provides intelligent responses using semantic search and natural language understanding
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def convert_to_serializable(obj: Any) -> Any:
    """Convert pandas/numpy objects to JSON-serializable types"""
    if isinstance(obj, dict):
        return {str(k): convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (pd.Period, pd.Timestamp)):
        return str(obj)
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq not available. Install with: pip install groq")


class PromptTemplates:
    """Comprehensive prompt templates for SCM queries"""

    SYSTEM_PROMPT = """You are an expert Supply Chain Management (SCM) analyst assistant.
You provide accurate, data-driven insights about supply chain operations.

IMPORTANT - Response Detail Level:
- For SIMPLE questions (e.g., "What is X?", "How many?"), provide ONLY the direct answer with the key metric
- For MODERATE questions (e.g., "Show me X", "Analyze X"), provide the answer plus 2-3 key supporting points
- For COMPLEX questions (e.g., "What insights?", "Explain why?", "Recommendations?"), provide comprehensive analysis

Examples:
Question: "What is the delivery delay rate?"
Answer: "The delivery delay rate is 6.28%."

Question: "Show delivery performance"
Answer: "Delivery Performance:
- Delay Rate: 6.28%
- On-Time Rate: 93.72%
- Total Orders: 89,316"

Question: "What insights can you provide about delivery delays?"
Answer: [Full analysis with insights, trends, recommendations]

Match your response length and detail to the question's complexity."""

    QUERY_ANALYSIS_PROMPT = """Analyze this supply chain query and extract:
1. Query Type (delivery, revenue, product, customer, forecast, supplier, comprehensive)
2. Specific Metrics Requested
3. Time Period (if mentioned)
4. Geographic Focus (if mentioned)
5. Any filters or conditions

Query: {query}

Provide analysis in JSON format:
{{
    "query_type": "...",
    "metrics": [...],
    "time_period": "...",
    "geographic_focus": "...",
    "filters": {{}}
}}"""

    ANSWER_WITH_CONTEXT = """Based on the supply chain data below, answer the user's question.

{context_section}

Analytics Results:
{analytics_data}

User Question: {query}

Response Guidelines:
1. ANALYZE the question's complexity level:
   - SIMPLE (single metric): Give just the direct answer (1 sentence)
   - MODERATE (show/analyze): Give answer + 2-4 key metrics
   - COMPLEX (insights/why/recommendations): Give full analysis

2. **IMPORTANT - Source Priority**:
   - If the question asks "What is/are..." about policies, definitions, severity levels, classifications, or guidelines → Answer ONLY from Policy Documents (ignore analytics)
   - If the question asks about actual metrics, rates, counts, or current data → Answer from Analytics Results
   - If the question asks to compare or combine both → Use both sources

3. For SIMPLE questions:
   - Answer format: "The [metric] is [value]."
   - Example: "The delivery delay rate is 6.28%."
   - DO NOT add extra sections, explanations, or recommendations

4. For MODERATE questions:
   - Brief intro + bullet points with key metrics
   - Keep under 5 lines

5. For COMPLEX questions:
   - Full analysis with insights and recommendations
   - Use sections and detailed formatting

Match your response to the question's level. If the question is simple, keep the answer simple."""

    CONVERSATIONAL_PROMPT = """You are a helpful SCM chatbot. The user asked: "{query}"

Previous conversation context:
{conversation_history}

Current data insights:
{insights}

Provide a natural, conversational response that:
- Answers the question directly
- Includes relevant metrics and data
- Maintains conversational flow
- Offers to provide more details if needed"""


class EnhancedSCMChatbot:
    """Enhanced SCM Chatbot with RAG and LLM capabilities"""

    def __init__(self, analytics_engine, rag_module=None, use_llm: bool = True):
        """
        Initialize enhanced chatbot

        Args:
            analytics_engine: SCMAnalytics instance
            rag_module: RAGModule instance (optional)
            use_llm: Whether to use LLM for responses
        """
        self.analytics = analytics_engine
        self.rag = rag_module
        self.use_llm = use_llm and GROQ_AVAILABLE
        self.conversation_history = []
        self.templates = PromptTemplates()

        # Initialize Groq client if available
        if self.use_llm:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.llm_client = Groq(api_key=api_key)
                logger.info("LLM integration enabled with Groq")
            else:
                self.use_llm = False
                logger.warning("GROQ_API_KEY not found, LLM features disabled")
        else:
            self.llm_client = None
            logger.info("Using rule-based responses (LLM disabled)")

    def analyze_query_intent(self, query: str) -> Dict:
        """Analyze query to determine intent and required analytics"""
        query_lower = query.lower()

        intent = {
            'type': 'general',
            'requires_analytics': [],
            'geographic': None,
            'time_based': False,
            'comparison': False
        }

        # Determine query type and required analytics
        if any(word in query_lower for word in ['delay', 'delayed', 'late', 'on-time', 'on time', 'delivery']):
            intent['type'] = 'delivery'
            intent['requires_analytics'].append('delivery_delays')

        if any(word in query_lower for word in ['revenue', 'sales', 'income', 'earnings', 'profit']):
            intent['type'] = 'revenue'
            intent['requires_analytics'].append('revenue_trends')

        if any(word in query_lower for word in ['product', 'item', 'category', 'inventory']):
            intent['type'] = 'product'
            intent['requires_analytics'].append('product_performance')

        if any(word in query_lower for word in ['customer', 'buyer', 'client']):
            intent['type'] = 'customer'
            intent['requires_analytics'].append('customer_behavior')

        if any(word in query_lower for word in ['forecast', 'predict', 'future', 'trend', 'projection']):
            intent['type'] = 'forecast'
            intent['requires_analytics'].append('demand_forecast')

        if any(word in query_lower for word in ['comprehensive', 'report', 'overview', 'summary', 'all']):
            intent['type'] = 'comprehensive'
            intent['requires_analytics'].append('comprehensive_report')

        # Check for geographic focus
        if any(word in query_lower for word in ['state', 'region', 'location', 'where', 'which state']):
            intent['geographic'] = True

        # Check for time-based queries
        if any(word in query_lower for word in ['month', 'year', 'trend', 'over time', 'growth']):
            intent['time_based'] = True

        # Check for comparisons
        if any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference', 'better', 'worse']):
            intent['comparison'] = True

        # Determine question complexity level
        intent['complexity'] = self._detect_complexity(query_lower)

        return intent

    def _detect_complexity(self, query_lower: str) -> str:
        """Detect if question is simple, moderate, or complex"""

        # SIMPLE: Direct "what is" questions asking for single metric
        simple_patterns = [
            'what is the',
            'what is',
            'what\'s the',
            'how many',
            'how much',
            'give me the',
            'tell me the'
        ]

        # Check if it's a simple question (single metric request)
        if any(pattern in query_lower for pattern in simple_patterns):
            # And doesn't ask for analysis/insights
            if not any(word in query_lower for word in ['why', 'how', 'insight', 'recommend', 'explain', 'analyze', 'compare']):
                # And is short (likely asking for one thing)
                if len(query_lower.split()) <= 10:
                    return 'simple'

        # COMPLEX: Questions asking for insights, explanations, recommendations
        complex_patterns = [
            'insight', 'why', 'how can', 'explain', 'recommend',
            'what should', 'help me understand', 'tell me about',
            'what are the main', 'what drives', 'root cause'
        ]

        if any(pattern in query_lower for pattern in complex_patterns):
            return 'complex'

        # MODERATE: Everything else (show, analyze, list, etc.)
        return 'moderate'

    def _extract_key_metric(self, data: Dict, intent: Dict, query: str) -> Dict:
        """Extract only the key metric for simple questions"""
        query_lower = query.lower()

        # For delivery queries
        if intent['type'] == 'delivery' and 'delivery' in data:
            if 'delay rate' in query_lower:
                return {'delay_rate_percentage': data['delivery']['delay_rate_percentage']}
            elif 'on-time' in query_lower or 'on time' in query_lower:
                on_time_rate = 100 - data['delivery']['delay_rate_percentage']
                return {'on_time_rate_percentage': on_time_rate}
            else:
                # Return just the core metrics
                return {
                    'delay_rate_percentage': data['delivery']['delay_rate_percentage'],
                    'total_orders': data['delivery']['total_orders'],
                    'delayed_orders': data['delivery']['delayed_orders']
                }

        # For revenue queries
        if intent['type'] == 'revenue' and 'revenue' in data:
            if 'total' in query_lower:
                return {'total_revenue': data['revenue']['total_revenue']}
            else:
                return {
                    'total_revenue': data['revenue']['total_revenue'],
                    'average_order_value': data['revenue']['average_order_value']
                }

        # For other types, return simplified data
        return data

    def gather_analytics_data(self, intent: Dict) -> Dict:
        """Gather required analytics data based on intent"""
        analytics_data = {}

        try:
            if 'delivery_delays' in intent['requires_analytics']:
                analytics_data['delivery'] = self.analytics.analyze_delivery_delays()

            if 'revenue_trends' in intent['requires_analytics']:
                analytics_data['revenue'] = self.analytics.analyze_revenue_trends()

            if 'product_performance' in intent['requires_analytics']:
                analytics_data['product'] = self.analytics.analyze_product_performance()

            if 'customer_behavior' in intent['requires_analytics']:
                analytics_data['customer'] = self.analytics.analyze_customer_behavior()

            if 'demand_forecast' in intent['requires_analytics']:
                analytics_data['forecast'] = self.analytics.forecast_demand(periods=30)

            if 'comprehensive_report' in intent['requires_analytics']:
                analytics_data['comprehensive'] = self.analytics.generate_comprehensive_report()

        except Exception as e:
            logger.error(f"Error gathering analytics: {e}")

        return analytics_data

    def retrieve_context(self, query: str) -> str:
        """Retrieve relevant context using RAG"""
        if not self.rag:
            return ""

        try:
            context = self.rag.retrieve_context(query)
            return context
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""

    def generate_llm_response(self, query: str, context: str, analytics_data: Dict, intent: Dict) -> str:
        """Generate response using LLM"""
        if not self.use_llm or not self.llm_client:
            return None

        try:
            # Convert analytics data to JSON-serializable format
            serializable_data = convert_to_serializable(analytics_data)

            # Get complexity level
            complexity = intent.get('complexity', 'moderate')

            # Simplify analytics data for simple questions (only include relevant parts)
            if complexity == 'simple':
                # Extract only the key metric being asked about
                serializable_data = self._extract_key_metric(serializable_data, intent, query)

            # Format analytics data for prompt
            analytics_summary = json.dumps(serializable_data, indent=2, default=str)

            # Format RAG context if available
            context_section = ""
            if context and len(context.strip()) > 0:
                context_section = f"""Policy Documents (from knowledge base):
{context}

---
"""

            # Add complexity hint to the prompt
            complexity_hint = {
                'simple': "\n\nIMPORTANT: This is a SIMPLE question. Provide ONLY the direct answer in 1 sentence. Do NOT add explanations, recommendations, or extra details.",
                'moderate': "\n\nThis is a MODERATE question. Provide a brief answer with 2-4 key metrics.",
                'complex': "\n\nThis is a COMPLEX question. Provide comprehensive analysis with insights and recommendations."
            }

            # Create prompt
            user_prompt = self.templates.ANSWER_WITH_CONTEXT.format(
                context_section=context_section,
                analytics_data=analytics_summary,
                query=query
            ) + complexity_hint.get(complexity, '')

            # Call LLM
            response = self.llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Current Groq model (updated 2026)
                messages=[
                    {"role": "system", "content": self.templates.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1024
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return None

    def generate_rule_based_response(self, query: str, intent: Dict, analytics_data: Dict) -> str:
        """Generate response using rule-based system (fallback)"""
        query_lower = query.lower()

        # Delivery queries
        if intent['type'] == 'delivery':
            delivery_data = analytics_data.get('delivery', {})
            if not delivery_data:
                return "Delivery data not available."

            # Check for state-specific queries
            if intent.get('geographic'):
                delays_by_state = delivery_data.get('delays_by_state', {})
                if delays_by_state:
                    state_delays = sorted(
                        [(state, rate * 100) for state, rate in delays_by_state.items()],
                        key=lambda x: x[1],
                        reverse=True
                    )

                    response = "📍 **Delivery Delays by State:**\n\n"
                    for i, (state, rate) in enumerate(state_delays[:10], 1):
                        response += f"{i}. **{state}**: {rate:.1f}% delay rate\n"
                    return response

            # Check for on-time queries
            elif 'on-time' in query_lower or 'on time' in query_lower:
                on_time_rate = 100 - delivery_data.get('delay_rate_percentage', 0)
                total = delivery_data.get('total_orders', 0)
                delayed = delivery_data.get('delayed_orders', 0)
                on_time = total - delayed

                return f"""✅ **On-Time Delivery Performance:**

- **On-Time Deliveries:** {on_time:,}
- **On-Time Rate:** {on_time_rate:.2f}%
- **Total Orders:** {total:,}
- **Delayed Orders:** {delayed:,}

**Performance Grade:** {'🌟 Excellent' if on_time_rate >= 95 else '✓ Good' if on_time_rate >= 90 else '⚠️ Needs Improvement'}"""

            # Default delivery response
            else:
                return f"""📊 **Delivery Performance Analysis:**

- **Total Orders:** {delivery_data.get('total_orders', 0):,}
- **Delayed Orders:** {delivery_data.get('delayed_orders', 0):,}
- **Delay Rate:** {delivery_data.get('delay_rate_percentage', 0):.2f}%
- **On-Time Rate:** {100 - delivery_data.get('delay_rate_percentage', 0):.2f}%
- **Average Delay:** {delivery_data.get('average_delay_days', 0):.1f} days
- **Maximum Delay:** {delivery_data.get('max_delay_days', 0):.0f} days
- **Median Delay:** {delivery_data.get('median_delay_days', 0):.1f} days"""

        # Revenue queries
        elif intent['type'] == 'revenue':
            revenue_data = analytics_data.get('revenue', {})
            if not revenue_data:
                return "Revenue data not available."

            return f"""💰 **Revenue Analysis:**

- **Total Revenue:** ${revenue_data.get('total_revenue', 0):,.2f}
- **Average Order Value:** ${revenue_data.get('average_order_value', 0):.2f}
- **Monthly Growth Rate:** {revenue_data.get('average_monthly_growth_rate', 0):.2f}%
- **Highest Revenue Month:** {revenue_data.get('highest_revenue_month', 'N/A')}
- **Lowest Revenue Month:** {revenue_data.get('lowest_revenue_month', 'N/A')}"""

        # Product queries
        elif intent['type'] == 'product':
            product_data = analytics_data.get('product', {})
            if not product_data:
                return "Product data not available."

            return f"""📦 **Product Performance Analysis:**

- **Unique Products:** {product_data.get('total_unique_products', 0):,}
- **Total Items Sold:** {product_data.get('total_items_sold', 0):,}
- **Average Product Price:** ${product_data.get('average_product_price', 0):.2f}"""

        # Customer queries
        elif intent['type'] == 'customer':
            customer_data = analytics_data.get('customer', {})
            if not customer_data:
                return "Customer data not available."

            return f"""👥 **Customer Behavior Analysis:**

- **Total Customers:** {customer_data.get('total_customers', 0):,}
- **Active Customers:** {customer_data.get('active_customers', 0):,}
- **Average Orders per Customer:** {customer_data.get('average_orders_per_customer', 0):.2f}
- **Repeat Customer Rate:** {customer_data.get('repeat_customer_rate', 0):.1f}%
- **Average Customer Lifetime Value:** ${customer_data.get('average_customer_lifetime_value', 0):.2f}"""

        # Forecast queries
        elif intent['type'] == 'forecast':
            forecast_data = analytics_data.get('forecast', {})
            if not forecast_data:
                return "Forecast data not available."

            return f"""📈 **Demand Forecast (30 Days):**

- **Historical Average:** {forecast_data.get('historical_average', 0):.1f} items/day
- **Trend:** {forecast_data.get('trend', 'unknown').title()}
- **Model Accuracy (MAPE):** {forecast_data.get('model_metrics', {}).get('mape', 0):.2f}%
- **R² Score:** {forecast_data.get('model_metrics', {}).get('r_squared', 0):.3f}"""

        # Comprehensive report
        elif intent['type'] == 'comprehensive':
            comp_data = analytics_data.get('comprehensive', {})
            if not comp_data:
                return "Unable to generate comprehensive report."

            delivery = comp_data.get('delivery_analysis', {})
            revenue = comp_data.get('revenue_analysis', {})
            product = comp_data.get('product_analysis', {})
            customer = comp_data.get('customer_analysis', {})

            return f"""📋 **Comprehensive Supply Chain Report**

## Delivery Performance
- **Delay Rate:** {delivery.get('delay_rate_percentage', 0):.2f}%
- **Average Delay:** {delivery.get('average_delay_days', 0):.1f} days

## Revenue Metrics
- **Total Revenue:** ${revenue.get('total_revenue', 0):,.2f}
- **Average Order Value:** ${revenue.get('average_order_value', 0):.2f}
- **Growth Rate:** {revenue.get('average_monthly_growth_rate', 0):.2f}%

## Product Performance
- **Unique Products:** {product.get('total_unique_products', 0):,}
- **Total Items Sold:** {product.get('total_items_sold', 0):,}

## Customer Insights
- **Active Customers:** {customer.get('active_customers', 0):,}
- **Repeat Rate:** {customer.get('repeat_customer_rate', 0):.1f}%
- **Avg CLV:** ${customer.get('average_customer_lifetime_value', 0):.2f}"""

        # Default help message
        return """🤖 **SCM Chatbot - How can I help?**

I can provide insights on:

📊 **Delivery Performance:**
- "What is the delivery delay rate?"
- "Which states have the most delays?"
- "Show on-time delivery performance"

💰 **Revenue & Sales:**
- "Show revenue analysis"
- "What are the revenue trends?"
- "Which month had highest revenue?"

📈 **Forecasting:**
- "Forecast demand for next 30 days"
- "What are the demand trends?"

📦 **Products:**
- "Analyze product performance"
- "What are the top selling products?"

👥 **Customers:**
- "Analyze customer behavior"
- "What is the repeat customer rate?"

📋 **Comprehensive:**
- "Generate comprehensive report"
- "Give me a complete overview"

What would you like to know?"""

    def query(self, user_query: str, show_agent: bool = True, use_rag: bool = True) -> str:
        """
        Process user query and generate response

        Args:
            user_query: User's question
            show_agent: Whether to show agent info in response
            use_rag: Whether to use RAG for context retrieval (default: True)

        Returns:
            Response string
        """
        # Track metrics for enhanced mode
        import time as _time
        _metrics_tracker = None
        _query_id = None
        try:
            from metrics_tracker import get_metrics_tracker
            _metrics_tracker = get_metrics_tracker()
            _query_id = _metrics_tracker.start_query(user_query, mode='enhanced')
            _metrics_tracker.add_data_source(_query_id, 'analytics_engine')
        except Exception:
            pass

        try:
            logger.info(f"Processing query: {user_query} (use_rag={use_rag})")

            # Analyze query intent
            intent = self.analyze_query_intent(user_query)
            logger.info(f"Query intent: {intent}")

            # Gather analytics data
            analytics_data = self.gather_analytics_data(intent)

            # Retrieve context using RAG if enabled and available
            context = self.retrieve_context(user_query) if (self.rag and use_rag) else ""
            if not use_rag:
                logger.info("RAG disabled for this query (user preference)")

            agent_info = ""
            response_text = ""

            # Try LLM response first
            if self.use_llm:
                llm_response = self.generate_llm_response(user_query, context, analytics_data, intent)
                if llm_response:
                    response_text = llm_response

                    # Build agent info
                    if show_agent:
                        agent_info = self._build_agent_info(
                            agent="Enhanced AI (LLM)",
                            model="Llama 3.3 70B",
                            complexity=intent.get('complexity', 'moderate'),
                            rag_used=bool(context and self.rag)
                        )

                    # Add to conversation history
                    self.conversation_history.append({
                        'query': user_query,
                        'response': response_text,
                        'intent': intent,
                        'agent': 'llm'
                    })

                    if _metrics_tracker and _query_id:
                        rag_actually_used = bool(context and self.rag and use_rag)
                        if rag_actually_used:
                            _metrics_tracker.add_data_source(_query_id, 'rag_documents')
                        _metrics_tracker.add_agent_execution(_query_id, 'enhanced', used_rag=rag_actually_used)
                        _metrics_tracker.calculate_hallucination_score(_query_id, response_text, ground_truth_data={'analytics': True})
                        _metrics_tracker.end_query(_query_id, success=True)

                    return response_text + agent_info

            # Fallback to rule-based response
            # If RAG context is available, synthesize it via LLM for conceptual questions
            rag_used_fallback = False
            if context and len(context.strip()) > 20 and 'no relevant' not in context.lower() and self.llm_client:
                try:
                    synth = self.llm_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": (
                                "You are a supply chain management expert. Using ONLY the provided document excerpts, "
                                "give a clear, concise answer to the user's question. "
                                "Use bullet points and bold key terms for readability. "
                                "If the documents don't fully answer the question, say what you found and note the gap. "
                                "Do NOT mention document numbers or relevance scores."
                            )},
                            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {user_query}"}
                        ],
                        temperature=0.3,
                        max_tokens=1024
                    )
                    response_text = synth.choices[0].message.content
                    rag_used_fallback = True
                except Exception as e:
                    logger.warning(f"RAG synthesis failed in rule-based fallback: {e}")
                    response_text = self.generate_rule_based_response(user_query, intent, analytics_data)
            else:
                response_text = self.generate_rule_based_response(user_query, intent, analytics_data)

            # Build agent info
            if show_agent:
                agent_info = self._build_agent_info(
                    agent="Rule-Based Engine" + (" + RAG" if rag_used_fallback else ""),
                    model="Pattern Matching",
                    complexity=intent.get('complexity', 'moderate'),
                    rag_used=rag_used_fallback
                )

            # Add to conversation history
            self.conversation_history.append({
                'query': user_query,
                'response': response_text,
                'intent': intent,
                'agent': 'rule-based'
            })

            if _metrics_tracker and _query_id:
                rag_actually_used = bool(context and self.rag and use_rag)
                if rag_actually_used:
                    _metrics_tracker.add_data_source(_query_id, 'rag_documents')
                _metrics_tracker.add_agent_execution(_query_id, 'enhanced', used_rag=rag_actually_used)
                _metrics_tracker.calculate_hallucination_score(_query_id, response_text, ground_truth_data={'analytics': True})
                _metrics_tracker.end_query(_query_id, success=True)

            return response_text + agent_info

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            import traceback
            traceback.print_exc()
            if _metrics_tracker and _query_id:
                _metrics_tracker.end_query(_query_id, success=False, error=str(e))
            return f"❌ Error processing your query: {str(e)}\n\nPlease try rephrasing your question."

    def _build_agent_info(self, agent: str, model: str, complexity: str, rag_used: bool) -> str:
        """Build agent execution information footer"""
        parts = [agent, model, complexity.title()]
        if rag_used:
            parts.append("Policy Docs")
        body = " | ".join(parts)
        return (
            f'\n\n<p style="font-size:0.75em;font-style:italic;opacity:0.6;margin-top:4px">'
            f'{body}</p>'
        )

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
