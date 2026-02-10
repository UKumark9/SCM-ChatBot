"""
Response Formatter - Enhanced Output with Metrics
"""

import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format agent responses with metrics and timing"""

    @staticmethod
    def format_response(result: Dict[str, Any], query: str, start_time: float) -> str:
        """
        Format agent response with enhanced metrics

        Args:
            result: Agent result dictionary
            query: Original user query
            start_time: Query start timestamp

        Returns:
            Formatted response string
        """
        execution_time = time.time() - start_time

        # Extract data from result
        response = result.get('response', 'No response')
        agent = result.get('agent', 'Unknown')
        success = result.get('success', True)
        classification = result.get('classification', {})
        used_rag = result.get('used_rag', False)

        # Build formatted output
        output_parts = []

        # Main response
        output_parts.append(response)

        # Add separator
        output_parts.append("\n" + "─" * 60)

        # Query Classification
        query_type = classification.get('query_type', 'unknown')
        domain = classification.get('domain', 'unknown')
        confidence = classification.get('confidence', 0.0)

        classification_line = f"📊 **Type:** {query_type.title()}"
        classification_line += f" | **Domain:** {domain.title()}"
        classification_line += f" | **Confidence:** {confidence:.0%}"

        output_parts.append(classification_line)

        # Execution Details
        execution_line = f"⏱️  **Time:** {execution_time:.2f}s"
        execution_line += f" | 🤖 **Agent:** {agent}"

        if used_rag:
            execution_line += " | 📚 **RAG**"

        status_icon = "✅" if success else "❌"
        execution_line += f" | {status_icon} **{'Success' if success else 'Failed'}**"

        output_parts.append(execution_line)

        # Data Source
        sources = []
        if classification.get('use_rag'):
            sources.append("Policy Documents")
        if classification.get('use_database'):
            sources.append("Database")

        if sources:
            source_line = f"📁 **Sources:** {', '.join(sources)}"
            output_parts.append(source_line)

        # Metrics (if available)
        metrics = result.get('metrics', {})
        if metrics:
            metrics_line = ResponseFormatter._format_metrics(metrics)
            if metrics_line:
                output_parts.append(metrics_line)

        # Close separator
        output_parts.append("─" * 60)

        return "\n".join(output_parts)

    @staticmethod
    def _format_metrics(metrics: Dict[str, Any]) -> str:
        """Format metrics section"""
        if not metrics:
            return ""

        metrics_parts = []

        # Data metrics
        if 'row_count' in metrics:
            metrics_parts.append(f"Rows: {metrics['row_count']}")

        if 'delay_count' in metrics:
            metrics_parts.append(f"Delayed: {metrics['delay_count']}")

        if 'delay_rate' in metrics:
            metrics_parts.append(f"Rate: {metrics['delay_rate']:.1f}%")

        # RAG metrics
        if 'documents_retrieved' in metrics:
            metrics_parts.append(f"Docs: {metrics['documents_retrieved']}")

        if 'relevance_avg' in metrics:
            metrics_parts.append(f"Relevance: {metrics['relevance_avg']:.2f}")

        if metrics_parts:
            return f"📈 **Metrics:** {' | '.join(metrics_parts)}"

        return ""

    @staticmethod
    def format_error(error_msg: str, query: str, start_time: float) -> str:
        """Format error response"""
        execution_time = time.time() - start_time

        output = f"❌ **Error:** {error_msg}\n\n"
        output += "─" * 60 + "\n"
        output += f"⏱️  **Time:** {execution_time:.2f}s | ❌ **Failed**\n"
        output += "─" * 60

        return output

    @staticmethod
    def format_data_result(data: Any, title: str = "Result") -> str:
        """Format data results (for database queries)"""
        if isinstance(data, list):
            if not data:
                return f"**{title}:** No data found"

            # Format as table
            output = f"**{title}** ({len(data)} records)\n\n"

            if len(data) <= 10:
                # Show all if small
                for i, row in enumerate(data, 1):
                    output += f"{i}. {row}\n"
            else:
                # Show first 5 and last 5
                for i, row in enumerate(data[:5], 1):
                    output += f"{i}. {row}\n"
                output += f"... ({len(data) - 10} more rows)\n"
                for i, row in enumerate(data[-5:], len(data) - 4):
                    output += f"{i}. {row}\n"

            return output

        elif isinstance(data, dict):
            output = f"**{title}:**\n"
            for key, value in data.items():
                output += f"  • **{key}:** {value}\n"
            return output

        else:
            return f"**{title}:** {data}"


# Quick test
if __name__ == "__main__":
    formatter = ResponseFormatter()

    # Test case
    start = time.time()
    result = {
        'response': 'The delivery delay rate is 12.5% based on the last 1000 orders.',
        'agent': 'Delay Agent',
        'success': True,
        'used_rag': False,
        'classification': {
            'query_type': 'data',
            'domain': 'delay',
            'confidence': 0.85,
            'use_database': True,
            'use_rag': False
        },
        'metrics': {
            'row_count': 1000,
            'delay_count': 125,
            'delay_rate': 12.5
        }
    }

    query = "What is the delivery delay rate?"
    formatted = formatter.format_response(result, query, start)
    print(formatted)
