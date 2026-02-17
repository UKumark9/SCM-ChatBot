"""
Gradio UI Module for SCM Chatbot
"""

import logging
import os
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import gradio as gr

logger = logging.getLogger(__name__)


def generate_delay_charts(app):
    """Generate matplotlib bar charts for delay analysis, styled for dark theme."""
    charts = []
    try:
        result = app.analytics.analyze_delivery_delays()

        # ── Chart 1: On-Time vs Delayed ──
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor('#1e293b')
        ax.set_facecolor('#1e293b')

        on_time_pct = 100 - result['delay_rate_percentage']
        delay_pct = result['delay_rate_percentage']
        categories = ['On-Time', 'Delayed']
        values = [on_time_pct, delay_pct]
        colors = ['#10b981', '#ef4444']

        bars = ax.bar(categories, values, color=colors, width=0.5, edgecolor='none')
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'{val:.1f}%', ha='center', va='bottom',
                    color='#f1f5f9', fontweight='bold', fontsize=13)

        ax.set_ylabel('Percentage', color='#94a3b8', fontsize=10)
        ax.set_title('Delivery Performance Overview', color='#f1f5f9', fontweight='bold', fontsize=13, pad=12)
        ax.tick_params(colors='#94a3b8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#334155')
        ax.spines['bottom'].set_color('#334155')
        ax.set_ylim(0, max(values) * 1.25)

        path = os.path.join(tempfile.gettempdir(), 'delay_overview.png')
        fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#1e293b')
        plt.close(fig)
        charts.append(path)

        # ── Chart 2: Top 10 States by Delay Rate ──
        delays_by_state = result.get('delays_by_state', {})
        if delays_by_state:
            sorted_states = sorted(
                [(state, rate * 100) for state, rate in delays_by_state.items()],
                key=lambda x: x[1], reverse=True
            )[:10]

            fig, ax = plt.subplots(figsize=(7, 4.5))
            fig.patch.set_facecolor('#1e293b')
            ax.set_facecolor('#1e293b')

            states = [s[0] for s in reversed(sorted_states)]
            rates = [s[1] for s in reversed(sorted_states)]
            bar_colors = ['#ef4444' if r > 10 else '#f59e0b' if r > 5 else '#10b981' for r in rates]

            bars = ax.barh(states, rates, color=bar_colors, height=0.6, edgecolor='none')
            for bar, val in zip(bars, rates):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                        f'{val:.1f}%', va='center', color='#f1f5f9', fontsize=10)

            ax.set_xlabel('Delay Rate (%)', color='#94a3b8', fontsize=10)
            ax.set_title('Top 10 States by Delay Rate', color='#f1f5f9', fontweight='bold', fontsize=13, pad=12)
            ax.tick_params(colors='#94a3b8')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#334155')
            ax.spines['bottom'].set_color('#334155')
            ax.set_xlim(0, max(rates) * 1.2)

            path = os.path.join(tempfile.gettempdir(), 'delay_states.png')
            fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#1e293b')
            plt.close(fig)
            charts.append(path)

        # ── Chart 3: Delay Severity Distribution ──
        orders = app.orders
        delayed = orders[orders['is_delayed'] == True]
        on_time_count = int((orders['is_on_time'] == True).sum())
        minor = int(((delayed['delay_days'] > 0) & (delayed['delay_days'] <= 2)).sum())
        major = int(((delayed['delay_days'] > 2) & (delayed['delay_days'] <= 5)).sum())
        critical = int((delayed['delay_days'] > 5).sum())

        fig, ax = plt.subplots(figsize=(6, 3.5))
        fig.patch.set_facecolor('#1e293b')
        ax.set_facecolor('#1e293b')

        cats = ['On-Time', 'Minor\n(1-2 days)', 'Major\n(3-5 days)', 'Critical\n(>5 days)']
        vals = [on_time_count, minor, major, critical]
        cols = ['#10b981', '#f59e0b', '#f97316', '#ef4444']

        bars = ax.bar(cats, vals, color=cols, width=0.6, edgecolor='none')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(vals) * 0.02,
                    f'{val:,}', ha='center', va='bottom',
                    color='#f1f5f9', fontweight='bold', fontsize=11)

        ax.set_ylabel('Number of Orders', color='#94a3b8', fontsize=10)
        ax.set_title('Delay Severity Distribution', color='#f1f5f9', fontweight='bold', fontsize=13, pad=12)
        ax.tick_params(colors='#94a3b8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#334155')
        ax.spines['bottom'].set_color('#334155')

        path = os.path.join(tempfile.gettempdir(), 'delay_severity.png')
        fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#1e293b')
        plt.close(fig)
        charts.append(path)

    except Exception as e:
        logger.error(f"Chart generation error: {e}")
    return charts


def run_ui(app):
    """ Gradio UI with modern design"""
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
        custom_css = """
        /* ═══ ROOT VARIABLES ═══ */
        :root {
            --primary: #6366f1;
            --primary-hover: #818cf8;
            --primary-dark: #4f46e5;
            --accent: #06b6d4;
            --accent-hover: #22d3ee;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --bg-input: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-color: #334155;
            --border-glow: rgba(99, 102, 241, 0.4);
            --glass-bg: rgba(30, 41, 59, 0.8);
            --glass-border: rgba(148, 163, 184, 0.1);
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.5);
            --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.15);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --transition-fast: 0.15s ease;
            --transition-med: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* ═══ GLOBAL RESET ═══ */
        .gradio-container {
            background: var(--bg-dark) !important;
            font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            max-width: 1400px !important;
            margin: 0 auto !important;
        }

        .dark .gradio-container {
            background: var(--bg-dark) !important;
        }

        /* ═══ ANIMATED HEADER ═══ */
        .header-banner {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 25%, #4338ca 50%, #6366f1 75%, #818cf8 100%);
            background-size: 200% 200%;
            animation: gradientShift 8s ease infinite;
            border-radius: var(--radius-xl) !important;
            padding: 32px 40px !important;
            margin-bottom: 24px !important;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: var(--shadow-lg), var(--shadow-glow);
        }

        .header-banner::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(ellipse at center, rgba(255,255,255,0.05) 0%, transparent 70%);
            animation: shimmer 6s ease-in-out infinite;
        }

        .header-banner h1 {
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
            margin-bottom: 8px !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        .header-banner p {
            color: rgba(255,255,255,0.85) !important;
            font-size: 1rem !important;
            font-weight: 400;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes shimmer {
            0%, 100% { transform: rotate(0deg) scale(1); opacity: 0.5; }
            50% { transform: rotate(180deg) scale(1.1); opacity: 0.8; }
        }

        /* ═══ STATUS BADGES ═══ */
        .status-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 12px;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 14px;
            border-radius: 100px;
            font-size: 0.8rem;
            font-weight: 600;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.15);
        }
        .badge-primary { background: rgba(99,102,241,0.3); color: #c7d2fe; }
        .badge-success { background: rgba(16,185,129,0.3); color: #6ee7b7; }
        .badge-accent  { background: rgba(6,182,212,0.3); color: #67e8f9; }
        .badge-warning { background: rgba(245,158,11,0.3); color: #fcd34d; }

        .badge-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            animation: pulse-dot 2s ease-in-out infinite;
        }
        .badge-dot-green { background: #10b981; box-shadow: 0 0 6px #10b981; }
        .badge-dot-blue { background: #6366f1; box-shadow: 0 0 6px #6366f1; }
        .badge-dot-cyan { background: #06b6d4; box-shadow: 0 0 6px #06b6d4; }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.85); }
        }

        /* ═══ TABS ═══ */
        .tabs {
            background: transparent !important;
        }

        div.tab-nav {
            background: var(--bg-card) !important;
            border-radius: var(--radius-lg) !important;
            padding: 6px !important;
            border: 1px solid var(--border-color) !important;
            margin-bottom: 20px !important;
            box-shadow: var(--shadow-sm);
            gap: 4px !important;
        }

        div.tab-nav button,
        div.tab-nav button[aria-selected="false"] {
            background: transparent !important;
            color: #e2e8f0 !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all var(--transition-med) !important;
            position: relative;
        }

        div.tab-nav button:hover,
        div.tab-nav button[aria-selected="false"]:hover {
            background: rgba(99,102,241,0.1) !important;
            color: #ffffff !important;
        }

        div.tab-nav button.selected {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 10px rgba(99,102,241,0.4) !important;
        }

        /* ═══ GLASSMORPHISM CARDS ═══ */
        .glass-card {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-lg) !important;
            padding: 24px !important;
            box-shadow: var(--shadow-md) !important;
            transition: all var(--transition-med) !important;
        }

        .glass-card:hover {
            border-color: var(--border-glow) !important;
            box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
            transform: translateY(-1px);
        }

        /* ═══ CHATBOT AREA ═══ */
        .chatbot-container .wrap {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-lg) !important;
            box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.03) !important;
        }

        /* User messages */
        .message.user .message-bubble-border {
            background: linear-gradient(135deg, var(--primary), #7c3aed) !important;
            border: none !important;
            border-radius: 18px 18px 4px 18px !important;
            box-shadow: 0 2px 12px rgba(99,102,241,0.3) !important;
        }

        .message.user .message-bubble-border .message-content {
            color: #ffffff !important;
        }

        /* Bot messages */
        .message.bot .message-bubble-border {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 18px 18px 18px 4px !important;
            box-shadow: var(--shadow-sm) !important;
        }

        .message.bot .message-bubble-border .message-content {
            color: var(--text-primary) !important;
        }

        /* ═══ GLOSSY BUTTONS ═══ */
        .gr-button, button.primary, button.secondary {
            border-radius: var(--radius-md) !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            letter-spacing: 0.01em;
            transition: all var(--transition-med) !important;
            position: relative;
            overflow: hidden;
            border: none !important;
        }

        /* Primary glossy button */
        .gr-button.primary, button.primary, .gr-button-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 50%, var(--primary-dark) 100%) !important;
            background-size: 200% 200% !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(99,102,241,0.4),
                        inset 0 1px 0 rgba(255,255,255,0.2),
                        inset 0 -1px 0 rgba(0,0,0,0.1) !important;
            padding: 10px 24px !important;
        }

        .gr-button.primary:hover, button.primary:hover, .gr-button-primary:hover {
            background-position: 100% 0% !important;
            box-shadow: 0 6px 25px rgba(99,102,241,0.5),
                        inset 0 1px 0 rgba(255,255,255,0.25),
                        0 0 30px rgba(99,102,241,0.2) !important;
            transform: translateY(-2px) !important;
        }

        .gr-button.primary:active, button.primary:active, .gr-button-primary:active {
            transform: translateY(0px) !important;
            box-shadow: 0 2px 8px rgba(99,102,241,0.3),
                        inset 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        /* Glossy shine overlay for primary buttons */
        .gr-button.primary::before, button.primary::before, .gr-button-primary::before {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 100%; height: 50%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
            transition: left 0.5s ease;
        }
        .gr-button.primary:hover::before, button.primary:hover::before, .gr-button-primary:hover::before {
            left: 100%;
        }

        /* Secondary button */
        .gr-button.secondary, button.secondary, .gr-button-secondary {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: var(--shadow-sm),
                        inset 0 1px 0 rgba(255,255,255,0.05) !important;
            padding: 10px 24px !important;
        }

        .gr-button.secondary:hover, button.secondary:hover, .gr-button-secondary:hover {
            background: var(--bg-card-hover) !important;
            border-color: var(--primary) !important;
            box-shadow: var(--shadow-md), 0 0 15px rgba(99,102,241,0.1) !important;
            transform: translateY(-1px) !important;
        }

        /* Stop/danger button */
        .gr-button.stop, button.stop, .gr-button-stop {
            background: linear-gradient(135deg, #dc2626, #ef4444, #b91c1c) !important;
            background-size: 200% 200% !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(239,68,68,0.3),
                        inset 0 1px 0 rgba(255,255,255,0.15) !important;
            padding: 10px 24px !important;
        }

        .gr-button.stop:hover, button.stop:hover, .gr-button-stop:hover {
            background-position: 100% 0% !important;
            box-shadow: 0 6px 25px rgba(239,68,68,0.4),
                        inset 0 1px 0 rgba(255,255,255,0.2) !important;
            transform: translateY(-2px) !important;
        }

        /* ═══ TEXT INPUTS ═══ */
        textarea, input[type="text"], .gr-textbox textarea {
            background: var(--bg-input) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-size: 0.95rem !important;
            padding: 12px 16px !important;
            transition: all var(--transition-med) !important;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.2) !important;
        }

        textarea:focus, input[type="text"]:focus, .gr-textbox textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.15),
                        inset 0 1px 3px rgba(0,0,0,0.1) !important;
            outline: none !important;
        }

        /* ═══ DROPDOWN / SELECT ═══ */
        .gr-dropdown, select {
            background: var(--bg-input) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            transition: all var(--transition-med) !important;
        }

        .gr-dropdown:hover, select:hover {
            border-color: var(--primary) !important;
        }

        /* ═══ RADIO BUTTONS ═══ */
        .gr-radio label {
            background: var(--bg-card) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            padding: 10px 16px !important;
            transition: all var(--transition-med) !important;
            cursor: pointer;
        }

        .gr-radio label:hover {
            border-color: var(--primary) !important;
            background: rgba(99,102,241,0.05) !important;
        }

        .gr-radio label.selected, .gr-radio input:checked + label {
            border-color: var(--primary) !important;
            background: rgba(99,102,241,0.1) !important;
            box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
        }

        /* ═══ SLIDER ═══ */
        input[type="range"] {
            accent-color: var(--primary) !important;
        }

        /* ═══ MARKDOWN CONTENT ═══ */
        .prose, .markdown-text, .gr-markdown {
            color: var(--text-primary) !important;
        }

        .prose h1, .prose h2, .prose h3 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
        }

        .prose p { color: var(--text-secondary) !important; }
        .prose li { color: var(--text-secondary) !important; }

        .prose strong { color: var(--text-primary) !important; }

        .prose code {
            background: rgba(99,102,241,0.15) !important;
            color: #c7d2fe !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-size: 0.85em !important;
        }

        .prose hr {
            border-color: var(--border-color) !important;
            opacity: 0.5;
        }

        /* Reusable text classes (avoid hardcoded inline colors) */
        .subtitle-text { color: var(--text-secondary); margin-bottom: 20px; }
        .heading-text { font-weight: 700; color: var(--text-primary); margin-bottom: 12px; font-size: 1.05rem; }

        /* ═══ AGENT CARDS ═══ */
        .agent-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 14px 18px;
            margin-bottom: 10px;
            transition: all var(--transition-med);
            cursor: default;
        }
        .agent-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 15px rgba(99,102,241,0.1);
            transform: translateX(4px);
        }
        .agent-card .agent-icon {
            width: 32px; height: 32px; margin-right: 10px;
            display: inline-flex; align-items: center; justify-content: center;
            background: rgba(99,102,241,0.1); border-radius: 8px; flex-shrink: 0;
        }
        .agent-card .agent-icon svg {
            width: 18px; height: 18px; stroke: var(--primary); fill: none;
            stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
        }
        .agent-card .agent-name { font-weight: 700; color: var(--text-primary); }
        .agent-card .agent-desc { color: var(--text-secondary); font-size: 0.85rem; margin-top: 4px; }

        /* ═══ METRIC CARDS ═══ */
        .metric-card {
            background: linear-gradient(135deg, var(--bg-card) 0%, rgba(99,102,241,0.05) 100%);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 20px;
            text-align: center;
            transition: all var(--transition-med);
        }
        .metric-card:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
            transform: translateY(-3px);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }

        /* ═══ SECTION HEADERS ═══ */
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border-color);
        }
        .section-header h3 {
            color: var(--text-primary) !important;
            font-weight: 700;
            margin: 0;
        }
        .section-icon {
            width: 36px; height: 36px;
            display: flex; align-items: center; justify-content: center;
            background: rgba(99,102,241,0.15);
            border-radius: var(--radius-sm);
            flex-shrink: 0;
        }
        .section-icon svg {
            width: 20px; height: 20px;
            stroke: var(--primary);
            fill: none;
            stroke-width: 1.8;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* ═══ FILE UPLOAD ═══ */
        .gr-file, .upload-area {
            border: 2px dashed var(--border-color) !important;
            border-radius: var(--radius-lg) !important;
            background: var(--bg-card) !important;
            transition: all var(--transition-med) !important;
        }

        .gr-file:hover, .upload-area:hover {
            border-color: var(--primary) !important;
            background: rgba(99,102,241,0.03) !important;
        }

        /* ═══ EXAMPLES ═══ */
        .gr-examples .gr-sample-textbox {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
            transition: all var(--transition-med) !important;
            cursor: pointer !important;
            font-size: 0.82em !important;
        }

        .gr-examples .gr-sample-textbox:hover {
            border-color: var(--primary) !important;
            color: #fff !important;
            background: rgba(99,102,241,0.12) !important;
            transform: translateY(-1px) !important;
        }

        /* ═══ TRY THESE ACCORDION ═══ */
        #try-these-accordion,
        #try-these-accordion > .label-wrap {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        #try-these-accordion > .label-wrap button,
        #try-these-accordion > .label-wrap span {
            color: var(--text-primary) !important;
            font-size: 0.9em !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
        }
        #try-these-accordion > .label-wrap svg {
            stroke: var(--primary) !important;
        }

        /* ═══ LABELS ═══ */
        label, .gr-input-label, .gr-box label {
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
        }

        /* ═══ INFO TEXT ═══ */
        .gr-info, .info {
            color: var(--text-muted) !important;
            font-size: 0.8rem !important;
        }

        /* ═══ SCROLLBAR ═══ */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-dark); }
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

        /* ═══ LOADING ANIMATION ═══ */
        .generating {
            border-color: var(--primary) !important;
        }

        .progress-bar {
            background: linear-gradient(90deg, var(--primary), var(--accent), var(--primary)) !important;
            background-size: 200% 100% !important;
            animation: progressShine 1.5s linear infinite !important;
        }

        @keyframes progressShine {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        /* ═══ ACCORDION ═══ */
        .gr-accordion {
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md) !important;
            background: var(--bg-card) !important;
        }

        /* ═══ RESPONSIVE ═══ */
        @media (max-width: 768px) {
            .header-banner { padding: 20px 24px !important; }
            .header-banner h1 { font-size: 1.4rem !important; }
        }

        /* ═══ FADE-IN ANIMATION ═══ */
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ═══ FOOTER ═══ */
        footer { display: none !important; }

        /* ═══ MARKDOWN TABLES (DARK MODE) ═══ */
        .prose table, .markdown-text table, .gr-markdown table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            border: 1px solid var(--border-color) !important;
            background: var(--bg-card) !important;
        }

        .prose table th, .markdown-text table th, .gr-markdown table th {
            background: var(--bg-card-hover) !important;
            color: var(--text-primary) !important;
            padding: 12px !important;
            text-align: left !important;
            border: 1px solid var(--border-color) !important;
            font-weight: 600 !important;
        }

        .prose table td, .markdown-text table td, .gr-markdown table td {
            color: var(--text-primary) !important;
            padding: 10px 12px !important;
            border: 1px solid var(--border-color) !important;
        }

        .prose table tbody tr:nth-child(even) {
            background: rgba(30, 41, 59, 0.7) !important;
        }

        .prose table tbody tr:nth-child(odd) {
            background: var(--bg-card) !important;
        }

        .prose table tbody tr:hover {
            background: var(--bg-card-hover) !important;
        }

        /* ═══ MARKDOWN CONTENT (DARK MODE) ═══ */
        .prose, .markdown-text, .gr-markdown {
            color: var(--text-primary) !important;
        }

        .prose h1, .markdown-text h1, .gr-markdown h1,
        .prose h2, .markdown-text h2, .gr-markdown h2,
        .prose h3, .markdown-text h3, .gr-markdown h3,
        .prose h4, .markdown-text h4, .gr-markdown h4 {
            color: var(--text-primary) !important;
        }

        .prose p, .markdown-text p, .gr-markdown p {
            color: var(--text-primary) !important;
        }

        .prose ul, .markdown-text ul, .gr-markdown ul,
        .prose ol, .markdown-text ol, .gr-markdown ol {
            color: var(--text-primary) !important;
        }

        .prose li, .markdown-text li, .gr-markdown li {
            color: var(--text-primary) !important;
        }

        .prose strong, .markdown-text strong, .gr-markdown strong,
        .prose b, .markdown-text b, .gr-markdown b {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }

        .prose em, .markdown-text em, .gr-markdown em,
        .prose i, .markdown-text i, .gr-markdown i {
            color: var(--text-secondary) !important;
        }

        .prose code, .markdown-text code, .gr-markdown code {
            background: rgba(99, 102, 241, 0.1) !important;
            color: var(--primary) !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }

        .prose pre, .markdown-text pre, .gr-markdown pre {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 12px !important;
        }

        .prose blockquote, .markdown-text blockquote, .gr-markdown blockquote {
            border-left: 3px solid var(--primary) !important;
            padding-left: 12px !important;
            color: var(--text-secondary) !important;
        }

        .prose hr, .markdown-text hr, .gr-markdown hr {
            border-color: var(--border-color) !important;
        }

        .prose a, .markdown-text a, .gr-markdown a {
            color: var(--primary) !important;
        }

        .prose a:hover, .markdown-text a:hover, .gr-markdown a:hover {
            color: var(--primary-hover) !important;
        }

        /* ═══ THEME TRANSITION ═══ */
        *, *::before, *::after {
            transition: background-color 0.35s ease, color 0.25s ease, border-color 0.25s ease,
                        box-shadow 0.25s ease !important;
        }

        /* ══════════════════════════════════════════
           THEME: LIGHT
           bg: soft greys | text: dark slate | accents: indigo
           ══════════════════════════════════════════ */
        .theme-light {
            --primary: #89A8B2;
            --primary-hover: #7a9ba6;
            --primary-dark: #6d8f9a;
            --accent: #89A8B2;
            --bg-dark: #E5E1DA;
            --bg-card: #F1F0E8;
            --bg-card-hover: #e8e4dd;
            --bg-input: #E5E1DA;
            --text-primary: #2c3e50;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --border-color: #B3C8CF;
            --border-glow: rgba(137,168,178,0.3);
            --glass-bg: rgba(245,240,232,0.95);
            --glass-border: rgba(179,200,207,0.5);
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-md: 0 2px 8px rgba(0,0,0,0.08);
            --shadow-lg: 0 4px 16px rgba(0,0,0,0.1);
            --shadow-glow: 0 0 10px rgba(137,168,178,0.15);
        }
        .theme-light .gradio-container { background: #E5E1DA !important; }
        .theme-light .header-banner {
            background: linear-gradient(135deg, #89A8B2 0%, #92b0b9 30%, #9fbcc4 60%, #89A8B2 100%) !important;
            background-size: 200% 200% !important;
            box-shadow: 0 4px 16px rgba(137,168,178,0.2) !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }
        .theme-light div.tab-nav { background: #F1F0E8 !important; border-color: #B3C8CF !important; }
        .theme-light div.tab-nav button, .theme-light div.tab-nav button[aria-selected="false"] { color: #4a5568 !important; }
        .theme-light div.tab-nav button:hover, .theme-light div.tab-nav button[aria-selected="false"]:hover { background: rgba(137,168,178,0.15) !important; color: #2c3e50 !important; }
        .theme-light div.tab-nav button.selected {
            background: linear-gradient(135deg, #89A8B2, #B3C8CF) !important; color: #fff !important;
            box-shadow: 0 2px 6px rgba(137,168,178,0.25) !important;
        }
        .theme-light .message.user .message-bubble-border {
            background: linear-gradient(135deg, #89A8B2, #B3C8CF) !important;
            box-shadow: 0 2px 8px rgba(137,168,178,0.2) !important;
        }
        .theme-light .message.user .message-bubble-border .message-content { color: #ffffff !important; }
        .theme-light .message.bot .message-bubble-border {
            background: #E5E1DA !important; border: 1px solid #B3C8CF !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
        }
        .theme-light .message.bot .message-bubble-border .message-content { color: #2c3e50 !important; }
        .theme-light .chatbot-container .wrap {
            background: #F1F0E8 !important; border-color: #B3C8CF !important;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.04) !important;
        }
        .theme-light .agent-card { background: #E5E1DA; border-color: #B3C8CF; }
        .theme-light .agent-card:hover { border-color: #89A8B2; box-shadow: 0 2px 10px rgba(137,168,178,0.2); }
        .theme-light .agent-card .agent-name { color: #2c3e50; }
        .theme-light .agent-card .agent-desc { color: #4a5568; }
        .theme-light .section-header { border-bottom-color: #B3C8CF; }
        .theme-light .section-header h3 { color: #2c3e50 !important; }
        .theme-light .section-icon { background: #F1F0E8; }
        .theme-light .section-icon svg { stroke: #89A8B2; }
        .theme-light .agent-card .agent-icon { background: #F1F0E8; }
        .theme-light .agent-card .agent-icon svg { stroke: #89A8B2; }
        .theme-light textarea, .theme-light input[type="text"], .theme-light .gr-textbox textarea {
            background: #E5E1DA !important; border-color: #B3C8CF !important; color: #2c3e50 !important;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.04) !important;
        }
        .theme-light textarea:focus, .theme-light input[type="text"]:focus {
            border-color: #89A8B2 !important;
            box-shadow: 0 0 0 3px rgba(137,168,178,0.2), inset 0 1px 2px rgba(0,0,0,0.03) !important;
        }
        .theme-light .gr-button.primary, .theme-light button.primary, .theme-light .gr-button-primary {
            background: linear-gradient(135deg, #B3C8CF 0%, #a8bcc6 50%, #9db4bd 100%) !important;
            color: #ffffff !important;
            border: 1px solid #B3C8CF !important;
            box-shadow: 0 2px 8px rgba(179,200,207,0.4), 0 0 12px rgba(179,200,207,0.3), inset 0 1px 0 rgba(255,255,255,0.25) !important;
        }
        .theme-light .gr-button.primary:hover, .theme-light button.primary:hover {
            background: linear-gradient(135deg, #9db4bd 0%, #afc2ca 50%, #b8c9d2 100%) !important;
            border: 1px solid #B3C8CF !important;
            box-shadow: 0 4px 16px rgba(179,200,207,0.5), 0 0 20px rgba(179,200,207,0.4), inset 0 1px 0 rgba(255,255,255,0.3) !important;
            transform: translateY(-2px) !important;
        }
        .theme-light .gr-button.secondary, .theme-light button.secondary, .theme-light .gr-button-secondary {
            background: #E5E1DA !important; border: 1px solid #B3C8CF !important; color: #4a5568 !important;
            box-shadow: 0 1px 4px rgba(179,200,207,0.5) !important;
        }
        .theme-light .gr-button.secondary:hover, .theme-light button.secondary:hover {
            border-color: #B3C8CF !important; background: #F1F0E8 !important;
            box-shadow: 0 2px 10px rgba(179,200,207,0.5), 0 0 12px rgba(179,200,207,0.4) !important;
            transform: translateY(-1px) !important;
        }
        .theme-light .gr-button.stop, .theme-light button.stop {
            background: linear-gradient(135deg, #dc2626, #ef4444) !important; color: #fff !important;
            border: 1px solid rgba(220,38,38,0.3) !important;
            box-shadow: 0 2px 8px rgba(220,38,38,0.2), 0 0 12px rgba(239,68,68,0.1) !important;
        }
        .theme-light .gr-button.stop:hover, .theme-light button.stop:hover {
            box-shadow: 0 4px 14px rgba(220,38,38,0.3), 0 0 18px rgba(239,68,68,0.15) !important;
            transform: translateY(-1px) !important;
        }
        .theme-light .prose, .theme-light .markdown-text, .theme-light .gr-markdown { color: #2c3e50 !important; }
        .theme-light .prose h1, .theme-light .prose h2, .theme-light .prose h3 { color: #2c3e50 !important; }
        .theme-light .prose p { color: #4a5568 !important; }
        .theme-light .prose li { color: #4a5568 !important; }
        .theme-light .prose strong { color: #2c3e50 !important; }
        .theme-light .prose code { background: rgba(137,168,178,0.12) !important; color: #6d8f9a !important; }
        .theme-light .prose hr { border-color: #B3C8CF !important; }
        .theme-light label, .theme-light .gr-input-label { color: #4a5568 !important; }
        .theme-light .gr-info, .theme-light .info { color: #718096 !important; }
        .theme-light .badge { border-color: rgba(137,168,178,0.2); }
        .theme-light .badge-primary { background: rgba(137,168,178,0.12); color: #6d8f9a; }
        .theme-light .badge-success { background: rgba(16,185,129,0.1); color: #047857; }
        .theme-light .badge-accent { background: rgba(137,168,178,0.12); color: #7a9ba6; }
        .theme-light ::-webkit-scrollbar-track { background: #E5E1DA; }
        .theme-light ::-webkit-scrollbar-thumb { background: #B3C8CF; }
        .theme-light ::-webkit-scrollbar-thumb:hover { background: #89A8B2; }

        /* Override Gradio internal CSS variables for light mode */
        .theme-light {
            --body-background-fill: #E5E1DA !important;
            --body-text-color: #2c3e50 !important;
            --body-text-color-subdued: #4a5568 !important;
            --block-background-fill: #F1F0E8 !important;
            --block-border-color: #B3C8CF !important;
            --block-label-background-fill: #F1F0E8 !important;
            --block-label-border-color: #B3C8CF !important;
            --block-label-text-color: #4a5568 !important;
            --block-title-background-fill: transparent !important;
            --block-title-border-color: transparent !important;
            --block-title-text-color: #2c3e50 !important;
            --block-info-text-color: #718096 !important;
            --block-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
            --input-background-fill: #E5E1DA !important;
            --input-background-fill-hover: #F1F0E8 !important;
            --input-background-fill-focus: #E5E1DA !important;
            --input-border-color: #B3C8CF !important;
            --input-border-color-hover: #89A8B2 !important;
            --input-border-color-focus: #89A8B2 !important;
            --input-shadow: none !important;
            --input-shadow-focus: 0 0 0 3px rgba(137,168,178,0.2) !important;
            --input-text-size: 0.95rem !important;
            --input-placeholder-color: #a0aab4 !important;
            --background-fill-primary: #E5E1DA !important;
            --background-fill-secondary: #F1F0E8 !important;
            --border-color-primary: #B3C8CF !important;
            --border-color-accent: #89A8B2 !important;
            --border-color-accent-subdued: rgba(137,168,178,0.3) !important;
            --color-accent: #89A8B2 !important;
            --color-accent-soft: rgba(137,168,178,0.12) !important;
            --shadow-drop: 0 1px 4px rgba(0,0,0,0.06) !important;
            --shadow-drop-lg: 0 4px 12px rgba(0,0,0,0.08) !important;
            --panel-background-fill: #F1F0E8 !important;
            --panel-border-color: #B3C8CF !important;
            --table-border-color: #B3C8CF !important;
            --table-even-background-fill: #F1F0E8 !important;
            --table-odd-background-fill: #E5E1DA !important;
            --table-text-color: #2c3e50 !important;
            --checkbox-background-color: #F1F0E8 !important;
            --checkbox-background-color-hover: #E5E1DA !important;
            --checkbox-background-color-selected: #89A8B2 !important;
            --checkbox-border-color: #B3C8CF !important;
            --checkbox-border-color-hover: #89A8B2 !important;
            --checkbox-border-color-selected: #89A8B2 !important;
            --checkbox-label-background-fill: #E5E1DA !important;
            --checkbox-label-background-fill-hover: #F1F0E8 !important;
            --checkbox-label-background-fill-selected: rgba(137,168,178,0.15) !important;
            --checkbox-label-border-color: #B3C8CF !important;
            --checkbox-label-border-color-hover: #89A8B2 !important;
            --checkbox-label-border-color-selected: #89A8B2 !important;
            --checkbox-label-text-color: #4a5568 !important;
            --checkbox-label-text-color-selected: #6d8f9a !important;
            --button-secondary-background-fill: #F1F0E8 !important;
            --button-secondary-background-fill-hover: #E5E1DA !important;
            --button-secondary-border-color: #B3C8CF !important;
            --button-secondary-border-color-hover: #89A8B2 !important;
            --button-secondary-text-color: #4a5568 !important;
            --button-secondary-text-color-hover: #6d8f9a !important;
            --button-cancel-background-fill: #F1F0E8 !important;
            --button-cancel-text-color: #dc2626 !important;
            --button-cancel-border-color: #fecaca !important;
            --accordion-text-color: #2c3e50 !important;
            --code-background-fill: rgba(137,168,178,0.1) !important;
            --error-background-fill: #fef2f2 !important;
            --error-border-color: #fecaca !important;
            --error-text-color: #dc2626 !important;
            --stat-background-fill: #E5E1DA !important;
            --link-text-color: #89A8B2 !important;
            --link-text-color-hover: #6d8f9a !important;
        }

        /* ═══ THEME BUTTONS (inline in user bar) ═══ */
        .theme-btns { display: flex; gap: 2px; margin-left: auto; flex-shrink: 0; }
        .theme-btn { background: none; border: 1px solid transparent; border-radius: 6px;
            cursor: pointer; font-size: 1rem; line-height: 1; padding: 3px 5px;
            color: #94a3b8; transition: background 0.15s, border-color 0.15s; }
        .theme-btn:hover { background: rgba(99,102,241,0.15); border-color: #6366f1; }
        .theme-btn.active { background: rgba(99,102,241,0.2); border-color: #818cf8; color: #f1f5f9; }

        /* ═══ USER INFO BAR ═══ */
        .user-info-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 6px;
            box-sizing: border-box;
        }
        .user-info-warn { border-color: rgba(234,179,8,0.35); background: rgba(234,179,8,0.06); }
        .user-avatar { font-size: 1.3rem; line-height: 1; }
        .user-details { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
        .user-name { color: #f1f5f9; font-size: 0.875rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .user-role { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
        .login-link { color: #818cf8; font-size: 0.8rem; text-decoration: none; }
        .login-link:hover { text-decoration: underline; }
        .signout-link { color: #f87171; font-size: 0.78rem; text-decoration: none; opacity: 0.85; }
        .signout-link:hover { text-decoration: underline; opacity: 1; }

        /* ═══ LOGOUT BUTTON ═══ */
        .logout-btn { margin-bottom: 12px !important; width: 100% !important; }
        .logout-btn button { font-size: 0.82rem !important; padding: 7px 12px !important; }
        """

        def chat_with_mode(message, history, mode, rag_config="with_rag"):
            """Handle chat with mode switching"""
            if mode == "agentic" and not app.orchestrator:
                return "**Agentic mode not initialized.** The multi-agent orchestrator requires initialization at startup."
            elif mode == "enhanced" and not app.enhanced_chatbot:
                return "**Enhanced mode not initialized.** The LLM-powered chatbot is not available."

            use_rag = (rag_config == "with_rag") if mode == "enhanced" else True
            return app.query(message, mode=mode, use_rag=use_rag)

        # Document upload handler
        def upload_document(file, doc_type, description):
            if not app.document_manager:
                return "Document Manager not initialized"
            if file is None:
                return "Please select a file to upload"
            try:
                with open(file.name, 'rb') as f:
                    content = f.read()
                result = app.document_manager.upload_document(
                    file_path=file.name, file_content=content,
                    doc_type=doc_type, description=description
                )
                if result['success']:
                    doc = result['document']
                    return (f"**Document uploaded successfully!**\n\n"
                            f"**Name:** {doc['original_name']}\n"
                            f"**Type:** {doc['file_type']}\n"
                            f"**Size:** {doc['size_bytes']:,} bytes\n"
                            f"**Vectorized:** {'Yes' if doc['vectorized'] else 'No'}")
                else:
                    return f"Upload failed: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"

        # Document list handler
        def list_documents(doc_type_filter):
            if not app.document_manager:
                return "Document Manager not initialized", gr.update(choices=[])
            try:
                filter_type = None if doc_type_filter == "All" else doc_type_filter.lower()
                docs = app.document_manager.list_documents(doc_type=filter_type)
                if not docs:
                    return "No documents found", gr.update(choices=[])
                output = f"**Found {len(docs)} document(s)**\n\n"
                doc_choices = []
                for idx, doc in enumerate(docs, 1):
                    size_kb = doc['size_bytes'] / 1024
                    vectorized_status = 'Indexed' if doc.get('vectorized') else 'Pending'
                    output += f"**{idx}. {doc['original_name']}**\n"
                    output += f"  - Type: {doc['file_type']} | Category: {doc['doc_type']}\n"
                    output += f"  - Size: {size_kb:.1f} KB | Uploaded: {doc['upload_date'][:10]}\n"
                    output += f"  - Status: {vectorized_status}\n\n"
                    display_name = f"{doc['original_name']} ({doc['file_type']}, {size_kb:.1f}KB)"
                    doc_choices.append((display_name, doc['id']))
                return output, gr.update(choices=doc_choices)
            except Exception as e:
                import traceback
                return f"Error: {str(e)}\n\n{traceback.format_exc()}", gr.update(choices=[])

        # Document delete handler with auto-refresh
        def delete_document(doc_id, current_filter):
            if not app.document_manager:
                return "Document Manager not initialized", gr.update(), gr.update()
            if not doc_id:
                return "Please select a document to delete", gr.update(), gr.update()
            try:
                doc = app.document_manager.get_document(doc_id)
                if not doc:
                    return "Document not found. Please refresh the list.", gr.update(), gr.update()
                doc_name = doc['original_name']
                success = app.document_manager.delete_document(doc_id)
                if success:
                    filter_type = None if current_filter == "All" else current_filter.lower()
                    docs = app.document_manager.list_documents(doc_type=filter_type)
                    if not docs:
                        list_output = "No documents found"
                        radio_update = gr.update(choices=[])
                    else:
                        list_output = f"**Found {len(docs)} document(s)**\n\n"
                        doc_choices = []
                        for idx, d in enumerate(docs, 1):
                            size_kb = d['size_bytes'] / 1024
                            vectorized_status = 'Indexed' if d.get('vectorized') else 'Pending'
                            list_output += f"**{idx}. {d['original_name']}**\n"
                            list_output += f"  - Type: {d['file_type']} | Category: {d['doc_type']}\n"
                            list_output += f"  - Size: {size_kb:.1f} KB | Uploaded: {d['upload_date'][:10]}\n"
                            list_output += f"  - Status: {vectorized_status}\n\n"
                            display_name = f"{d['original_name']} ({d['file_type']}, {size_kb:.1f}KB)"
                            doc_choices.append((display_name, d['id']))
                        radio_update = gr.update(choices=doc_choices, value=None)
                    return (f"**Successfully deleted:** {doc_name}\n\nDocument and vector embeddings removed.",
                            list_output, radio_update)
                else:
                    return f"Failed to delete: {doc_name}", gr.update(), gr.update()
            except Exception as e:
                import traceback
                return f"Error: {str(e)}\n\n{traceback.format_exc()}", gr.update(), gr.update()

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
                    stage = progress.get('stage', '')
                    total = progress.get('total', 0)
                    current = progress.get('current', 0)
                    successful = progress.get('successful', 0)
                    failed = progress.get('failed', 0)
                    chunks = progress.get('chunks', 0)
                    doc_name = progress.get('doc_name', '')

                    if stage == 'error':
                        yield f"**Rebuild failed:** {progress.get('error', 'Unknown error')}"
                        return

                    bar_len = 20
                    filled = int(bar_len * current / total) if total else 0
                    bar = "█" * filled + "░" * (bar_len - filled)
                    pct = int(100 * current / total) if total else 0
                    header = f"**Rebuilding Index** `[{bar}]` {pct}% ({current}/{total})\n\n"
                    stats = f"> Processed: **{successful}** | Failed: **{failed}** | Chunks: **{chunks}**\n\n"

                    if stage == 'start':
                        yield f"**Rebuilding Index** — found **{total}** document(s)...\n\n> Starting..."
                        time.sleep(0.2)

                    elif stage == 'extracting':
                        yield header + stats + f"Extracting text from `{doc_name}`..."
                        time.sleep(0.1)

                    elif stage == 'chunking':
                        text_len = progress.get('text_length', 0)
                        yield header + stats + f"Chunking `{doc_name}` ({text_len:,} chars)..."
                        time.sleep(0.1)

                    elif stage == 'doc_done':
                        doc_chunks = progress.get('doc_chunks', 0)
                        yield header + stats + f"`{doc_name}` — **{doc_chunks} chunks** created"
                        time.sleep(0.1)

                    elif stage == 'doc_failed':
                        reason = progress.get('reason', 'Unknown')
                        yield header + stats + f"`{doc_name}` — **failed** ({reason})"
                        time.sleep(0.1)

                    elif stage == 'building':
                        bar_full = "█" * bar_len
                        yield f"**Rebuilding Index** `[{bar_full}]` 100%\n\n{stats}Building FAISS + BM25 index..."
                        time.sleep(0.1)

                    elif stage == 'saving':
                        bar_full = "█" * bar_len
                        yield f"**Rebuilding Index** `[{bar_full}]` 100%\n\n{stats}Saving index to disk..."
                        time.sleep(0.1)

                    elif stage == 'done':
                        yield (f"**Index rebuilt successfully!**\n\n"
                               f"**Documents processed:** {successful}/{total}\n"
                               f"**Chunks indexed:** {chunks}\n"
                               f"**Failed:** {failed}")
            except Exception as e:
                yield f"Error: {str(e)}"

        # Feature store stats handler
        def show_feature_stats():
            if not app.feature_store:
                return "Feature Store not initialized"
            try:
                stats = app.feature_store.get_stats()
                doc_stats = app.document_manager.get_stats() if app.document_manager else {}

                output = "## Feature Store\n\n"
                output += f"| Metric | Value |\n|---|---|\n"
                output += f"| Total Features | {stats.get('total_features', 0):,} |\n"
                output += f"| Backend | {stats.get('backend', 'file')} |\n"
                output += f"| Storage Size | {stats.get('storage_size_mb', 0):.2f} MB |\n\n"

                if doc_stats:
                    output += "## Document Library\n\n"
                    output += f"| Metric | Value |\n|---|---|\n"
                    output += f"| Total Documents | {doc_stats.get('total_documents', 0)} |\n"
                    output += f"| Vectorized | {doc_stats.get('vectorized_count', 0)} |\n"
                    output += f"| Total Size | {doc_stats.get('total_size_mb', 0):.2f} MB |\n\n"
                    if doc_stats.get('by_type'):
                        output += "**Documents by Type:**\n\n"
                        for doc_type, count in doc_stats['by_type'].items():
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
            )
        ) as demo:

            # ── Header ──
            # Build status badges HTML
            mode_badges = []
            if app.orchestrator:
                mode_badges.append('<span class="badge badge-primary"><span class="badge-dot badge-dot-blue"></span>Agentic</span>')
            if app.enhanced_chatbot:
                mode_badges.append('<span class="badge badge-success"><span class="badge-dot badge-dot-green"></span>Enhanced AI</span>')
            if app.use_rag:
                mode_badges.append('<span class="badge badge-accent"><span class="badge-dot badge-dot-cyan"></span>RAG Enabled</span>')

            badges_html = " ".join(mode_badges) if mode_badges else '<span class="badge badge-warning">Initializing...</span>'

            gr.HTML(f"""
            <div class="header-banner">
                <h1>SCM Intelligent Chatbot</h1>
                <p>Enterprise supply chain management powered by multi-agent AI, semantic search, and machine learning</p>
                <div class="status-row">{badges_html}</div>
            </div>
            """)

            with gr.Tabs() as tabs:
                # ══════ CHAT TAB ══════
                with gr.Tab("Chat", id="chat"):
                    with gr.Row(equal_height=False):
                        # Main chat area
                        with gr.Column(scale=3):
                            chatbot = gr.Chatbot(
                                height=520,
                                label="Conversation",
                                placeholder="Ask about delivery delays, revenue analytics, demand forecasting, or upload policy documents.",
                                elem_classes=["chatbot-container"]
                            )
                            with gr.Row():
                                msg = gr.Textbox(
                                    label="Message",
                                    placeholder="Ask about supply chain metrics, delays, revenue...",
                                    scale=5,
                                    lines=1,
                                    max_lines=3,
                                    container=False
                                )
                                submit_btn = gr.Button(
                                    "Send",
                                    scale=1,
                                    variant="primary",
                                    size="lg"
                                )

                        # Sidebar
                        with gr.Column(scale=1, min_width=280):
                            # ── User info + theme toggle (single cell) ──
                            _TB = (
                                '<div class="theme-btns">'
                                '<button class="theme-btn active" title="Dark" onclick="'
                                "var c=document.querySelector('.gradio-container');if(c)c.classList.remove('theme-light');"
                                "this.parentNode.querySelectorAll('.theme-btn').forEach(function(b){b.classList.remove('active')});"
                                'this.classList.add(\'active\');">🌙</button>'
                                '<button class="theme-btn" title="Light" onclick="'
                                "var c=document.querySelector('.gradio-container');if(c)c.classList.add('theme-light');"
                                "this.parentNode.querySelectorAll('.theme-btn').forEach(function(b){b.classList.remove('active')});"
                                'this.classList.add(\'active\');">☀️</button>'
                                '</div>'
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
                                visible=False
                            )
                            logout_btn.click(
                                fn=None,
                                inputs=[],
                                outputs=[],
                                js="() => { window.location.href = 'http://127.0.0.1:8000/logout'; }"
                            )

                            # Mode selector
                            gr.HTML('<div class="section-header"><div class="section-icon"><svg viewBox="0 0 24 24"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg></div><h3>Configuration</h3></div>')
                            mode_selector = gr.Radio(
                                choices=[
                                    ("Agentic (Multi-Agent)", "agentic"),
                                    ("Enhanced (Single LLM)", "enhanced")
                                ],
                                value=current_mode,
                                label="Execution Mode",
                                info="Select how queries are processed"
                            )

                            rag_selector = gr.Radio(
                                choices=[
                                    ("With RAG", "with_rag"),
                                    ("Without RAG", "without_rag")
                                ],
                                value="with_rag",
                                label="RAG Configuration",
                                info="Toggle document-based context retrieval",
                                visible=(current_mode == "enhanced")
                            )

                            # Available Agents section
                            agents_section = gr.HTML(
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
                                """ if current_mode == "agentic" else "",
                                visible=(current_mode == "agentic")
                            )

                            # Example queries
                            with gr.Accordion("Try These", open=True, elem_id="try-these-accordion"):
                                examples = gr.Examples(
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
                                        "Data summary"
                                    ],
                                    inputs=msg,
                                    label=""
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
                                file_types=[".pdf", ".docx", ".txt", ".md"]
                            )
                            doc_type_input = gr.Dropdown(
                                choices=["General", "Policy", "Procedure", "Guide", "Report"],
                                value="General",
                                label="Category"
                            )
                            doc_description = gr.Textbox(
                                label="Description",
                                placeholder="Brief description of the document",
                                lines=2
                            )
                            upload_btn = gr.Button("Upload Document", variant="primary", size="lg")
                            upload_output = gr.Markdown()

                        with gr.Column(scale=1):
                            gr.HTML('<div class="heading-text">Document Library</div>')
                            with gr.Row():
                                doc_filter = gr.Dropdown(
                                    choices=["All", "General", "Policy", "Procedure", "Guide", "Report"],
                                    value="All",
                                    label="Filter",
                                    scale=3
                                )
                                list_btn = gr.Button("Refresh", variant="secondary", scale=1)

                            doc_list_output = gr.Markdown()

                            gr.HTML('<div class="heading-text" style="margin-top:16px;">Manage Documents</div>')
                            doc_selector = gr.Radio(
                                choices=[],
                                label="Select document:",
                                interactive=True
                            )
                            delete_btn = gr.Button("Delete Selected", variant="stop")
                            delete_output = gr.Markdown()

                            gr.HTML('<div class="heading-text" style="margin-top:16px;">Index Management</div>')
                            rebuild_btn = gr.Button("Rebuild Index", variant="secondary")
                            rebuild_output = gr.Markdown()

                    # Event handlers for documents
                    upload_btn.click(upload_document, inputs=[doc_file, doc_type_input, doc_description], outputs=upload_output)
                    list_btn.click(list_documents, inputs=doc_filter, outputs=[doc_list_output, doc_selector])
                    delete_btn.click(delete_document, inputs=[doc_selector, doc_filter], outputs=[delete_output, doc_list_output, doc_selector])
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
                    refresh_stats_btn = gr.Button("Refresh Statistics", variant="primary")
                    refresh_stats_btn.click(show_feature_stats, inputs=None, outputs=stats_output)

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
- **Token Usage** - LLM tokens consumed
- **Task Completion** - Success rate
- **Hallucination Risk** - Data grounding score
- **RAG Usage** - Document context retrieval
- **Agents Used** - Count and type
                            """)

                    metrics_output = gr.Markdown()
                    with gr.Row():
                        metrics_window = gr.Slider(
                            minimum=10, maximum=100, value=50, step=10,
                            label="Analysis Window (recent queries)"
                        )
                    refresh_metrics_btn = gr.Button("Refresh Metrics", variant="primary")

                    def show_performance_metrics(window):
                        try:
                            from metrics_tracker import get_metrics_tracker
                            tracker = get_metrics_tracker()
                            return tracker.format_comparison_display(window=int(window))
                        except Exception as e:
                            return f"Error loading metrics: {e}\n\nRun some queries first to generate metrics data."

                    refresh_metrics_btn.click(show_performance_metrics, inputs=metrics_window, outputs=metrics_output)

            # ── Chat event handlers ──
            def respond(message, chat_history, mode, rag_config):
                if not message.strip():
                    return "", chat_history
                bot_message = chat_with_mode(message, chat_history, mode, rag_config)
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": bot_message})

                # Generate charts for delay analysis queries
                msg_lower = message.lower()
                delay_words = ['delay', 'delivery', 'on-time', 'on time', 'late', 'delayed', 'overdue']
                analysis_words = ['statistic', 'analyze', 'analysis', 'show', 'overview',
                                  'performance', 'report', 'chart', 'graph', 'visual', 'dashboard']
                has_delay = any(w in msg_lower for w in delay_words)
                has_analysis = any(w in msg_lower for w in analysis_words)
                if has_delay and has_analysis and app.analytics:
                    chart_paths = generate_delay_charts(app)
                    for path in chart_paths:
                        chat_history.append({"role": "assistant", "content": {"path": path}})

                return "", chat_history

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
                            visible=True
                        ),
                        gr.update(visible=False)
                    ]
                else:
                    return [
                        gr.update(value="", visible=False),
                        gr.update(visible=True)
                    ]

            msg.submit(respond, [msg, chatbot, mode_selector, rag_selector], [msg, chatbot])
            submit_btn.click(respond, [msg, chatbot, mode_selector, rag_selector], [msg, chatbot])
            mode_selector.change(update_mode_sections, inputs=mode_selector, outputs=[agents_section, rag_selector])

            # ── Auth: read signed token from URL on page load ──
            def on_load(request: gr.Request):
                from modules.auth_utils import verify_user, get_display, ROLE_PERMISSIONS
                try:
                    params = dict(request.query_params)
                except Exception:
                    params = {}
                user = params.get("user", "")
                role = params.get("role", "")
                sig  = params.get("sig", "")

                if verify_user(user, role, sig):
                    display   = get_display(user)
                    perms     = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["analyst"])
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
                        f'</span>{_TB}</div>'
                    )
                else:
                    show_docs = False
                    info_html = (
                        '<div class="user-info-bar user-info-warn">'
                        '<span class="user-avatar">⚠️</span>'
                        '<span class="user-details">'
                        '<span class="user-name">Not logged in</span>'
                        '<a href="http://127.0.0.1:8000/" class="login-link">Sign in →</a>'
                        f'</span>{_TB}</div>'
                    )

                return gr.update(value=info_html), gr.update(visible=show_docs)

            demo.load(on_load, inputs=None, outputs=[user_info, docs_tab])

        print("\n" + "="*70)
        print(f"  SCM Intelligent Chatbot ({mode_info}{rag_info})")
        print("="*70)

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

        print(f"\n  Open: http://localhost:7860")
        print("  Press Ctrl+C to stop\n")

        demo.launch(server_port=7860, share=False)

    except Exception as e:
        logger.error(f"UI error: {e}")
        import traceback
        traceback.print_exc()
        print("\n  UI failed. Try CLI: python main.py --mode cli")
