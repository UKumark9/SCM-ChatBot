"""
Gradio UI Module for SCM Chatbot
"""

import datetime
import logging
import os
import tempfile
import time

import gradio as gr

from scm_chatbot.ui.ui_styles import CUSTOM_CSS
from scm_chatbot.ui.ui_charts import (
    generate_delay_charts,
    generate_revenue_charts,
    generate_forecast_charts,
)

logger = logging.getLogger(__name__)


# ── Topic keywords shared between chart-triggering and follow-up suggestions ──
ANALYSIS_WORDS = [
    "statistic",
    "analyze",
    "analysis",
    "show",
    "overview",
    "performance",
    "report",
    "chart",
    "graph",
    "visual",
    "dashboard",
]
DELAY_WORDS = ["delay", "delivery", "on-time", "on time", "late", "delayed", "overdue"]
REVENUE_WORDS = ["revenue", "sales", "income", "earnings", "profit"]
FORECAST_WORDS = [
    "forecast",
    "predict",
    "prediction",
    "projection",
    "future demand",
    "demand trend",
]
CUSTOMER_WORDS = ["customer", "buyer", "client"]
PRODUCT_WORDS = ["product", "item", "category", "inventory"]

FOLLOWUP_SUGGESTIONS = {
    "delay": ["Which states have the most delays?", "Show delay severity breakdown"],
    "revenue": ["Which month had the highest revenue?", "Show revenue by state"],
    "forecast": [
        "Forecast revenue for 60 days",
        "Forecast delay rate for next 30 days",
    ],
    "customer": ["What is the repeat customer rate?", "Show customer lifetime value"],
    "product": ["What are the top 10 products?", "Show top 5 categories"],
    "default": ["Give me a comprehensive report", "What insights can you share?"],
}


def _followups_for(user_message: str) -> list:
    """Heuristic contextual follow-up questions based on the topic of a message"""
    msg_lower = user_message.lower()
    if any(w in msg_lower for w in DELAY_WORDS):
        return FOLLOWUP_SUGGESTIONS["delay"]
    if any(w in msg_lower for w in REVENUE_WORDS):
        return FOLLOWUP_SUGGESTIONS["revenue"]
    if any(w in msg_lower for w in FORECAST_WORDS):
        return FOLLOWUP_SUGGESTIONS["forecast"]
    if any(w in msg_lower for w in CUSTOMER_WORDS):
        return FOLLOWUP_SUGGESTIONS["customer"]
    if any(w in msg_lower for w in PRODUCT_WORDS):
        return FOLLOWUP_SUGGESTIONS["product"]
    return FOLLOWUP_SUGGESTIONS["default"]


def run_ui(app):
    """Gradio UI with modern design"""
    try:
        # Determine current mode (default to agentic if both available)
        if app.orchestrator and app.enhanced_chatbot:
            current_mode = "agentic"
            mode_info = "Both Modes Available"
        elif app.orchestrator:
            current_mode = "agentic"
            mode_info = "Multi-Agent System"
        elif app.enhanced_chatbot:
            current_mode = "enhanced"
            mode_info = "Enhanced AI"
        else:
            current_mode = "enhanced"
            mode_info = "Not Initialized"

        rag_info = " + RAG" if app.use_rag else ""

        # ── Production CSS Theme ──────────────────────────────────
        custom_css = CUSTOM_CSS

        def chat_with_mode_stream(message, mode, rag_config="with_rag"):
            """Yield the bot's response incrementally as it becomes available"""
            if mode == "agentic" and not app.orchestrator:
                yield "**Agentic mode not initialized.** The multi-agent orchestrator requires initialization at startup."
                return
            if mode == "enhanced" and not app.enhanced_chatbot:
                yield "**Enhanced mode not initialized.** The LLM-powered chatbot is not available."
                return

            use_rag = (rag_config == "with_rag") if mode == "enhanced" else True
            yield from app.query_stream(message, mode=mode, use_rag=use_rag)

        # Document upload handler
        def upload_document(file, doc_type, description):
            if not app.document_manager:
                return "Document Manager not initialized"
            if file is None:
                return "Please select a file to upload"
            try:
                with open(file.name, "rb") as f:
                    content = f.read()
                result = app.document_manager.upload_document(
                    file_path=file.name,
                    file_content=content,
                    doc_type=doc_type,
                    description=description,
                )
                if result["success"]:
                    doc = result["document"]
                    return (
                        f"**Document uploaded successfully!**\n\n"
                        f"**Name:** {doc['original_name']}\n"
                        f"**Type:** {doc['file_type']}\n"
                        f"**Size:** {doc['size_bytes']:,} bytes\n"
                        f"**Vectorized:** {'Yes' if doc['vectorized'] else 'No'}"
                    )
                else:
                    return f"Upload failed: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"

        # Document list handler
        def list_documents(doc_type_filter):
            if not app.document_manager:
                return "Document Manager not initialized", gr.update(choices=[])
            try:
                filter_type = (
                    None if doc_type_filter == "All" else doc_type_filter.lower()
                )
                docs = app.document_manager.list_documents(doc_type=filter_type)
                if not docs:
                    return "No documents found", gr.update(choices=[])
                output = f"**Found {len(docs)} document(s)**\n\n"
                doc_choices = []
                for idx, doc in enumerate(docs, 1):
                    size_kb = doc["size_bytes"] / 1024
                    vectorized_status = (
                        "Indexed" if doc.get("vectorized") else "Pending"
                    )
                    output += f"**{idx}. {doc['original_name']}**\n"
                    output += (
                        f"  - Type: {doc['file_type']} | Category: {doc['doc_type']}\n"
                    )
                    output += f"  - Size: {size_kb:.1f} KB | Uploaded: {doc['upload_date'][:10]}\n"
                    output += f"  - Status: {vectorized_status}\n\n"
                    display_name = (
                        f"{doc['original_name']} ({doc['file_type']}, {size_kb:.1f}KB)"
                    )
                    doc_choices.append((display_name, doc["id"]))
                return output, gr.update(choices=doc_choices)
            except Exception as e:
                import traceback

                return f"Error: {str(e)}\n\n{traceback.format_exc()}", gr.update(
                    choices=[]
                )

        # Document delete handler with auto-refresh
        def delete_document(doc_id, current_filter):
            if not app.document_manager:
                return "Document Manager not initialized", gr.update(), gr.update()
            if not doc_id:
                return "Please select a document to delete", gr.update(), gr.update()
            try:
                doc = app.document_manager.get_document(doc_id)
                if not doc:
                    return (
                        "Document not found. Please refresh the list.",
                        gr.update(),
                        gr.update(),
                    )
                doc_name = doc["original_name"]
                success = app.document_manager.delete_document(doc_id)
                if success:
                    filter_type = (
                        None if current_filter == "All" else current_filter.lower()
                    )
                    docs = app.document_manager.list_documents(doc_type=filter_type)
                    if not docs:
                        list_output = "No documents found"
                        radio_update = gr.update(choices=[])
                    else:
                        list_output = f"**Found {len(docs)} document(s)**\n\n"
                        doc_choices = []
                        for idx, d in enumerate(docs, 1):
                            size_kb = d["size_bytes"] / 1024
                            vectorized_status = (
                                "Indexed" if d.get("vectorized") else "Pending"
                            )
                            list_output += f"**{idx}. {d['original_name']}**\n"
                            list_output += f"  - Type: {d['file_type']} | Category: {d['doc_type']}\n"
                            list_output += f"  - Size: {size_kb:.1f} KB | Uploaded: {d['upload_date'][:10]}\n"
                            list_output += f"  - Status: {vectorized_status}\n\n"
                            display_name = f"{d['original_name']} ({d['file_type']}, {size_kb:.1f}KB)"
                            doc_choices.append((display_name, d["id"]))
                        radio_update = gr.update(choices=doc_choices, value=None)
                    return (
                        f"**Successfully deleted:** {doc_name}\n\nDocument and vector embeddings removed.",
                        list_output,
                        radio_update,
                    )
                else:
                    return f"Failed to delete: {doc_name}", gr.update(), gr.update()
            except Exception as e:
                import traceback

                return (
                    f"Error: {str(e)}\n\n{traceback.format_exc()}",
                    gr.update(),
                    gr.update(),
                )

        # Rebuild index handler (generator for live progress)
        def rebuild_index():
            import time

            if not app.document_manager:
                yield "Document Manager not initialized"
                return
            if not app.document_manager.rag_module:
                yield "RAG module not available — index rebuild requires RAG initialization"
                return
            try:
                for progress in app.document_manager.rebuild_index_with_progress():
                    stage = progress.get("stage", "")
                    total = progress.get("total", 0)
                    current = progress.get("current", 0)
                    successful = progress.get("successful", 0)
                    failed = progress.get("failed", 0)
                    chunks = progress.get("chunks", 0)
                    doc_name = progress.get("doc_name", "")

                    if stage == "error":
                        yield f"**Rebuild failed:** {progress.get('error', 'Unknown error')}"
                        return

                    bar_len = 20
                    filled = int(bar_len * current / total) if total else 0
                    bar = "█" * filled + "░" * (bar_len - filled)
                    pct = int(100 * current / total) if total else 0
                    header = (
                        f"**Rebuilding Index** `[{bar}]` {pct}% ({current}/{total})\n\n"
                    )
                    stats = f"> Processed: **{successful}** | Failed: **{failed}** | Chunks: **{chunks}**\n\n"

                    if stage == "start":
                        yield f"**Rebuilding Index** — found **{total}** document(s)...\n\n> Starting..."
                        time.sleep(0.2)

                    elif stage == "extracting":
                        yield header + stats + f"Extracting text from `{doc_name}`..."
                        time.sleep(0.1)

                    elif stage == "chunking":
                        text_len = progress.get("text_length", 0)
                        yield header + stats + f"Chunking `{doc_name}` ({text_len:,} chars)..."
                        time.sleep(0.1)

                    elif stage == "doc_done":
                        doc_chunks = progress.get("doc_chunks", 0)
                        yield header + stats + f"`{doc_name}` — **{doc_chunks} chunks** created"
                        time.sleep(0.1)

                    elif stage == "doc_failed":
                        reason = progress.get("reason", "Unknown")
                        yield header + stats + f"`{doc_name}` — **failed** ({reason})"
                        time.sleep(0.1)

                    elif stage == "building":
                        bar_full = "█" * bar_len
                        yield f"**Rebuilding Index** `[{bar_full}]` 100%\n\n{stats}Building FAISS + BM25 index..."
                        time.sleep(0.1)

                    elif stage == "saving":
                        bar_full = "█" * bar_len
                        yield f"**Rebuilding Index** `[{bar_full}]` 100%\n\n{stats}Saving index to disk..."
                        time.sleep(0.1)

                    elif stage == "done":
                        yield (
                            f"**Index rebuilt successfully!**\n\n"
                            f"**Documents processed:** {successful}/{total}\n"
                            f"**Chunks indexed:** {chunks}\n"
                            f"**Failed:** {failed}"
                        )
            except Exception as e:
                yield f"Error: {str(e)}"

        # Clear feature cache handler
        def clear_feature_cache():
            if not app.feature_store:
                return "Feature Store not initialized"
            try:
                count = app.feature_store.clear_all()
                return f"**Cache cleared!** Removed {count} cached entries.\n\nRefresh statistics to see updated counts."
            except Exception as e:
                return f"Error clearing cache: {str(e)}"

        # Feature store stats handler
        def show_feature_stats():
            if not app.feature_store:
                return "Feature Store not initialized"
            try:
                stats = app.feature_store.get_stats()
                doc_stats = (
                    app.document_manager.get_stats() if app.document_manager else {}
                )

                output = "## Feature Store\n\n"
                output += "| Metric | Value |\n|---|---|\n"
                output += f"| Total Features | {stats.get('total_features', 0):,} |\n"
                output += f"| Backend | {stats.get('backend', 'file')} |\n"
                output += (
                    f"| Storage Size | {stats.get('storage_size_mb', 0):.2f} MB |\n\n"
                )

                if doc_stats:
                    output += "## Document Library\n\n"
                    output += "| Metric | Value |\n|---|---|\n"
                    output += (
                        f"| Total Documents | {doc_stats.get('total_documents', 0)} |\n"
                    )
                    output += (
                        f"| Vectorized | {doc_stats.get('vectorized_count', 0)} |\n"
                    )
                    output += f"| Total Size | {doc_stats.get('total_size_mb', 0):.2f} MB |\n\n"
                    if doc_stats.get("by_type"):
                        output += "**Documents by Type:**\n\n"
                        for doc_type, count in doc_stats["by_type"].items():
                            output += f"- **{doc_type}**: {count}\n"
                return output
            except Exception as e:
                return f"Error: {str(e)}"

        # ── Build the Gradio App ──────────────────────────────────
        with gr.Blocks(
            title="SCM Intelligent Chatbot",
            css=custom_css,
            theme=gr.themes.Base(
                primary_hue=gr.themes.colors.indigo,
                secondary_hue=gr.themes.colors.slate,
                neutral_hue=gr.themes.colors.slate,
                font=gr.themes.GoogleFont("Inter"),
                font_mono=gr.themes.GoogleFont("JetBrains Mono"),
            ).set(
                body_background_fill="#0f172a",
                body_background_fill_dark="#0f172a",
                block_background_fill="#1e293b",
                block_background_fill_dark="#1e293b",
                block_border_color="#334155",
                block_border_color_dark="#334155",
                block_label_text_color="#94a3b8",
                block_label_text_color_dark="#94a3b8",
                block_title_text_color="#f1f5f9",
                block_title_text_color_dark="#f1f5f9",
                input_background_fill="#1e293b",
                input_background_fill_dark="#1e293b",
                input_border_color="#334155",
                input_border_color_dark="#334155",
                button_primary_background_fill="linear-gradient(135deg, #6366f1, #4f46e5)",
                button_primary_background_fill_dark="linear-gradient(135deg, #6366f1, #4f46e5)",
                button_primary_background_fill_hover="linear-gradient(135deg, #818cf8, #6366f1)",
                button_primary_background_fill_hover_dark="linear-gradient(135deg, #818cf8, #6366f1)",
                button_primary_text_color="#ffffff",
                button_primary_text_color_dark="#ffffff",
                button_secondary_background_fill="#1e293b",
                button_secondary_background_fill_dark="#1e293b",
                button_secondary_text_color="#f1f5f9",
                button_secondary_text_color_dark="#f1f5f9",
                border_color_primary="#334155",
                border_color_primary_dark="#334155",
                background_fill_primary="#0f172a",
                background_fill_primary_dark="#0f172a",
                background_fill_secondary="#1e293b",
                background_fill_secondary_dark="#1e293b",
                color_accent_soft="rgba(99,102,241,0.15)",
                color_accent_soft_dark="rgba(99,102,241,0.15)",
                shadow_drop="0 4px 12px rgba(0,0,0,0.4)",
                shadow_drop_lg="0 8px 32px rgba(0,0,0,0.5)",
                block_shadow="0 2px 8px rgba(0,0,0,0.3)",
                block_shadow_dark="0 2px 8px rgba(0,0,0,0.3)",
            ),
        ) as demo:

            # ── Header ──
            # Build status badges HTML
            mode_badges = []
            if app.orchestrator:
                mode_badges.append(
                    '<span class="badge badge-primary"><span class="badge-dot badge-dot-blue"></span>Agentic</span>'
                )
            if app.enhanced_chatbot:
                mode_badges.append(
                    '<span class="badge badge-success"><span class="badge-dot badge-dot-green"></span>Enhanced AI</span>'
                )
            if app.use_rag:
                mode_badges.append(
                    '<span class="badge badge-accent"><span class="badge-dot badge-dot-cyan"></span>RAG Enabled</span>'
                )

            badges_html = (
                " ".join(mode_badges)
                if mode_badges
                else '<span class="badge badge-warning">Initializing...</span>'
            )

            gr.HTML(f"""
            <div class="header-banner">
                <h1>SCM Intelligent Chatbot</h1>
                <p>Enterprise supply chain management powered by multi-agent AI, semantic search, and machine learning</p>
                <div class="status-row">{badges_html}</div>
            </div>
            """)

            with gr.Tabs():
                # ══════ CHAT TAB ══════
                with gr.Tab("Chat", id="chat"):
                    with gr.Row(equal_height=False):
                        # Main chat area
                        with gr.Column(scale=3):
                            chatbot = gr.Chatbot(
                                height=520,
                                label="Conversation",
                                placeholder="Ask about delivery delays, revenue analytics, demand forecasting, or upload policy documents.",
                                elem_classes=["chatbot-container"],
                                buttons=["copy", "copy_all"],
                            )
                            with gr.Row():
                                msg = gr.Textbox(
                                    label="Message",
                                    placeholder="Ask about supply chain metrics, delays, revenue...",
                                    scale=5,
                                    lines=1,
                                    max_lines=3,
                                    container=False,
                                )
                                submit_btn = gr.Button(
                                    "Send", scale=1, variant="primary", size="lg"
                                )
                                stop_btn = gr.Button(
                                    "Stop",
                                    scale=1,
                                    variant="stop",
                                    size="lg",
                                    visible=False,
                                )
                            with gr.Row():
                                regenerate_btn = gr.Button(
                                    "🔄 Regenerate response",
                                    size="sm",
                                    variant="secondary",
                                )
                                new_chat_btn = gr.Button(
                                    "🗑️ New Chat", size="sm", variant="secondary"
                                )
                                export_btn = gr.DownloadButton(
                                    "📥 Export Chat", size="sm", variant="secondary"
                                )
                            with gr.Row():
                                followup_btn_1 = gr.Button(
                                    visible=False, size="sm", variant="secondary"
                                )
                                followup_btn_2 = gr.Button(
                                    visible=False, size="sm", variant="secondary"
                                )

                        # Sidebar
                        with gr.Column(scale=1, min_width=280):
                            # ── User info + theme toggle (single cell) ──
                            _TB = (
                                '<div class="theme-btns">'
                                '<button class="theme-btn active" title="Dark" onclick="'
                                "var c=document.querySelector('.gradio-container');if(c)c.classList.remove('theme-light');"
                                "this.parentNode.querySelectorAll('.theme-btn').forEach(function(b){b.classList.remove('active')});"
                                "this.classList.add('active');\">🌙</button>"
                                '<button class="theme-btn" title="Light" onclick="'
                                "var c=document.querySelector('.gradio-container');if(c)c.classList.add('theme-light');"
                                "this.parentNode.querySelectorAll('.theme-btn').forEach(function(b){b.classList.remove('active')});"
                                "this.classList.add('active');\">☀️</button>"
                                "</div>"
                            )
                            user_info = gr.HTML(
                                value=(
                                    '<div class="user-info-bar"><span class="user-avatar">👤</span>'
                                    '<span class="user-details"><span class="user-name">Loading…</span>'
                                    f'<span class="user-role"></span></span>{_TB}</div>'
                                )
                            )
                            logout_btn = gr.Button(
                                "⏻  Sign Out",
                                variant="secondary",
                                size="sm",
                                elem_classes=["logout-btn"],
                                visible=False,
                            )
                            logout_btn.click(
                                fn=None,
                                inputs=[],
                                outputs=[],
                                js="() => { window.location.href = 'http://127.0.0.1:8000/logout'; }",
                            )

                            # Mode selector
                            gr.HTML(
                                '<div class="section-header"><div class="section-icon"><svg viewBox="0 0 24 24"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg></div><h3>Configuration</h3></div>'
                            )
                            mode_selector = gr.Radio(
                                choices=[
                                    ("Agentic (Multi-Agent)", "agentic"),
                                    ("Enhanced (Single LLM)", "enhanced"),
                                ],
                                value=current_mode,
                                label="Execution Mode",
                                info="",
                            )

                            rag_selector = gr.Radio(
                                choices=[
                                    ("With RAG", "with_rag"),
                                    ("Without RAG", "without_rag"),
                                ],
                                value="with_rag",
                                label="RAG Configuration",
                                info="",
                                visible=(current_mode == "enhanced"),
                            )

                            # Available Agents section
                            agents_section = gr.HTML(
                                value=(
                                    """
                                <details open style="margin-bottom:8px">
                                  <summary style="list-style:none;cursor:pointer;outline:none">
                                    <div class="section-header" style="margin-bottom:0">
                                      <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></div>
                                      <h3>Active Agents</h3>
                                    </div>
                                  </summary>
                                  <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg></span><span class="agent-name">Delay Agent</span><div class="agent-desc">Delivery performance, delays & carrier metrics</div></div>
                                  <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg></span><span class="agent-name">Analytics Agent</span><div class="agent-desc">Revenue, sales & customer insights</div></div>
                                  <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></span><span class="agent-name">Forecasting Agent</span><div class="agent-desc">Demand predictions & trend analysis</div></div>
                                  <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></span><span class="agent-name">Data Query Agent</span><div class="agent-desc">Orders, customers & product lookups</div></div>
                                </details>
                                """
                                    if current_mode == "agentic"
                                    else ""
                                ),
                                visible=(current_mode == "agentic"),
                            )

                            # Example queries
                            with gr.Accordion(
                                "Try These", open=True, elem_id="try-these-accordion"
                            ):
                                gr.Examples(
                                    examples=[
                                        # Delay Agent
                                        "What is the delivery delay rate?",
                                        "Which states have the most delays?",
                                        # Analytics Agent
                                        "Show revenue analysis",
                                        "Analyze customer behavior",
                                        # Forecasting Agent
                                        "Forecast demand for 30 days",
                                        "Forecast revenue for 60 days",
                                        "Forecast delay rate for next 30 days",
                                        # Data Query Agent - Rankings
                                        "Top 10 products",
                                        "Top 5 categories",
                                        # Data Query Agent - Geographic
                                        "Customers in São Paulo",
                                        "Customer distribution by state",
                                        # Data Query Agent - Date Filtering
                                        "Orders in January 2024",
                                        "Orders between 2024-01-01 and 2024-03-31",
                                        # Data Query Agent - Status & Trends
                                        "Order status breakdown",
                                        "Monthly order trends",
                                        # Data Query Agent - Customer History
                                        "Show me orders",
                                        "Data summary",
                                    ],
                                    inputs=msg,
                                    label="",
                                )

                # ══════ DOCUMENTS TAB ══════
                with gr.Tab("Documents", id="docs", visible=False) as docs_tab:
                    gr.HTML("""
                    <div class="section-header">
                        <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="M8 7h6"/><path d="M8 11h8"/></svg></div>
                        <h3>Document Management</h3>
                    </div>
                    <p class="subtitle-text">Upload business documents for automatic vectorization and RAG-powered semantic search.</p>
                    """)

                    with gr.Row(equal_height=False):
                        with gr.Column(scale=1):
                            gr.HTML('<div class="heading-text">Upload Document</div>')
                            doc_file = gr.File(
                                label="Select File",
                                file_types=[".pdf", ".docx", ".txt", ".md"],
                            )
                            doc_type_input = gr.Dropdown(
                                choices=[
                                    "General",
                                    "Policy",
                                    "Procedure",
                                    "Guide",
                                    "Report",
                                ],
                                value="General",
                                label="Category",
                            )
                            doc_description = gr.Textbox(
                                label="Description",
                                placeholder="Brief description of the document",
                                lines=2,
                            )
                            upload_btn = gr.Button(
                                "Upload Document", variant="primary", size="lg"
                            )
                            upload_output = gr.Markdown()

                        with gr.Column(scale=1):
                            gr.HTML('<div class="heading-text">Document Library</div>')
                            with gr.Row():
                                doc_filter = gr.Dropdown(
                                    choices=[
                                        "All",
                                        "General",
                                        "Policy",
                                        "Procedure",
                                        "Guide",
                                        "Report",
                                    ],
                                    value="All",
                                    label="Filter",
                                    scale=3,
                                )
                                list_btn = gr.Button(
                                    "Refresh", variant="secondary", scale=1
                                )

                            doc_list_output = gr.Markdown()

                            gr.HTML(
                                '<div class="heading-text" style="margin-top:16px;">Manage Documents</div>'
                            )
                            doc_selector = gr.Radio(
                                choices=[], label="Select document:", interactive=True
                            )
                            delete_btn = gr.Button("Delete Selected", variant="stop")
                            delete_output = gr.Markdown()

                            gr.HTML(
                                '<div class="heading-text" style="margin-top:16px;">Index Management</div>'
                            )
                            rebuild_btn = gr.Button(
                                "Rebuild Index", variant="secondary"
                            )
                            rebuild_output = gr.Markdown()

                    # Event handlers for documents
                    upload_btn.click(
                        upload_document,
                        inputs=[doc_file, doc_type_input, doc_description],
                        outputs=upload_output,
                    )
                    list_btn.click(
                        list_documents,
                        inputs=doc_filter,
                        outputs=[doc_list_output, doc_selector],
                    )
                    delete_btn.click(
                        delete_document,
                        inputs=[doc_selector, doc_filter],
                        outputs=[delete_output, doc_list_output, doc_selector],
                    )
                    rebuild_btn.click(rebuild_index, inputs=[], outputs=rebuild_output)

                # ══════ STATISTICS TAB ══════
                with gr.Tab("Statistics", id="stats"):
                    gr.HTML("""
                    <div class="section-header">
                        <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg></div>
                        <h3>System Statistics</h3>
                    </div>
                    <p class="subtitle-text">Feature store, document library, and system resource metrics.</p>
                    """)

                    stats_output = gr.Markdown()
                    with gr.Row():
                        refresh_stats_btn = gr.Button(
                            "Refresh Statistics", variant="primary"
                        )
                        clear_cache_btn = gr.Button("Clear Cache", variant="secondary")
                    refresh_stats_btn.click(
                        show_feature_stats, inputs=None, outputs=stats_output
                    )
                    clear_cache_btn.click(
                        clear_feature_cache, inputs=None, outputs=stats_output
                    )

                # ══════ PERFORMANCE TAB ══════
                with gr.Tab("Performance", id="perf"):
                    gr.HTML("""
                    <div class="section-header">
                        <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg></div>
                        <h3>Performance Metrics</h3>
                    </div>
                    <p class="subtitle-text">Compare single-agent (Enhanced) vs multi-agent (Agentic) query performance.</p>
                    """)

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("""
**Tracked per Query:**
- **Latency** - Response time in milliseconds
- **Task Completion** - Success rate
- **Hallucination Risk** - Data grounding score
- **RAG Usage** - Document context retrieval
- **Agents Used** - Count and type
                            """)

                    metrics_output = gr.Markdown()
                    with gr.Row():
                        metrics_window = gr.Slider(
                            minimum=10,
                            maximum=100,
                            value=50,
                            step=10,
                            label="Analysis Window (recent queries)",
                        )
                    refresh_metrics_btn = gr.Button(
                        "Refresh Metrics", variant="primary"
                    )

                    def show_performance_metrics(window):
                        try:
                            from scm_chatbot.services.metrics_tracker import (
                                get_metrics_tracker,
                            )

                            tracker = get_metrics_tracker()
                            return tracker.format_comparison_display(window=int(window))
                        except Exception as e:
                            return f"Error loading metrics: {e}\n\nRun some queries first to generate metrics data."

                    refresh_metrics_btn.click(
                        show_performance_metrics,
                        inputs=metrics_window,
                        outputs=metrics_output,
                    )

            # ── Chat event handlers ──
            def _last_user_index(chat_history):
                """Index of the most recent user turn, or None if there isn't one"""
                for i in range(len(chat_history) - 1, -1, -1):
                    if chat_history[i].get("role") == "user":
                        return i
                return None

            def _stream_turn(chat_history, user_message, mode, rag_config):
                """Append a streamed assistant answer (plus any charts) to chat_history
                in place, yielding chat_history after every incremental update. Shared
                by respond() (new message) and regenerate() (re-run last message)."""
                chat_history.append({"role": "assistant", "content": ""})
                yield chat_history

                for chunk in chat_with_mode_stream(user_message, mode, rag_config):
                    chat_history[-1]["content"] += chunk
                    yield chat_history

                # Generate inline charts when the question calls for one
                msg_lower = user_message.lower()
                has_analysis = any(w in msg_lower for w in ANALYSIS_WORDS)
                has_delay = any(w in msg_lower for w in DELAY_WORDS)
                has_revenue = any(w in msg_lower for w in REVENUE_WORDS)
                has_forecast = any(w in msg_lower for w in FORECAST_WORDS)

                chart_paths = []
                if app.analytics:
                    if has_delay and has_analysis:
                        chart_paths = generate_delay_charts(app)
                    elif has_revenue and has_analysis:
                        chart_paths = generate_revenue_charts(app)
                    elif has_forecast:
                        chart_paths = generate_forecast_charts(app)

                if chart_paths:
                    for path in chart_paths:
                        chat_history.append(
                            {"role": "assistant", "content": {"path": path}}
                        )
                    yield chat_history

            def respond(message, chat_history, mode, rag_config):
                if not message.strip():
                    yield "", chat_history
                    return

                chat_history.append({"role": "user", "content": message})
                for updated_history in _stream_turn(
                    chat_history, message, mode, rag_config
                ):
                    yield "", updated_history

            def regenerate(chat_history, mode, rag_config):
                """Drop the last assistant answer and re-run the last user message"""
                idx = _last_user_index(chat_history)
                if idx is None:
                    yield chat_history
                    return

                last_message = chat_history[idx]["content"]
                chat_history = chat_history[: idx + 1]
                yield from _stream_turn(chat_history, last_message, mode, rag_config)

            def show_followups(chat_history):
                """Populate the follow-up chips with suggestions related to the last turn"""
                idx = _last_user_index(chat_history)
                if idx is None:
                    return [gr.update(visible=False), gr.update(visible=False)]

                suggestions = _followups_for(chat_history[idx]["content"])
                return [gr.update(value=s, visible=True) for s in suggestions]

            def send_followup(suggestion):
                """A follow-up chip's own label becomes the message to send"""
                return suggestion

            def export_chat(chat_history):
                """Render the conversation as Markdown and hand back a file to download"""
                lines = [
                    "# SCM Chatbot Conversation",
                    f"_Exported {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_",
                    "",
                ]
                if not chat_history:
                    lines.append("_No messages yet._")
                for entry in chat_history:
                    role = entry.get("role", "assistant")
                    content = entry.get("content", "")
                    speaker = "**You**" if role == "user" else "**Assistant**"
                    if isinstance(content, dict) and "path" in content:
                        lines.append(
                            f"{speaker}: _[chart: {os.path.basename(content['path'])}]_\n"
                        )
                    else:
                        lines.append(f"{speaker}:\n\n{content}\n")

                path = os.path.join(
                    tempfile.gettempdir(), f"scm_chat_export_{int(time.time())}.md"
                )
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                return path

            def new_chat():
                """Clear the visible conversation and the backends' own memory of it"""
                if app.enhanced_chatbot:
                    app.enhanced_chatbot.clear_history()
                if app.orchestrator:
                    app.orchestrator.clear_history()
                return []

            def handle_feedback(chat_history, like_data: gr.LikeData):
                """Record a thumbs up/down on an assistant message via metrics_tracker"""
                try:
                    idx = like_data.index
                    if isinstance(idx, (tuple, list)):
                        idx = idx[0]

                    response_text = like_data.value
                    if not isinstance(response_text, str):
                        response_text = str(response_text)

                    user_query = ""
                    for i in range(idx - 1, -1, -1):
                        if chat_history[i].get("role") == "user":
                            user_query = chat_history[i]["content"]
                            break

                    from scm_chatbot.services.metrics_tracker import get_metrics_tracker

                    get_metrics_tracker().record_feedback(
                        query=user_query,
                        response=response_text,
                        liked=bool(like_data.liked),
                    )
                except Exception as e:
                    logger.error(f"Failed to record feedback: {e}")

            def update_mode_sections(mode):
                if mode == "agentic":
                    return [
                        gr.update(
                            value="""
                            <details open style="margin-bottom:8px">
                              <summary style="list-style:none;cursor:pointer;outline:none">
                                <div class="section-header" style="margin-bottom:0">
                                  <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></div>
                                  <h3>Active Agents</h3>
                                </div>
                              </summary>
                              <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg></span><span class="agent-name">Delay Agent</span><div class="agent-desc">Delivery performance, delays & carrier metrics</div></div>
                              <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg></span><span class="agent-name">Analytics Agent</span><div class="agent-desc">Revenue, sales & customer insights</div></div>
                              <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></span><span class="agent-name">Forecasting Agent</span><div class="agent-desc">Demand predictions & trend analysis</div></div>
                              <div class="agent-card"><span class="agent-icon"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></span><span class="agent-name">Data Query Agent</span><div class="agent-desc">Orders, customers & product lookups</div></div>
                            </details>
                            """,
                            visible=True,
                        ),
                        gr.update(visible=False),
                    ]
                else:
                    return [gr.update(value="", visible=False), gr.update(visible=True)]

            def _generating_state():
                """Swap Send -> Stop while a response is being generated"""
                return gr.update(visible=False), gr.update(visible=True)

            def _idle_state():
                """Swap Stop -> Send once generation finishes (or is cancelled)"""
                return gr.update(visible=True), gr.update(visible=False)

            followup_btns = [followup_btn_1, followup_btn_2]

            msg_event = (
                msg.submit(_generating_state, None, [submit_btn, stop_btn], queue=False)
                .then(
                    respond, [msg, chatbot, mode_selector, rag_selector], [msg, chatbot]
                )
                .then(_idle_state, None, [submit_btn, stop_btn], queue=False)
                .then(show_followups, [chatbot], followup_btns)
            )
            submit_event = (
                submit_btn.click(
                    _generating_state, None, [submit_btn, stop_btn], queue=False
                )
                .then(
                    respond, [msg, chatbot, mode_selector, rag_selector], [msg, chatbot]
                )
                .then(_idle_state, None, [submit_btn, stop_btn], queue=False)
                .then(show_followups, [chatbot], followup_btns)
            )
            regenerate_event = (
                regenerate_btn.click(
                    _generating_state, None, [submit_btn, stop_btn], queue=False
                )
                .then(regenerate, [chatbot, mode_selector, rag_selector], [chatbot])
                .then(_idle_state, None, [submit_btn, stop_btn], queue=False)
                .then(show_followups, [chatbot], followup_btns)
            )
            followup_events = [
                followup_btn.click(send_followup, [followup_btn], [msg], queue=False)
                .then(_generating_state, None, [submit_btn, stop_btn], queue=False)
                .then(
                    respond, [msg, chatbot, mode_selector, rag_selector], [msg, chatbot]
                )
                .then(_idle_state, None, [submit_btn, stop_btn], queue=False)
                .then(show_followups, [chatbot], followup_btns)
                for followup_btn in followup_btns
            ]
            all_turn_events = [
                msg_event,
                submit_event,
                regenerate_event,
            ] + followup_events
            stop_btn.click(
                _idle_state,
                None,
                [submit_btn, stop_btn],
                cancels=all_turn_events,
                queue=False,
            )
            new_chat_btn.click(new_chat, None, [chatbot], cancels=all_turn_events).then(
                lambda: (gr.update(visible=False), gr.update(visible=False)),
                None,
                followup_btns,
                queue=False,
            ).then(_idle_state, None, [submit_btn, stop_btn], queue=False)
            chatbot.like(handle_feedback, [chatbot], None)
            export_btn.click(export_chat, [chatbot], [export_btn])
            mode_selector.change(
                update_mode_sections,
                inputs=mode_selector,
                outputs=[agents_section, rag_selector],
            )

            # ── Auth: read signed token from URL on page load ──
            def on_load(request: gr.Request):
                from scm_chatbot.services.auth_utils import (
                    verify_user,
                    get_display,
                    ROLE_PERMISSIONS,
                )

                try:
                    params = dict(request.query_params)
                except Exception:
                    params = {}
                user = params.get("user", "")
                role = params.get("role", "")
                sig = params.get("sig", "")

                if verify_user(user, role, sig):
                    display = get_display(user)
                    perms = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["analyst"])
                    show_docs = perms["docs_tab_visible"]
                    role_label = role.upper()
                    role_color = "#a5b4fc" if role == "admin" else "#6ee7b7"
                    info_html = (
                        f'<div class="user-info-bar">'
                        f'<span class="user-avatar">👤</span>'
                        f'<span class="user-details">'
                        f'<span class="user-name">{display}</span>'
                        f'<span class="user-role" style="color:{role_color}">{role_label}</span>'
                        f'<a href="http://127.0.0.1:8000/logout" class="signout-link">Sign Out →</a>'
                        f"</span>{_TB}</div>"
                    )
                else:
                    show_docs = False
                    info_html = (
                        '<div class="user-info-bar user-info-warn">'
                        '<span class="user-avatar">⚠️</span>'
                        '<span class="user-details">'
                        '<span class="user-name">Not logged in</span>'
                        '<a href="http://127.0.0.1:8000/" class="login-link">Sign in →</a>'
                        f"</span>{_TB}</div>"
                    )

                return gr.update(value=info_html), gr.update(visible=show_docs)

            demo.load(on_load, inputs=None, outputs=[user_info, docs_tab])

        print("\n" + "=" * 70)
        print(f"  SCM Intelligent Chatbot ({mode_info}{rag_info})")
        print("=" * 70)

        if app.orchestrator:
            print("\n  Multi-Agent System Active:")
            print("   - Delay Agent       : Delivery analysis")
            print("   - Analytics Agent   : Revenue & customers")
            print("   - Forecasting Agent : Demand predictions")
            print("   - Data Query Agent  : Raw data access")
        elif app.enhanced_chatbot:
            print("\n  Enhanced AI Features:")
            print("   - Natural language understanding")
            print("   - Context-aware responses")
            if app.use_rag:
                print("   - Semantic search with RAG")
        else:
            print("\n  Rule-Based Mode:")
            print("   - Fast keyword-based responses")

        print("\n  Open: http://localhost:7860")
        print("  Press Ctrl+C to stop\n")

        demo.launch(server_port=7860, share=False)

    except Exception as e:
        logger.error(f"UI error: {e}")
        import traceback

        traceback.print_exc()
        print("\n  UI failed. Try CLI: python main.py --mode cli")
