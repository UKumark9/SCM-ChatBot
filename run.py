"""
Entry point for the SCM Chatbot.

Usage:
    python run.py --agentic --rag
    python run.py --mode cli

Makes the src-layout package importable without requiring an editable
install (`pip install -e .`), then delegates to scm_chatbot.core.main.
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scm_chatbot.core.main import main  # noqa: E402 - needs sys.path set up above first

if __name__ == "__main__":
    main()
