# 🤖 SCM Chatbot - Multi-Agent Supply Chain Management Assistant

An intelligent chatbot for supply chain management analysis with **dual-mode architecture**: Multi-Agent (Agentic) and Single-LLM (Enhanced) execution modes.

## ✨ Features

### 🤖 **Multi-Agent Mode (Agentic)**
- **4 Specialized Agents** using LangChain framework
  - 🚚 **Delay Agent** - Delivery performance analysis
  - 💰 **Analytics Agent** - Revenue, products, customers
  - 📈 **Forecasting Agent** - Demand predictions
  - 📊 **Data Query Agent** - Raw data access
- Intelligent query routing via **Agent Orchestrator**
- Tool calling and agentic workflows

### ✨ **Enhanced Mode (Single LLM)**
- Direct Groq API integration with Llama 3.3 70B
- Adaptive response complexity (simple/moderate/complex)
- Context-aware natural language understanding
- Faster responses, lower API costs

### 📊 **Legacy Mode (Rule-Based)**
- Pattern matching with keyword detection
- No LLM required (works offline)
- Fast analytics queries

### 🎨 **Dynamic UI with Mode Switching**
- Gradio web interface at http://localhost:7860
- Switch between all 3 modes during conversation
- Compare responses across different execution strategies
- Agent name display with execution metadata

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key (get from https://console.groq.com/)

### Installation

1. **Clone or download** the project

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**:
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

   **OR** for Windows, double-click: `START_HERE.bat`

5. **Open your browser** to http://localhost:7860

## 📖 Usage

### Mode Selection

In the web UI, use the **Mode Selector** on the right:

- **🤖 Agentic (Multi-Agent)** - Specialized agents with intelligent routing
- **✨ Enhanced (Single LLM)** - Adaptive single-model responses
- **📊 Legacy (Rule-Based)** - Fast keyword-based queries

### Example Queries

**Delivery Analysis:**
```
- "What is the delivery delay rate?"
- "Which states have the most delays?"
- "Show on-time delivery performance"
```

**Revenue & Sales:**
```
- "Show revenue analysis"
- "What are the revenue trends?"
- "Compare revenue by region"
```

**Forecasting:**
```
- "Forecast demand for 30 days"
- "What are the demand trends?"
- "Predict next month's orders"
```

**Comprehensive:**
```
- "Generate comprehensive supply chain report"
- "What insights can you provide about our supply chain?"
```

## 📁 Project Structure

```
scm_chatbot/
├── main.py                    # Main application entry point
├── enhanced_chatbot.py        # Enhanced chatbot with LLM integration
├── rag.py                     # RAG module for semantic search
├── requirements.txt           # Python dependencies
├── START_HERE.bat            # Windows quick-start script
├── .env                       # Configuration (API keys)
│
├── agents/                    # Multi-agent system
│   ├── __init__.py
│   ├── delay_agent.py        # Delivery delay specialist
│   ├── analytics_agent.py    # Revenue & customer specialist
│   ├── forecasting_agent.py  # Demand prediction specialist
│   ├── data_query_agent.py   # Raw data query specialist
│   ├── orchestrator.py       # Central coordinator
│   └── scm_agent.py          # Legacy agent implementation
│
├── data/                      # Data files
│   └── train/                # Training dataset (CSV files)
│       ├── df_Customers.csv
│       ├── df_Orders.csv
│       ├── df_OrderItems.csv
│       ├── df_Payments.csv
│       └── df_Products.csv
│
├── tools/                     # Analytics utilities
│   └── analytics.py          # SCM analytics engine
│
├── docs/                      # Documentation
│   └── guides/
│       ├── AGENTIC_ARCHITECTURE.md     # Architecture details
│       ├── USAGE_GUIDE.md              # Complete user guide
│       ├── IMPLEMENTATION_SUMMARY.md   # Implementation details
│       └── PROJECT_STRUCTURE.md        # Project organization
│
├── scripts/                   # Utility scripts
│   └── diagnostics/          # Diagnostic tools
│       ├── check_modes.py
│       ├── diagnose.py
│       └── test_architecture.py
│
└── archive/                   # Archived files
```

## 🛠️ Command Line Options

```bash
# Default: UI mode with all modes enabled
python main.py

# Specific modes
python main.py --agentic        # Multi-agent only
python main.py --enhanced       # Enhanced LLM only
python main.py --legacy         # Rule-based only

# Additional options
python main.py --rag            # Enable RAG semantic search
python main.py --hide-agent     # Hide agent info
python main.py --mode cli       # Command-line interface
python main.py --data test      # Use test dataset
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Required for LLM modes (Agentic and Enhanced)
GROQ_API_KEY=your_groq_api_key_here

# Optional
RAG_ENABLED=false
LOG_LEVEL=INFO
```

### Data Files

Place CSV files in `data/train/`:
- `df_Customers.csv` - Customer information
- `df_Orders.csv` - Order records
- `df_OrderItems.csv` - Order line items
- `df_Payments.csv` - Payment records
- `df_Products.csv` - Product catalog

## 📊 Mode Comparison

| Feature | Agentic | Enhanced | Legacy |
|---------|---------|----------|--------|
| **Response Quality** | Excellent | High | Good |
| **Speed** | Medium | Fast | Very Fast |
| **API Calls** | Multiple | Single | None |
| **Specialization** | High | Medium | Low |
| **Offline Support** | No | No | Yes |
| **Cost** | Higher | Medium | Free |

## 🎯 When to Use Each Mode

### Use Agentic Mode When:
- Need specialized domain expertise
- Complex multi-domain queries
- Want comprehensive reports
- Budget allows for multiple API calls

### Use Enhanced Mode When:
- Need fast general responses
- Want adaptive detail levels
- Simple to moderate queries
- Limited API budget

### Use Legacy Mode When:
- No API key available
- Need offline operation
- Simple keyword-based queries
- Very fast responses required

## 🧪 Testing

Run diagnostics:
```bash
python scripts/diagnostics/check_modes.py
```

This verifies:
- ✅ All dependencies installed
- ✅ Data files present
- ✅ Modes properly initialized
- ✅ API key configured

## 📚 Documentation

- **[Architecture Guide](docs/guides/AGENTIC_ARCHITECTURE.md)** - Complete architecture documentation
- **[Usage Guide](docs/guides/USAGE_GUIDE.md)** - Detailed user guide with examples
- **[Implementation Summary](docs/guides/IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## 🤝 Contributing

This is a demonstration project showcasing multi-agent AI architecture for supply chain management.

## 📝 License

MIT License - feel free to use and modify for your projects.

## 🆘 Troubleshooting

### "Agentic mode not initialized"
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Restart the application: `python main.py`

### "GROQ_API_KEY not set"
- Create `.env` file with your API key
- Get key from: https://console.groq.com/

### "Data loading failed"
- Check CSV files exist in `data/train/`
- Verify file names match expected names

### Dependencies not found
- Install: `pip install -r requirements.txt`
- Or use: `START_HERE.bat` (Windows)

## 🎉 Features Implemented

- ✅ Multi-agent architecture with LangChain
- ✅ Dynamic mode switching in UI
- ✅ Agent name display with metadata
- ✅ Intelligent query routing
- ✅ Adaptive response complexity
- ✅ Comprehensive analytics engine
- ✅ Demand forecasting
- ✅ RAG semantic search support
- ✅ Clean project organization
- ✅ Complete documentation

## 📧 Support

For issues or questions:
1. Check [docs/guides/USAGE_GUIDE.md](docs/guides/USAGE_GUIDE.md)
2. Run diagnostics: `python scripts/diagnostics/diagnose.py`
3. Review console logs for error messages

---

**Built with:** Python, LangChain, Groq API, Gradio, Pandas

**Model:** Llama 3.3 70B via Groq

**Last Updated:** January 2026
