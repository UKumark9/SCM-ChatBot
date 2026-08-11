"""
Pytest configuration: makes the src-layout package importable without
requiring an editable install (`pip install -e .`).
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
