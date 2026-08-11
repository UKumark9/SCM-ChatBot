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

    # Minimal SVG paths — optimised for small sizes (8-10px)
    _ICONS = {
        'check':     '<polyline points="20 6 9 17 4 12"/>',
        'x-circle':  '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        'file':      '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
                     '<polyline points="14 2 14 8 20 8"/>',
        'database':  '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
                     '<path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>'
                     '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        'package':   '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8'
                     'a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
        'truck':     '<rect x="1" y="3" width="15" height="13"/>'
                     '<path d="M16 8h4l3 5v3h-7V8z"/>'
                     '<circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
        'bar-chart': '<line x1="18" y1="20" x2="18" y2="10"/>'
                     '<line x1="12" y1="20" x2="12" y2="4"/>'
                     '<line x1="6" y1="20" x2="6" y2="14"/>',
        'zap':       '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        'cpu':       '<rect x="4" y="4" width="16" height="16" rx="2"/>'
                     '<line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>',
    }

    @staticmethod
    def _svg(icon_key: str, color: str = '#818cf8', size: int = 8) -> str:
        """Return an inline SVG matching the UI's Lucide stroke style."""
        paths = UIFormatter._ICONS.get(icon_key, '')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
            f'style="vertical-align:middle;margin-right:5px;display:inline-block">'
            f'{paths}</svg>'
        )

    @staticmethod
    def format_response(result: Dict[str, Any]) -> str:
        response = result.get('response', '')
        agent = result.get('agent', 'Unknown')
        success = result.get('success', True)
        used_rag = result.get('used_rag', False)
        metrics = result.get('metrics', {})
        classification = result.get('classification', {})
        chart_base64 = result.get('chart_base64', None)

        formatted_content = UIFormatter._format_content(response)
        charts_base64 = result.get('charts_base64', None)

        output = []
        output.append(formatted_content)

        # Embed forecast charts — prefer multi-chart list, fall back to single
        if charts_base64 and isinstance(charts_base64, list):
            for idx, cb64 in enumerate(charts_base64):
                if cb64:
                    output.append("")
                    output.append(
                        f'<img src="data:image/png;base64,{cb64}" '
                        f'alt="Forecast Chart {idx + 1}" '
                        f'style="max-width:100%; border-radius:12px; '
                        f'margin:12px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">'
                    )
            output.append("")
        elif chart_base64:
            output.append("")
            output.append(
                f'<img src="data:image/png;base64,{chart_base64}" '
                f'alt="Forecast Chart" '
                f'style="max-width:100%; border-radius:12px; '
                f'margin:12px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">'
            )
            output.append("")

        # Always add blank line before metadata for visual separation
        output.append("")
        metadata = UIFormatter._format_metadata(agent, success, used_rag, classification, metrics)
        output.append(metadata)

        return "\n".join(output)

    @staticmethod
    def _is_table_line(line: str) -> bool:
        """Return True for markdown table rows and separator lines — must not be mutated."""
        stripped = line.strip()
        return stripped.startswith('|') or bool(re.match(r'^\|?[\s\-:]+\|', stripped))

    @staticmethod
    def _format_content(text: str) -> str:
        if not text:
            return "*No response generated.*"

        # Collapse excessive blank lines globally (safe on tables)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Apply inline fixups only to non-table lines to avoid corrupting cell content
        lines = text.split('\n')
        processed = []
        for line in lines:
            if UIFormatter._is_table_line(line):
                processed.append(line)
            else:
                line = re.sub(r'([^\n])(\s*[•]\s)', r'\1\n\2', line)       # bullet points
                line = re.sub(r'([^\n])(\s*-\s)(?!\s*\|)', r'\1\n\2', line) # dashes (not table)
                line = re.sub(r'([^\n])(\s*\d+\.\s)', r'\1\n\2', line)     # numbered lists
                line = re.sub(r':([A-Z])(?![^|]*\|)', r':\n\1', line)      # colon+Upper (not inside table)
                processed.append(line)
        text = '\n'.join(processed)

        if "Based on policy documents:" in text:
            text = text.replace("Based on policy documents:", "\n### Policy Documents\n")

        text = re.sub(r'\[Source: ([^\]]+)\]', r'\n*Source: \1*\n', text)
        text = re.sub(r'\[Relevance: ([\d\.]+)\]', r'\n**Relevance:** `\1`\n', text)
        text = UIFormatter._enhance_sections(text)
        text = text.strip()

        return text

    @staticmethod
    def _enhance_sections(text: str) -> str:
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            # Skip table rows — never convert them to section headers
            if UIFormatter._is_table_line(line):
                formatted_lines.append(line)
            elif line.strip().endswith(':') and len(line.strip()) > 5 and not line.strip().startswith('['):
                formatted_lines.append(f"\n### {line.strip()}\n")
            else:
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    @staticmethod
    def _format_metadata(agent: str, success: bool, used_rag: bool,
                        classification: Dict, metrics: Dict) -> str:
        parts = []

        # Agent + status
        status = "Success" if success else "Failed"
        agent_name = agent.replace(' (Rule-Based)', '').replace('(Rule-Based)', '').strip()
        parts.append(f"{agent_name} — {status}")

        # Sources
        if used_rag:
            parts.append("Policy Docs")
        if classification.get('use_database'):
            parts.append("Live Database")

        # Intent + confidence
        if classification:
            query_type = classification.get('query_type', '').strip().lower()
            confidence = classification.get('confidence', 0)
            type_labels = {
                'data': 'Data Lookup', 'policy': 'Policy',
                'analytics': 'Analytics', 'forecast': 'Forecast', 'general': 'General',
            }
            qtype = type_labels.get(query_type, query_type.title())
            if qtype:
                conf_pct = int(confidence * 100)
                conf_label = "High" if conf_pct >= 80 else ("Medium" if conf_pct >= 50 else "Low")
                parts.append(qtype)
                parts.append(f"{conf_pct}% {conf_label}")

        # Metrics
        if metrics:
            metric_str = UIFormatter._format_metrics_inline(metrics)
            if metric_str:
                parts.append(metric_str)

        body = " | ".join(parts)
        return f'<p style="font-size:0.75em;font-style:italic;opacity:0.6;margin-top:4px">{body}</p>'

    @staticmethod
    def _format_metrics_inline(metrics: Dict) -> str:
        parts = []
        if 'row_count' in metrics:
            parts.append(f"{metrics['row_count']:,} records")
        if 'delay_count' in metrics:
            parts.append(f"{metrics['delay_count']:,} delayed")
        if 'delay_rate' in metrics:
            parts.append(f"rate {metrics['delay_rate']:.1f}%")
        if 'documents_retrieved' in metrics:
            parts.append(f"{metrics['documents_retrieved']} docs")
        if 'execution_time' in metrics:
            parts.append(f"{metrics['execution_time']:.2f}s")
        return " | ".join(parts)

    @staticmethod
    def synthesize_rag_response(query: str, context: str, llm_client=None) -> str:
        """Use LLM to synthesize a coherent answer from RAG context.
        Falls back to formatted raw chunks if LLM is unavailable."""
        if not context or context == "No relevant context found.":
            return "*No relevant policy documents found.*"

        if not llm_client:
            return UIFormatter.format_rag_context(context)

        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content=(
                    "You are a supply chain management expert. Using ONLY the provided document excerpts, "
                    "give a clear, concise answer to the user's question. "
                    "Use bullet points and bold key terms for readability. "
                    "When citing information, mention the source document name in italics, e.g. *filename.pdf*. "
                    "If the documents don't fully answer the question, say what you found and note the gap. "
                    "Do NOT mention relevance scores or chunk numbers."
                )),
                HumanMessage(content=f"Documents:\n{context}\n\nQuestion: {query}")
            ]
            response = llm_client.invoke(messages)
            return response.content
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"LLM synthesis failed, using raw context: {e}")
            return UIFormatter.format_rag_context(context)

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
        doc_name = None

        # Extract source name first
        for line in lines:
            m = re.match(r'\[Source: (.+)\]', line.strip())
            if m:
                doc_name = m.group(1)
                break

        heading = f"#### Document {index}" + (f" — *{doc_name}*" if doc_name else "")
        formatted.append(heading)
        formatted.append("")

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('[Source:'):
                continue  # Already shown in heading
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
