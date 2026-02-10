"""
UI Output Formatter - Enhanced Gradio Display
Formats agent and RAG responses for better readability
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class UIFormatter:
    """Format responses for Gradio UI with proper line breaks and structure"""

    @staticmethod
    def format_response(result: Dict[str, Any]) -> str:
        """
        Main formatter for agent responses

        Args:
            result: Agent result dictionary with response, agent, metrics, etc.

        Returns:
            Formatted markdown string for Gradio
        """
        response = result.get('response', '')
        agent = result.get('agent', 'Unknown')
        success = result.get('success', True)
        used_rag = result.get('used_rag', False)
        metrics = result.get('metrics', {})
        classification = result.get('classification', {})

        # Format the main response content
        formatted_content = UIFormatter._format_content(response)

        # Build complete output
        output = []

        # Main content with proper spacing
        output.append(formatted_content)
        output.append("")  # Blank line

        # Add divider
        output.append("---")
        output.append("")  # Blank line

        # Add metadata section
        metadata = UIFormatter._format_metadata(
            agent, success, used_rag, classification, metrics
        )
        output.append(metadata)

        return "\n".join(output)

    @staticmethod
    def _format_content(text: str) -> str:
        """
        Format the main response content with proper line breaks

        Args:
            text: Raw response text

        Returns:
            Formatted text with line breaks
        """
        if not text:
            return "No response generated."

        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Ensure bullet points have line breaks
        text = re.sub(r'([^\n])(\s*[•\-\*]\s)', r'\1\n\2', text)

        # Ensure numbered lists have line breaks
        text = re.sub(r'([^\n])(\s*\d+\.\s)', r'\1\n\2', text)

        # Add line breaks after colons in headers
        text = re.sub(r':([A-Z])', r':\n\1', text)

        # Format "Based on policy documents:" sections
        if "Based on policy documents:" in text:
            text = text.replace("Based on policy documents:", "\n### 📚 Policy Documents\n")

        # Format RAG relevance scores
        text = re.sub(r'\[Relevance: ([\d\.]+)\]', r'\n**Relevance:** \1\n', text)

        # Format sections with headers
        text = UIFormatter._enhance_sections(text)

        # Clean up any remaining issues
        text = text.strip()

        return text

    @staticmethod
    def _enhance_sections(text: str) -> str:
        """Add visual structure to sections"""

        # Detect and format section headers (lines ending with :)
        lines = text.split('\n')
        formatted_lines = []

        for i, line in enumerate(lines):
            # Check if this looks like a section header
            if line.strip().endswith(':') and len(line.strip()) > 5 and not line.strip().startswith('['):
                # Make it a subheader
                formatted_lines.append(f"\n### {line.strip()}\n")
            else:
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    @staticmethod
    def _format_metadata(agent: str, success: bool, used_rag: bool,
                        classification: Dict, metrics: Dict) -> str:
        """
        Format metadata section with icons and structure

        Args:
            agent: Agent name
            success: Success status
            used_rag: Whether RAG was used
            classification: Query classification info
            metrics: Performance metrics

        Returns:
            Formatted metadata string
        """
        meta_parts = []

        # Agent and status
        status_icon = "✅" if success else "❌"
        meta_parts.append(f"**🤖 Agent:** {agent} | {status_icon} **{'Success' if success else 'Failed'}**")

        # Data sources
        sources = []
        if used_rag:
            sources.append("📚 Policy Documents")
        if classification.get('use_database'):
            sources.append("💾 Database")

        if sources:
            meta_parts.append(f"**📁 Sources:** {' + '.join(sources)}")

        # Query classification (if available)
        if classification:
            query_type = classification.get('query_type', '').title()
            confidence = classification.get('confidence', 0)
            if query_type:
                meta_parts.append(f"**📊 Type:** {query_type} | **Confidence:** {confidence:.0%}")

        # Metrics (if available)
        if metrics:
            metric_str = UIFormatter._format_metrics_inline(metrics)
            if metric_str:
                meta_parts.append(f"**📈 Metrics:** {metric_str}")

        return "\n\n".join(meta_parts)

    @staticmethod
    def _format_metrics_inline(metrics: Dict) -> str:
        """Format metrics in a compact inline format"""
        parts = []

        # Common metrics
        if 'row_count' in metrics:
            parts.append(f"Rows: {metrics['row_count']:,}")
        if 'delay_count' in metrics:
            parts.append(f"Delayed: {metrics['delay_count']:,}")
        if 'delay_rate' in metrics:
            parts.append(f"Rate: {metrics['delay_rate']:.1f}%")
        if 'documents_retrieved' in metrics:
            parts.append(f"Docs: {metrics['documents_retrieved']}")
        if 'execution_time' in metrics:
            parts.append(f"Time: {metrics['execution_time']:.2f}s")

        return " | ".join(parts)

    @staticmethod
    def format_rag_context(context: str) -> str:
        """
        Format RAG context with better structure

        Args:
            context: Raw RAG context string

        Returns:
            Formatted context
        """
        if not context or context == "No relevant context found.":
            return "❌ No relevant policy documents found."

        # Split by document separator
        documents = context.split('---')

        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            if not doc.strip():
                continue

            # Format each document
            formatted_doc = UIFormatter._format_single_document(doc.strip(), i)
            formatted_docs.append(formatted_doc)

        # Join with visual separators
        output = "\n\n---\n\n".join(formatted_docs)

        return output

    @staticmethod
    def _format_single_document(doc: str, index: int) -> str:
        """Format a single RAG document"""
        lines = doc.split('\n')
        formatted = []

        # Add document header
        formatted.append(f"#### 📄 Document {index}")
        formatted.append("")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Format relevance score
            if line.startswith('[Relevance:'):
                score = re.search(r'[\d\.]+', line)
                if score:
                    score_val = float(score.group())
                    formatted.append(f"**Relevance:** {score_val:.2f} {'🔥' if score_val > 0.7 else '✓'}")
            else:
                # Add line with bullet formatting
                if line.startswith('•') or line.startswith('-'):
                    formatted.append(f"  {line}")
                else:
                    formatted.append(line)

        return "\n".join(formatted)

    @staticmethod
    def format_data_result(data: Any, title: str = "Results") -> str:
        """
        Format database query results

        Args:
            data: Query results (list, dict, or simple value)
            title: Section title

        Returns:
            Formatted results
        """
        output = [f"### {title}", ""]

        if isinstance(data, list):
            if not data:
                output.append("_No data found_")
            elif len(data) <= 10:
                # Show all if small
                output.append(f"**Total Records:** {len(data)}")
                output.append("")
                for i, row in enumerate(data, 1):
                    output.append(f"{i}. {UIFormatter._format_row(row)}")
            else:
                # Show sample if large
                output.append(f"**Total Records:** {len(data)} (showing first 5)")
                output.append("")
                for i, row in enumerate(data[:5], 1):
                    output.append(f"{i}. {UIFormatter._format_row(row)}")
                output.append(f"\n_... and {len(data) - 5} more records_")

        elif isinstance(data, dict):
            for key, value in data.items():
                output.append(f"**{key}:** {value}")

        else:
            output.append(str(data))

        return "\n".join(output)

    @staticmethod
    def _format_row(row: Any) -> str:
        """Format a single data row"""
        if isinstance(row, dict):
            # Format as key-value pairs
            parts = [f"{k}: {v}" for k, v in list(row.items())[:3]]  # Show first 3 fields
            return " | ".join(parts)
        else:
            return str(row)

    @staticmethod
    def format_error(error: str, agent: str = "System") -> str:
        """
        Format error messages

        Args:
            error: Error message
            agent: Agent that generated the error

        Returns:
            Formatted error
        """
        output = [
            "### ❌ Error",
            "",
            error,
            "",
            "---",
            "",
            f"**🤖 Agent:** {agent} | ❌ **Failed**"
        ]

        return "\n".join(output)

    @staticmethod
    def format_summary_statistics(stats: Dict) -> str:
        """
        Format summary statistics in a clean table-like format

        Args:
            stats: Dictionary of statistics

        Returns:
            Formatted statistics
        """
        output = ["### 📊 Summary Statistics", ""]

        for key, value in stats.items():
            # Format the key (convert snake_case to Title Case)
            formatted_key = key.replace('_', ' ').title()

            # Format the value
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)

            output.append(f"- **{formatted_key}:** {formatted_value}")

        return "\n".join(output)

    @staticmethod
    def add_visual_separators(sections: List[str]) -> str:
        """
        Join multiple sections with visual separators

        Args:
            sections: List of formatted sections

        Returns:
            Combined output with separators
        """
        # Filter out empty sections
        sections = [s for s in sections if s and s.strip()]

        # Join with visual separators
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
