"""
UI Output Formatter - Production Gradio Display
Formats agent and RAG responses for polished dark-theme readability
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class UIFormatter:
    """Format responses for Gradio UI with clean structure optimized for dark theme"""

    @staticmethod
    def format_response(result: Dict[str, Any]) -> str:
        response = result.get('response', '')
        agent = result.get('agent', 'Unknown')
        success = result.get('success', True)
        used_rag = result.get('used_rag', False)
        metrics = result.get('metrics', {})
        classification = result.get('classification', {})

        formatted_content = UIFormatter._format_content(response)

        output = []
        output.append(formatted_content)
        output.append("")
        output.append("---")
        output.append("")

        metadata = UIFormatter._format_metadata(agent, success, used_rag, classification, metrics)
        output.append(metadata)

        return "\n".join(output)

    @staticmethod
    def _format_content(text: str) -> str:
        if not text:
            return "*No response generated.*"

        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'([^\n])(\s*[•\-\*]\s)', r'\1\n\2', text)
        text = re.sub(r'([^\n])(\s*\d+\.\s)', r'\1\n\2', text)
        text = re.sub(r':([A-Z])', r':\n\1', text)

        if "Based on policy documents:" in text:
            text = text.replace("Based on policy documents:", "\n### Policy Documents\n")

        text = re.sub(r'\[Relevance: ([\d\.]+)\]', r'\n**Relevance:** `\1`\n', text)
        text = UIFormatter._enhance_sections(text)
        text = text.strip()

        return text

    @staticmethod
    def _enhance_sections(text: str) -> str:
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            if line.strip().endswith(':') and len(line.strip()) > 5 and not line.strip().startswith('['):
                formatted_lines.append(f"\n### {line.strip()}\n")
            else:
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    @staticmethod
    def _format_metadata(agent: str, success: bool, used_rag: bool,
                        classification: Dict, metrics: Dict) -> str:
        meta_parts = []

        status_text = "Success" if success else "Failed"
        meta_parts.append(f"**Agent:** {agent} | **Status:** {status_text}")

        sources = []
        if used_rag:
            sources.append("Policy Documents")
        if classification.get('use_database'):
            sources.append("Database")
        if sources:
            meta_parts.append(f"**Sources:** {' + '.join(sources)}")

        if classification:
            query_type = classification.get('query_type', '').title()
            confidence = classification.get('confidence', 0)
            if query_type:
                meta_parts.append(f"**Type:** {query_type} | **Confidence:** {confidence:.0%}")

        if metrics:
            metric_str = UIFormatter._format_metrics_inline(metrics)
            if metric_str:
                meta_parts.append(f"**Metrics:** {metric_str}")

        return " | ".join(meta_parts) if len(meta_parts) <= 2 else "\n\n".join(meta_parts)

    @staticmethod
    def _format_metrics_inline(metrics: Dict) -> str:
        parts = []
        if 'row_count' in metrics:
            parts.append(f"Rows: {metrics['row_count']:,}")
        if 'delay_count' in metrics:
            parts.append(f"Delayed: {metrics['delay_count']:,}")
        if 'delay_rate' in metrics:
            parts.append(f"Rate: {metrics['delay_rate']:.1f}%")
        if 'documents_retrieved' in metrics:
            parts.append(f"Docs: {metrics['documents_retrieved']}")
        if 'execution_time' in metrics:
            parts.append(f"`{metrics['execution_time']:.2f}s`")
        return " | ".join(parts)

    @staticmethod
    def format_rag_context(context: str) -> str:
        if not context or context == "No relevant context found.":
            return "*No relevant policy documents found.*"

        documents = context.split('---')
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            if not doc.strip():
                continue
            formatted_doc = UIFormatter._format_single_document(doc.strip(), i)
            formatted_docs.append(formatted_doc)

        return "\n\n---\n\n".join(formatted_docs)

    @staticmethod
    def _format_single_document(doc: str, index: int) -> str:
        lines = doc.split('\n')
        formatted = []
        formatted.append(f"#### Document {index}")
        formatted.append("")

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('[Relevance:'):
                score = re.search(r'[\d\.]+', line)
                if score:
                    score_val = float(score.group())
                    bar = "+" * int(score_val * 10)
                    formatted.append(f"**Relevance:** `{score_val:.2f}` {bar}")
            else:
                if line.startswith(('*', '-')):
                    formatted.append(f"  {line}")
                else:
                    formatted.append(line)

        return "\n".join(formatted)

    @staticmethod
    def format_data_result(data: Any, title: str = "Results") -> str:
        output = [f"### {title}", ""]

        if isinstance(data, list):
            if not data:
                output.append("*No data found*")
            elif len(data) <= 10:
                output.append(f"**Total Records:** {len(data)}")
                output.append("")
                for i, row in enumerate(data, 1):
                    output.append(f"{i}. {UIFormatter._format_row(row)}")
            else:
                output.append(f"**Total Records:** {len(data)} (showing first 5)")
                output.append("")
                for i, row in enumerate(data[:5], 1):
                    output.append(f"{i}. {UIFormatter._format_row(row)}")
                output.append(f"\n*... and {len(data) - 5} more records*")

        elif isinstance(data, dict):
            output.append("| Key | Value |")
            output.append("|---|---|")
            for key, value in data.items():
                output.append(f"| **{key}** | {value} |")

        else:
            output.append(str(data))

        return "\n".join(output)

    @staticmethod
    def _format_row(row: Any) -> str:
        if isinstance(row, dict):
            parts = [f"{k}: {v}" for k, v in list(row.items())[:3]]
            return " | ".join(parts)
        else:
            return str(row)

    @staticmethod
    def format_error(error: str, agent: str = "System") -> str:
        output = [
            "### Error",
            "",
            f"> {error}",
            "",
            "---",
            "",
            f"**Agent:** {agent} | **Status:** Failed"
        ]
        return "\n".join(output)

    @staticmethod
    def format_summary_statistics(stats: Dict) -> str:
        output = ["### Summary Statistics", ""]
        output.append("| Metric | Value |")
        output.append("|---|---|")

        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            output.append(f"| **{formatted_key}** | {formatted_value} |")

        return "\n".join(output)

    @staticmethod
    def add_visual_separators(sections: List[str]) -> str:
        sections = [s for s in sections if s and s.strip()]
        return "\n\n---\n\n".join(sections)


# Quick test
if __name__ == "__main__":
    formatter = UIFormatter()

    # Test case 1: RAG response
    test_result = {
        'response': """Based on policy documents:
[Relevance: 0.74]
Delay Classification 2.1 Severity Levels
• Critical Delay: >5 business days
• Major Delay: 3-5 business days
• Minor Delay: 1-2 business days""",
        'agent': 'RAG System',
        'success': True,
        'used_rag': True,
        'classification': {
            'query_type': 'policy',
            'confidence': 0.85
        },
        'metrics': {
            'documents_retrieved': 3,
            'execution_time': 1.82
        }
    }

    formatted = formatter.format_response(test_result)
    print("=" * 60)
    print("TEST OUTPUT:")
    print("=" * 60)
    print(formatted)
    print("=" * 60)
