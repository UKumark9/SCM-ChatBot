# SCM Chatbot - Project Structure

## Directory Organization

```
scm_chatbot/
├── main.py                           # Main application entry point
├── requirements.txt                  # Core dependencies
├── requirements_enhanced.txt         # Full dependencies with AI/RAG
├── .env                              # Environment variables (API keys)
├── README.md                         # Main project documentation
│
├── src/                              # Source code
│   ├── chatbot/                      # Chatbot modules
│   │   ├── __init__.py
│   │   └── enhanced_chatbot.py       # Enhanced AI chatbot
│   ├── analytics/                    # Analytics engine
│   │   ├── __init__.py
│   │   └── analytics.py              # SCM analytics
│   └── rag/                          # RAG modules
│       ├── __init__.py
│       └── rag_module.py             # Semantic search
│
├── data/                             # Data files
│   ├── train/                        # Training dataset
│   │   ├── df_Orders.csv
│   │   ├── df_Customers.csv
│   │   ├── df_Products.csv
│   │   ├── df_OrderItems.csv
│   │   └── df_Payments.csv
│   └── data_loader.py                # Data loading utilities
│
├── tests/                            # Test files
│   ├── test_delays.py                # Test delay calculations
│   ├── test_query.py                 # Test query responses
│   ├── test_agent_info.py            # Test agent identification
│   ├── test_response_levels.py       # Test adaptive responses
│   ├── test_serialization.py         # Test JSON serialization
│   ├── verify_fix.py                 # Verify bug fixes
│   └── ...
│
├── scripts/                          # Utility scripts
│   ├── demo_agent_info.py            # Demo agent info feature
│   └── ...
│
├── docs/                             # Documentation
│   ├── guides/                       # User guides
│   │   ├── QUICK_REFERENCE.md        # Quick start guide
│   │   ├── PROMPTS_GUIDE.md          # Query examples
│   │   └── SETUP_COMPLETE.md         # Setup guide
│   ├── features/                     # Feature documentation
│   │   ├── FEATURE_ADAPTIVE_RESPONSES.md
│   │   └── BUGFIX_PERIOD_SERIALIZATION.md
│   └── technical/                    # Technical docs
│       └── IMPROVEMENTS_SUMMARY.md   # Implementation details
│
├── config/                           # Configuration
│   └── __init__.py
│
└── archive/                          # Old/deprecated files
    └── ...
```

## Key Files

### Entry Points
- **main.py** - Main application (CLI and UI modes)
- **enhanced_chatbot.py** - Enhanced AI chatbot with LLM

### Core Modules
- **analytics.py** - Supply chain analytics engine
- **data_loader.py** - CSV data loading and preprocessing
- **rag_module.py** - RAG for semantic search

### Documentation
- **README.md** - Main project overview
- **QUICK_REFERENCE.md** - Quick start guide
- **PROMPTS_GUIDE.md** - 50+ query examples
- **SETUP_COMPLETE.md** - Complete setup guide

### Tests
- **tests/** - All test files for verification

## Running the Project

```bash
# From project root
python main.py

# Run tests
python -m pytest tests/

# Run specific test
python tests/test_query.py
```

## Installation

```bash
# Core dependencies
pip install -r requirements.txt

# Full features (AI + RAG)
pip install -r requirements_enhanced.txt
```
