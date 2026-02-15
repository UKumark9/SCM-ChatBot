"""
Intent Classifier - Improved Query Type Detection
Distinguishes between policy questions (RAG) and data questions (database)
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Enhanced intent classifier that distinguishes between:
    - Policy questions (use RAG only)
    - Data questions (use database only)
    - Mixed questions (use both)
    """

    def __init__(self):
        # Policy question indicators
        self.policy_indicators = {
            'question_words': ['what is', 'what are', 'define', 'explain', 'describe', 'tell me about'],
            'policy_targets': ['policy', 'procedure', 'guideline', 'rule', 'standard', 'requirement',
                             'target', 'threshold', 'definition', 'classification', 'level', 'category'],
            'policy_concepts': ['severity level', 'critical delay', 'major delay', 'minor delay',
                               'kpi', 'key performance indicator', 'target rate', 'compliance'],
        }

        # Data question indicators
        self.data_indicators = {
            'metrics': ['rate', 'count', 'number', 'total', 'average', 'percentage', 'how many',
                       'how much', 'actual', 'current', 'real', 'measured',
                       'delivery', 'shipment', 'order', 'supplier'],
            'verbs': ['show', 'list', 'get', 'find', 'display', 'retrieve', 'calculate',
                     'compute', 'analyze', 'report'],
            'time_references': ['today', 'yesterday', 'this week', 'last month', 'current',
                               'recent', 'historical', 'trend', 'over time'],
            'data_requests': ['from database', 'from data', 'actual data', 'real data',
                             'calculated', 'measured value'],
            # Forecasting is always a data action — never a policy lookup
            'forecast_actions': ['forecast', 'predict', 'projection', 'demand forecast',
                                 'predict demand', 'future demand', 'demand prediction',
                                 'forecast demand', 'sarima', 'time series',
                                 'revenue forecast', 'forecast revenue', 'predict revenue',
                                 'delay rate forecast', 'forecast delay rate', 'predict delay',
                                 'category forecast', 'forecast category'],
        }

        # Domain detection (for agent routing)
        self.domain_keywords = {
            'delay': {
                'keywords': ['delay', 'late', 'on-time', 'on time', 'delivery', 'shipped', 'arrived'],
                'phrases': ['delivery delay', 'late delivery', 'delayed order', 'delivery performance']
            },
            'analytics': {
                'keywords': ['revenue', 'sales', 'profit', 'customer', 'performance', 'order value'],
                'phrases': ['total revenue', 'customer behavior', 'sales performance']
            },
            'forecasting': {
                'keywords': ['forecast', 'predict', 'future', 'demand', 'projection', 'estimate',
                             'sarima', 'prophet', 'time series', 'seasonal'],
                'phrases': ['demand forecast', 'predict demand', 'future demand',
                            'demand projection', 'forecast demand', 'show forecast',
                            'forecast with sarima', 'sarima forecast', 'time series forecast',
                            'revenue forecast', 'forecast revenue', 'predict revenue',
                            'delay rate forecast', 'forecast delay rate', 'predict delay rate',
                            'category forecast', 'forecast category', 'category demand forecast',
                            'each category', 'all categories', 'per category',
                            'every category', 'category comparison', 'compare categories',
                            'breakdown by category', 'each product category']
            },
            'data_query': {
                'keywords': ['show', 'list', 'get', 'find', 'display', 'retrieve'],
                'phrases': ['show me', 'list all', 'find order']
            }
        }

    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify query into policy, data, or mixed type

        Args:
            query: User's question

        Returns:
            Classification result with query_type, domain, and confidence
        """
        query_lower = query.lower()

        # Score policy vs data indicators
        policy_score = self._calculate_policy_score(query_lower)
        data_score = self._calculate_data_score(query_lower)

        # Determine query type
        if policy_score > data_score * 1.2:  # Policy signal dominates
            query_type = 'policy'
            confidence = min(0.5 + policy_score / 12.0, 0.95)
            use_rag = True
            use_database = False
        elif data_score > policy_score * 1.2:  # Data signal dominates
            query_type = 'data'
            confidence = min(0.5 + data_score / 12.0, 0.95)
            use_rag = False
            use_database = True
        elif policy_score > 2 and data_score > 2:  # Both signals present
            query_type = 'mixed'
            confidence = min(0.6 + (policy_score + data_score) / 20.0, 0.90)
            use_rag = True
            use_database = True
        else:
            # Default to data query; base confidence on whichever score is higher
            query_type = 'data'
            best_score = max(policy_score, data_score)
            confidence = min(0.5 + best_score / 12.0, 0.80)
            use_rag = False
            use_database = True

        # Detect domain
        domain = self._detect_domain(query_lower)

        result = {
            'query_type': query_type,  # 'policy', 'data', or 'mixed'
            'domain': domain,  # 'delay', 'analytics', 'forecasting', 'data_query'
            'confidence': confidence,
            'use_rag': use_rag,
            'use_database': use_database,
            'policy_score': policy_score,
            'data_score': data_score,
            'reasoning': self._explain_classification(query_type, policy_score, data_score, domain)
        }

        logger.info(f"Query classification: {query_type} ({domain}) - confidence: {confidence:.2f}")
        logger.debug(f"Scores - Policy: {policy_score}, Data: {data_score}")

        return result

    def _calculate_policy_score(self, query_lower: str) -> float:
        """Calculate policy question score"""
        score = 0.0

        # Check for question words + policy targets
        for qw in self.policy_indicators['question_words']:
            if qw in query_lower:
                score += 2.0  # Strong policy signal

        # Check for policy-specific terms
        for target in self.policy_indicators['policy_targets']:
            if target in query_lower:
                score += 3.0  # Very strong policy signal

        # Check for policy concepts
        for concept in self.policy_indicators['policy_concepts']:
            if concept in query_lower:
                score += 2.5

        return score

    def _calculate_data_score(self, query_lower: str) -> float:
        """Calculate data question score"""
        score = 0.0

        # Check for metric keywords
        for metric in self.data_indicators['metrics']:
            if metric in query_lower:
                score += 3.0  # Strong data signal

        # Check for action verbs
        for verb in self.data_indicators['verbs']:
            if verb in query_lower:
                score += 2.0

        # Check for time references
        for time_ref in self.data_indicators['time_references']:
            if time_ref in query_lower:
                score += 2.5  # Indicates current/historical data request

        # Check for explicit data requests
        for data_req in self.data_indicators['data_requests']:
            if data_req in query_lower:
                score += 4.0  # Very strong data signal

        # Forecasting terms are unambiguously data actions — override any policy signal
        for fc_term in self.data_indicators['forecast_actions']:
            if fc_term in query_lower:
                score += 5.0  # Strongest possible data signal

        return score

    def _detect_domain(self, query_lower: str) -> str:
        """Detect which domain/agent should handle the query"""
        domain_scores = {}

        for domain, patterns in self.domain_keywords.items():
            score = 0
            # Keyword matches
            score += sum(1 for kw in patterns['keywords'] if kw in query_lower)
            # Phrase matches (stronger signal)
            score += sum(2 for phrase in patterns['phrases'] if phrase in query_lower)
            domain_scores[domain] = score

        # Return domain with highest score
        if not any(domain_scores.values()):
            return 'analytics'  # Default

        return max(domain_scores.items(), key=lambda x: x[1])[0]

    def _explain_classification(self, query_type: str, policy_score: float,
                                data_score: float, domain: str) -> str:
        """Generate human-readable reasoning for classification"""
        if query_type == 'policy':
            return f"Policy question detected (score: {policy_score:.1f} vs {data_score:.1f}). Using RAG for policy documents."
        elif query_type == 'data':
            return f"Data question detected (score: {data_score:.1f} vs {policy_score:.1f}). Using database query."
        else:
            return f"Mixed question detected (policy: {policy_score:.1f}, data: {data_score:.1f}). Using both RAG and database."


# Example usage and testing
if __name__ == "__main__":
    classifier = IntentClassifier()

    test_queries = [
        "What is the delivery delay rate?",  # DATA - asking for actual metric
        "What are severity levels?",  # POLICY - asking for policy definition
        "What is the target on-time delivery rate?",  # POLICY - asking for target
        "Show me all delayed orders",  # DATA - list request
        "What is the policy on critical delays?",  # POLICY - explicit policy ask
        "How many orders were delayed this month?",  # DATA - metric + time
        "What is the definition of major delay?",  # POLICY - definition
        "Calculate the current delay rate from database",  # DATA - explicit data request
    ]

    print("Testing Intent Classifier:")
    print("=" * 80)

    for query in test_queries:
        result = classifier.classify_query(query)
        print(f"\nQuery: {query}")
        print(f"Type: {result['query_type'].upper()} | Domain: {result['domain']}")
        print(f"RAG: {result['use_rag']} | Database: {result['use_database']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
