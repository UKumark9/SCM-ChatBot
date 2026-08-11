"""
CSS theme for the SCM Chatbot Gradio UI.

Extracted from ui.py (SRP): this module owns styling only, so CSS edits
don't require touching event-wiring logic and vice versa.
"""

CUSTOM_CSS = """
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
