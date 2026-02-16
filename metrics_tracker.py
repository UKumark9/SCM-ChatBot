"""
Simple Metrics Tracker - Lightweight version for tracking query performance
"""

import time
import logging
from typing import Dict, Any, List, Optional
from collections import deque

logger = logging.getLogger(__name__)


class MetricsTracker:
    """Lightweight metrics tracker for query performance monitoring"""

    def __init__(self, max_history: int = 100):
        """
        Initialize metrics tracker

        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.active_queries = {}  # query_id -> start_time and metadata
        logger.info("Metrics Tracker initialized")

    def start_query(self, query: str, mode: str = 'agentic') -> str:
        """
        Start tracking a new query

        Args:
            query: User's query string
            mode: Query mode (agentic, cli, ui)

        Returns:
            query_id: Unique identifier for this query
        """
        query_id = f"{int(time.time() * 1000)}_{len(self.active_queries)}"

        self.active_queries[query_id] = {
            'query': query,
            'mode': mode,
            'start_time': time.time(),
            'agents_executed': [],
            'data_sources_used': [],
            'rag_used': False
        }

        return query_id

    def add_agent_execution(self, query_id: str, agent_name: str, used_rag: bool = False):
        """
        Record that an agent was executed for this query

        Args:
            query_id: Query identifier
            agent_name: Name of the agent
            used_rag: Whether RAG was used
        """
        if query_id in self.active_queries:
            self.active_queries[query_id]['agents_executed'].append(agent_name)
            if used_rag:
                self.active_queries[query_id]['rag_used'] = True

    def add_data_source(self, query_id: str, source: str):
        """
        Record a data source used for this query

        Args:
            query_id: Query identifier
            source: Data source name (e.g., 'rag_documents', 'analytics_engine')
        """
        if query_id in self.active_queries:
            if source not in self.active_queries[query_id]['data_sources_used']:
                self.active_queries[query_id]['data_sources_used'].append(source)

    def calculate_hallucination_score(self, query_id: str, response: str, ground_truth_data: Dict = None) -> float:
        """
        Calculate hallucination risk score (simplified version)

        Args:
            query_id: Query identifier
            response: Generated response
            ground_truth_data: Optional ground truth data for validation

        Returns:
            Hallucination score (0-1, lower is better)
        """
        if query_id not in self.active_queries:
            return 0.0

        # Simple heuristic: if RAG or analytics are used, assume low hallucination
        rag_used = self.active_queries[query_id].get('rag_used', False)
        has_data_sources = len(self.active_queries[query_id].get('data_sources_used', [])) > 0

        if rag_used or has_data_sources or ground_truth_data:
            score = 0.1  # Low risk - data-grounded response
        else:
            score = 0.3  # Medium risk - no grounding data

        self.active_queries[query_id]['hallucination_score'] = score
        return score

    def end_query(self, query_id: str, success: bool = True, error: str = None):
        """
        Mark query as complete and save metrics

        Args:
            query_id: Query identifier
            success: Whether query succeeded
            error: Optional error message
        """
        if query_id not in self.active_queries:
            return

        query_data = self.active_queries[query_id]
        end_time = time.time()
        latency_ms = (end_time - query_data['start_time']) * 1000

        # Build final metrics
        metrics = {
            'query_id': query_id,
            'query': query_data['query'],
            'mode': query_data['mode'],
            'latency_ms': latency_ms,
            'success': success,
            'agents_executed': query_data.get('agents_executed', []),
            'data_sources_used': query_data.get('data_sources_used', []),
            'rag_used': query_data.get('rag_used', False),
            'hallucination_score': query_data.get('hallucination_score', 0.0),
            'timestamp': end_time,
            'error': error
        }

        # Save to history
        self.metrics_history.append(metrics)

        # Clean up active queries
        del self.active_queries[query_id]

        logger.debug(f"Query completed: {latency_ms:.0f}ms, success={success}")

    def get_recent_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent query metrics

        Args:
            limit: Maximum number of metrics to return

        Returns:
            List of metrics dictionaries
        """
        return list(self.metrics_history)[-limit:]

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics

        Returns:
            Dictionary with summary statistics
        """
        if not self.metrics_history:
            return {
                'total_queries': 0,
                'average_latency_ms': 0,
                'success_rate': 0,
                'rag_usage_rate': 0,
                'average_hallucination_score': 0
            }

        total = len(self.metrics_history)
        successful = sum(1 for m in self.metrics_history if m['success'])
        rag_used = sum(1 for m in self.metrics_history if m['rag_used'])
        avg_latency = sum(m['latency_ms'] for m in self.metrics_history) / total
        avg_hallucination = sum(m['hallucination_score'] for m in self.metrics_history) / total

        return {
            'total_queries': total,
            'average_latency_ms': avg_latency,
            'success_rate': (successful / total) * 100,
            'rag_usage_rate': (rag_used / total) * 100,
            'average_hallucination_score': avg_hallucination
        }

    def clear_history(self):
        """Clear metrics history"""
        self.metrics_history.clear()
        logger.info("Metrics history cleared")

    def format_comparison_display(self, window: int = 50) -> str:
        """
        Format performance comparison display for UI

        Args:
            window: Number of recent queries to analyze

        Returns:
            Formatted markdown string with performance metrics
        """
        if not self.metrics_history:
            return """## Performance Metrics

No queries recorded yet. Run some queries to see performance metrics.

**Tip:** Try both Agentic and Enhanced modes to compare performance!"""

        # Get recent metrics
        recent = list(self.metrics_history)[-window:]

        if not recent:
            return "No metrics available in the selected window."

        # Separate by mode if available
        agentic_queries = [m for m in recent if 'agentic' in m.get('mode', '').lower() or
                          any('Agent' in agent for agent in m.get('agents_executed', []))]
        enhanced_queries = [m for m in recent if 'enhanced' in m.get('mode', '').lower() and m not in agentic_queries]

        # Calculate overall stats
        total_queries = len(recent)
        avg_latency = sum(m['latency_ms'] for m in recent) / total_queries if recent else 0
        success_rate = sum(1 for m in recent if m['success']) / total_queries * 100 if recent else 0
        rag_usage = sum(1 for m in recent if m['rag_used']) / total_queries * 100 if recent else 0

        output = f"""## Performance Metrics (Last {len(recent)} Queries)

### Overall Statistics
- **Total Queries:** {total_queries}
- **Average Latency:** {avg_latency:.0f}ms ({avg_latency/1000:.2f}s)
- **Success Rate:** {success_rate:.1f}%
- **RAG Usage Rate:** {rag_usage:.1f}%

---
"""

        # Mode comparison if both modes have queries
        if agentic_queries and enhanced_queries:
            agentic_avg = sum(m['latency_ms'] for m in agentic_queries) / len(agentic_queries)
            enhanced_avg = sum(m['latency_ms'] for m in enhanced_queries) / len(enhanced_queries)
            improvement = ((enhanced_avg - agentic_avg) / enhanced_avg) * 100 if enhanced_avg > 0 else 0

            output += f"""### Mode Comparison

| Mode | Queries | Avg Latency | Success Rate |
|------|---------|-------------|--------------|
| Agentic | {len(agentic_queries)} | {agentic_avg:.0f}ms ({agentic_avg/1000:.2f}s) | {sum(1 for m in agentic_queries if m['success'])/len(agentic_queries)*100:.1f}% |
| Enhanced | {len(enhanced_queries)} | {enhanced_avg:.0f}ms ({enhanced_avg/1000:.2f}s) | {sum(1 for m in enhanced_queries if m['success'])/len(enhanced_queries)*100:.1f}% |

**Performance Improvement:** Agentic mode is **{improvement:.1f}% faster** than Enhanced mode

---
"""
        elif agentic_queries:
            output += f"""### Agentic Mode Statistics
- **Queries:** {len(agentic_queries)}
- **Average Latency:** {sum(m['latency_ms'] for m in agentic_queries)/len(agentic_queries):.0f}ms

---
"""
        elif enhanced_queries:
            output += f"""### Enhanced Mode Statistics
- **Queries:** {len(enhanced_queries)}
- **Average Latency:** {sum(m['latency_ms'] for m in enhanced_queries)/len(enhanced_queries):.0f}ms

---
"""

        # Recent queries breakdown
        output += "### Recent Queries\n\n"
        for i, metric in enumerate(recent[-10:], 1):  # Show last 10
            mode_icon = "🤖" if metric in agentic_queries else "✨"
            success_icon = "✅" if metric['success'] else "❌"
            rag_icon = "📚" if metric['rag_used'] else "💾"

            query_text = metric['query'][:50] + "..." if len(metric['query']) > 50 else metric['query']

            output += f"{i}. {mode_icon} {success_icon} **{query_text}** - {metric['latency_ms']:.0f}ms {rag_icon}\n"

        output += f"\n*Showing last 10 of {len(recent)} queries*\n"

        return output


# Global instance
_metrics_tracker_instance = None


def get_metrics_tracker() -> MetricsTracker:
    """
    Get the global MetricsTracker instance

    Returns:
        Global MetricsTracker instance
    """
    global _metrics_tracker_instance

    if _metrics_tracker_instance is None:
        _metrics_tracker_instance = MetricsTracker()

    return _metrics_tracker_instance


# Example usage
if __name__ == "__main__":
    tracker = get_metrics_tracker()

    # Simulate a query
    query_id = tracker.start_query("What is the delivery delay rate?", mode='agentic')
    tracker.add_agent_execution(query_id, "Delay Agent", used_rag=False)
    tracker.add_data_source(query_id, "analytics_engine")
    tracker.calculate_hallucination_score(query_id, "The delay rate is 6.28%", ground_truth_data={'analytics': True})
    tracker.end_query(query_id, success=True)

    # Get metrics
    recent = tracker.get_recent_metrics(limit=1)
    print("Recent Metrics:", recent)

    stats = tracker.get_summary_stats()
    print("\nSummary Stats:", stats)
