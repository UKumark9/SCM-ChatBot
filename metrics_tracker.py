"""
Metrics Tracking Module for SCM Chatbot
Tracks performance metrics for single vs multi-agent queries
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricsTracker:
    """Track and analyze query metrics"""

    def __init__(self, metrics_file: str = "data/metrics_log.jsonl"):
        """
        Initialize metrics tracker

        Args:
            metrics_file: Path to store metrics logs
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_query_metrics = {}

    def start_query(self, query: str, mode: str) -> str:
        """
        Start tracking a new query

        Args:
            query: User query text
            mode: Execution mode (agentic, enhanced)

        Returns:
            query_id for tracking
        """
        query_id = f"{datetime.now().timestamp()}"

        self.current_query_metrics[query_id] = {
            'query_id': query_id,
            'query': query,
            'mode': mode,
            'start_time': time.time(),
            'end_time': None,
            'latency_ms': None,
            'agents_used': [],
            'agents_with_rag': [],
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'success': False,
            'error': None,
            'hallucination_score': 0.0,
            'task_completion': False,
            'data_sources_used': [],
            'rag_context_retrieved': False
        }

        return query_id

    def end_query(self, query_id: str, success: bool = True, error: str = None):
        """
        Mark query as complete and calculate metrics

        Args:
            query_id: Query identifier
            success: Whether query succeeded
            error: Error message if failed
        """
        if query_id not in self.current_query_metrics:
            logger.warning(f"Query ID {query_id} not found in metrics")
            return

        metrics = self.current_query_metrics[query_id]
        metrics['end_time'] = time.time()
        metrics['latency_ms'] = (metrics['end_time'] - metrics['start_time']) * 1000
        metrics['success'] = success
        metrics['error'] = error
        metrics['timestamp'] = datetime.now().isoformat()

        # Calculate task completion
        metrics['task_completion'] = self._calculate_task_completion(metrics)

        # Save to log file
        self._save_metrics(metrics)

        # Clean up
        del self.current_query_metrics[query_id]

    def add_agent_execution(self, query_id: str, agent_name: str, used_rag: bool = False,
                           tokens: Optional[Dict[str, int]] = None):
        """
        Record agent execution

        Args:
            query_id: Query identifier
            agent_name: Name of executed agent
            used_rag: Whether RAG was used
            tokens: Token usage dict with 'prompt_tokens' and 'completion_tokens'
        """
        if query_id not in self.current_query_metrics:
            return

        metrics = self.current_query_metrics[query_id]

        if agent_name not in metrics['agents_used']:
            metrics['agents_used'].append(agent_name)

        if used_rag and agent_name not in metrics['agents_with_rag']:
            metrics['agents_with_rag'].append(agent_name)
            metrics['rag_context_retrieved'] = True

        if tokens:
            metrics['prompt_tokens'] += tokens.get('prompt_tokens', 0)
            metrics['completion_tokens'] += tokens.get('completion_tokens', 0)
            metrics['total_tokens'] += tokens.get('total_tokens', 0)

    def add_data_source(self, query_id: str, source: str):
        """
        Record data source used

        Args:
            query_id: Query identifier
            source: Data source name (e.g., 'analytics_engine', 'rag_documents')
        """
        if query_id not in self.current_query_metrics:
            return

        metrics = self.current_query_metrics[query_id]
        if source not in metrics['data_sources_used']:
            metrics['data_sources_used'].append(source)

    def calculate_hallucination_score(self, query_id: str, response: str,
                                     ground_truth_data: Optional[Dict] = None) -> float:
        """
        Calculate hallucination risk score

        Args:
            query_id: Query identifier
            response: Generated response
            ground_truth_data: Actual data from database/analytics

        Returns:
            Hallucination score (0.0 = no hallucination, 1.0 = high risk)
        """
        if query_id not in self.current_query_metrics:
            return 0.0

        score = 0.0

        # Check if data sources were used
        metrics = self.current_query_metrics[query_id]
        if not metrics['data_sources_used'] and not metrics['rag_context_retrieved']:
            score += 0.5  # No grounding in data

        # Check for specific numeric claims without data source
        if any(char.isdigit() for char in response):
            if not metrics['data_sources_used']:
                score += 0.3  # Making numeric claims without data

        # Check if ground truth data was provided and used
        if ground_truth_data:
            # If we have ground truth but didn't use data sources, likely hallucinating
            if not metrics['data_sources_used']:
                score += 0.2

        # Cap at 1.0
        score = min(score, 1.0)

        metrics['hallucination_score'] = score
        return score

    def _calculate_task_completion(self, metrics: Dict) -> bool:
        """
        Determine if task was completed successfully

        Args:
            metrics: Query metrics dictionary

        Returns:
            True if task completed successfully
        """
        # Task is complete if:
        # 1. Query succeeded
        # 2. At least one agent was used OR data sources were accessed
        # 3. No errors occurred

        if not metrics['success']:
            return False

        if metrics['error']:
            return False

        if not metrics['agents_used'] and not metrics['data_sources_used']:
            return False

        return True

    def _save_metrics(self, metrics: Dict):
        """
        Save metrics to log file

        Args:
            metrics: Metrics dictionary to save
        """
        try:
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_recent_metrics(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve recent metrics from log

        Args:
            limit: Number of recent queries to retrieve

        Returns:
            List of metrics dictionaries
        """
        metrics_list = []

        try:
            if not self.metrics_file.exists():
                return []

            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Get last N lines
            for line in lines[-limit:]:
                try:
                    metrics_list.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            logger.error(f"Failed to read metrics: {e}")

        return metrics_list

    def get_comparison_stats(self, window: int = 50) -> Dict[str, Any]:
        """
        Compare single vs multi-agent performance

        Args:
            window: Number of recent queries to analyze

        Returns:
            Comparison statistics
        """
        recent_metrics = self.get_recent_metrics(limit=window)

        if not recent_metrics:
            return {
                'error': 'No metrics available'
            }

        # Separate by mode
        agentic_metrics = [m for m in recent_metrics if m['mode'] == 'agentic']
        enhanced_metrics = [m for m in recent_metrics if m['mode'] == 'enhanced']

        # Calculate stats for each mode
        stats = {
            'total_queries': len(recent_metrics),
            'agentic': self._calculate_mode_stats(agentic_metrics),
            'enhanced': self._calculate_mode_stats(enhanced_metrics),
            'window_size': window
        }

        return stats

    def _calculate_mode_stats(self, metrics_list: List[Dict]) -> Dict[str, Any]:
        """
        Calculate statistics for a specific mode

        Args:
            metrics_list: List of metrics for this mode

        Returns:
            Statistics dictionary
        """
        if not metrics_list:
            return {
                'count': 0,
                'avg_latency_ms': 0,
                'avg_tokens': 0,
                'task_completion_rate': 0,
                'avg_hallucination_score': 0,
                'avg_agents_per_query': 0,
                'rag_usage_rate': 0
            }

        total_latency = sum(m['latency_ms'] for m in metrics_list if m['latency_ms'])
        total_tokens = sum(m['total_tokens'] for m in metrics_list)
        completed_tasks = sum(1 for m in metrics_list if m['task_completion'])
        total_hallucination = sum(m['hallucination_score'] for m in metrics_list)
        total_agents = sum(len(m['agents_used']) for m in metrics_list)
        rag_used = sum(1 for m in metrics_list if m['rag_context_retrieved'])

        count = len(metrics_list)

        return {
            'count': count,
            'avg_latency_ms': round(total_latency / count, 2) if count > 0 else 0,
            'avg_tokens': round(total_tokens / count, 2) if count > 0 else 0,
            'task_completion_rate': round((completed_tasks / count) * 100, 2) if count > 0 else 0,
            'avg_hallucination_score': round(total_hallucination / count, 3) if count > 0 else 0,
            'avg_agents_per_query': round(total_agents / count, 2) if count > 0 else 0,
            'rag_usage_rate': round((rag_used / count) * 100, 2) if count > 0 else 0
        }

    def format_metrics_display(self, query_id: str = None, metrics: Dict = None) -> str:
        """
        Format metrics for display

        Args:
            query_id: Query ID to display metrics for
            metrics: Pre-computed metrics dict (if not using query_id)

        Returns:
            Formatted metrics string
        """
        if query_id and query_id in self.current_query_metrics:
            metrics = self.current_query_metrics[query_id]

        if not metrics:
            return ""

        # Format metrics display
        display = "\n\n" + "─" * 60 + "\n"
        display += "📊 **Query Metrics**\n"
        display += "─" * 60 + "\n"

        # Latency
        if metrics.get('latency_ms'):
            display += f"⏱️ **Latency**: {metrics['latency_ms']:.0f}ms\n"

        # Agents used
        if metrics.get('agents_used'):
            agents_str = ', '.join(metrics['agents_used'])
            display += f"🤖 **Agents Used**: {agents_str}\n"
            display += f"📈 **Agent Count**: {len(metrics['agents_used'])}\n"

        # RAG usage
        if metrics.get('rag_context_retrieved'):
            rag_agents = ', '.join(metrics.get('agents_with_rag', []))
            display += f"📚 **RAG Used By**: {rag_agents if rag_agents else 'Yes'}\n"

        # Token usage
        if metrics.get('total_tokens', 0) > 0:
            display += f"🔤 **Tokens Used**: {metrics['total_tokens']:,} "
            display += f"(Prompt: {metrics.get('prompt_tokens', 0):,}, "
            display += f"Completion: {metrics.get('completion_tokens', 0):,})\n"

        # Task completion
        completion_icon = "✅" if metrics.get('task_completion') else "⚠️"
        display += f"{completion_icon} **Task Completed**: {metrics.get('task_completion', False)}\n"

        # Hallucination score
        halluc_score = metrics.get('hallucination_score', 0)
        if halluc_score > 0:
            risk_level = "Low" if halluc_score < 0.3 else "Medium" if halluc_score < 0.6 else "High"
            display += f"🎯 **Hallucination Risk**: {risk_level} ({halluc_score:.2f})\n"

        # Data sources
        if metrics.get('data_sources_used'):
            sources_str = ', '.join(metrics['data_sources_used'])
            display += f"💾 **Data Sources**: {sources_str}\n"

        display += "─" * 60

        return display

    def format_comparison_display(self, window: int = 50) -> str:
        """
        Format comparison statistics for display

        Args:
            window: Number of recent queries to analyze

        Returns:
            Formatted comparison string
        """
        stats = self.get_comparison_stats(window=window)

        if 'error' in stats:
            return f"\n⚠️ {stats['error']}"

        display = "\n\n" + "=" * 60 + "\n"
        display += "📊 **Performance Comparison (Single vs Multi-Agent)**\n"
        display += "=" * 60 + "\n"
        display += f"📝 **Analysis Window**: Last {window} queries\n"
        display += f"📈 **Total Queries Analyzed**: {stats['total_queries']}\n\n"

        # Agentic mode stats
        agentic = stats['agentic']
        display += "🤖 **Agentic (Multi-Agent) Mode**\n"
        display += f"   • Queries: {agentic['count']}\n"
        display += f"   • Avg Latency: {agentic['avg_latency_ms']:.0f}ms\n"
        display += f"   • Avg Tokens: {agentic['avg_tokens']:.0f}\n"
        display += f"   • Task Completion Rate: {agentic['task_completion_rate']:.1f}%\n"
        display += f"   • Avg Agents per Query: {agentic['avg_agents_per_query']:.1f}\n"
        display += f"   • RAG Usage Rate: {agentic['rag_usage_rate']:.1f}%\n"
        display += f"   • Hallucination Risk: {agentic['avg_hallucination_score']:.3f}\n\n"

        # Enhanced mode stats
        enhanced = stats['enhanced']
        display += "✨ **Enhanced (Single LLM) Mode**\n"
        display += f"   • Queries: {enhanced['count']}\n"
        display += f"   • Avg Latency: {enhanced['avg_latency_ms']:.0f}ms\n"
        display += f"   • Avg Tokens: {enhanced['avg_tokens']:.0f}\n"
        display += f"   • Task Completion Rate: {enhanced['task_completion_rate']:.1f}%\n"
        display += f"   • RAG Usage Rate: {enhanced['rag_usage_rate']:.1f}%\n"
        display += f"   • Hallucination Risk: {enhanced['avg_hallucination_score']:.3f}\n\n"

        # Comparison insights
        display += "💡 **Key Insights**\n"

        if agentic['count'] > 0 and enhanced['count'] > 0:
            latency_diff = ((agentic['avg_latency_ms'] - enhanced['avg_latency_ms']) / enhanced['avg_latency_ms'] * 100) if enhanced['avg_latency_ms'] > 0 else 0
            token_diff = ((agentic['avg_tokens'] - enhanced['avg_tokens']) / enhanced['avg_tokens'] * 100) if enhanced['avg_tokens'] > 0 else 0

            display += f"   • Latency: Agentic is {abs(latency_diff):.0f}% {'slower' if latency_diff > 0 else 'faster'}\n"
            display += f"   • Token Usage: Agentic uses {abs(token_diff):.0f}% {'more' if token_diff > 0 else 'fewer'} tokens\n"

            if agentic['task_completion_rate'] > enhanced['task_completion_rate']:
                diff = agentic['task_completion_rate'] - enhanced['task_completion_rate']
                display += f"   • Agentic has {diff:.1f}% higher task completion rate\n"
            elif enhanced['task_completion_rate'] > agentic['task_completion_rate']:
                diff = enhanced['task_completion_rate'] - agentic['task_completion_rate']
                display += f"   • Enhanced has {diff:.1f}% higher task completion rate\n"

            if agentic['avg_hallucination_score'] < enhanced['avg_hallucination_score']:
                display += f"   • Agentic shows lower hallucination risk\n"
            elif enhanced['avg_hallucination_score'] < agentic['avg_hallucination_score']:
                display += f"   • Enhanced shows lower hallucination risk\n"

        display += "=" * 60

        return display


# Global metrics tracker instance
_metrics_tracker = None

def get_metrics_tracker() -> MetricsTracker:
    """Get global metrics tracker instance"""
    global _metrics_tracker
    if _metrics_tracker is None:
        _metrics_tracker = MetricsTracker()
    return _metrics_tracker
