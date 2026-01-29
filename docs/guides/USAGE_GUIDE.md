# SCM Chatbot Usage Guide

## 🚀 Quick Start

### Start the Application (UI Mode - Recommended)

```bash
python main.py
```

**What happens**:
- ✅ Automatically initializes **all modes** (Agentic, Enhanced, Legacy)
- ✅ Opens web UI at http://localhost:7860
- ✅ Allows **dynamic switching** between modes in the UI
- ✅ Displays agent name with each response

### Using the Mode Selector

Once the UI is open:

1. **Type your question** in the text box
2. **Select execution mode** using the radio buttons on the right:
   - 🤖 **Agentic (Multi-Agent)** - Uses specialized agents with LangChain
   - ✨ **Enhanced (Single LLM)** - Uses direct LLM API calls
   - 📊 **Legacy (Rule-Based)** - Uses pattern matching (no LLM)
3. **Click Send** or press Enter
4. **View the response** with agent name displayed at the bottom

### Example Workflow

```
1. Ask: "What is the delivery delay rate?"
   Mode: Enhanced (Single LLM)
   Result: "The delivery delay rate is 6.28%."
   Agent: Enhanced AI (LLM) - Llama 3.3 70B

2. Switch to: Agentic (Multi-Agent)
   Ask same question
   Result: Detailed analysis from Delay Agent
   Agent: Delay Agent (LangChain)

3. Switch to: Legacy (Rule-Based)
   Ask same question
   Result: Pattern-matched response
   Agent: Legacy Rule-Based System
```

## 🎯 Mode Comparison

### 🤖 Agentic Mode (Multi-Agent)

**Best for**: Complex queries, specialized analysis, comprehensive reports

**Features**:
- 4 specialized agents (Delay, Analytics, Forecasting, Data Query)
- Intelligent routing based on query intent
- LangChain tool calling
- Multi-agent orchestration

**Example Queries**:
```
- "What insights can you provide about delivery delays?"
- "Generate a comprehensive supply chain report"
- "Analyze delays by state and forecast demand"
```

**Agent Display**:
```
────────────────────────────────────────────────────────
🤖 Agent: Delay Agent (LangChain)
🎯 Orchestrator: Multi-Agent System
📊 Intent: delay (confidence: 0.80)
✅ Status: Success
────────────────────────────────────────────────────────
```

---

### ✨ Enhanced Mode (Single LLM)

**Best for**: General queries, fast responses, adaptive detail levels

**Features**:
- Single LLM (Llama 3.3 70B) via direct API
- Adaptive response complexity (simple/moderate/complex)
- Context-aware responses
- Lower API costs than agentic

**Example Queries**:
```
- "What is the delivery delay rate?"
  → Simple answer: "The delivery delay rate is 6.28%."

- "Show delivery performance"
  → Moderate answer with key metrics

- "What insights about delays?"
  → Complex answer with full analysis
```

**Agent Display**:
```
────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM)
📋 Model: Llama 3.3 70B
🎯 Query Complexity: Simple
────────────────────────────────────────────────────────
```

---

### 📊 Legacy Mode (Rule-Based)

**Best for**: Simple queries, offline use, no API costs

**Features**:
- Pattern matching based on keywords
- No LLM required (works without API key)
- Very fast responses
- Basic analytics only

**Example Queries**:
```
- "What is the delivery delay rate?"
- "Show revenue analysis"
- "Which states have delays?"
```

**Agent Display**:
```
────────────────────────────────────────────────────────
⚙️ Agent: Legacy Rule-Based System
📊 Mode: Pattern Matching
────────────────────────────────────────────────────────
```

## 🛠️ Command Line Options

### UI Mode (Default - All Modes Enabled)

```bash
# Standard UI mode - all modes available
python main.py

# Explicitly enable all modes
python main.py --init-all

# With RAG semantic search
python main.py --rag

# Hide agent info in responses
python main.py --hide-agent
```

### Specific Mode Only

```bash
# Agentic mode only
python main.py --agentic

# Enhanced mode only
python main.py --enhanced

# Legacy mode only
python main.py --legacy
```

### CLI Mode

```bash
# CLI with all modes (can't switch during conversation)
python main.py --mode cli

# CLI with specific mode
python main.py --mode cli --agentic
python main.py --mode cli --legacy
```

### Data Selection

```bash
# Use training data (default)
python main.py --data train

# Use test data
python main.py --data test
```

## 📋 Example Queries by Domain

### Delivery & Delays

```
Simple:
- "What is the delivery delay rate?"
- "What is the on-time rate?"

Moderate:
- "Show delivery performance"
- "Which states have the most delays?"

Complex:
- "What insights can you provide about delivery delays?"
- "Analyze delivery performance by state and time"
```

### Revenue & Sales

```
Simple:
- "What is total revenue?"
- "What is average order value?"

Moderate:
- "Show revenue analysis"
- "What are the revenue trends?"

Complex:
- "What insights about revenue and growth?"
- "Compare revenue across regions and products"
```

### Forecasting

```
Simple:
- "Forecast demand"

Moderate:
- "Forecast demand for 30 days"
- "What are the demand trends?"

Complex:
- "Forecast demand and provide insights"
- "What factors affect demand predictions?"
```

### Products & Customers

```
Simple:
- "How many products?"
- "How many customers?"

Moderate:
- "Analyze product performance"
- "Analyze customer behavior"

Complex:
- "What insights about customer lifetime value?"
- "Which products drive the most revenue?"
```

### Comprehensive

```
- "Generate comprehensive report"
- "Give me a complete overview"
- "Analyze all aspects of supply chain"
```

## 🎨 UI Features

### Mode Selector
- Radio buttons on the right side of the screen
- Three options: Agentic, Enhanced, Legacy
- Switch anytime during conversation
- Current mode highlighted

### Example Queries Sidebar
- Pre-written example questions
- Click to populate input field
- Covers different query types

### Agent Information Display
- Shows at bottom of each response
- Includes:
  - Agent name
  - Model/framework used
  - Query complexity (for Enhanced mode)
  - Intent & confidence (for Agentic mode)
- Can be hidden with `--hide-agent` flag

### Conversation History
- Scrollable chat interface
- User messages on left
- Bot responses on right
- Agent info included in responses

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for LLM modes (Agentic and Enhanced)
GROQ_API_KEY=your_groq_api_key_here

# Optional
RAG_ENABLED=false
LOG_LEVEL=INFO
```

### Get Groq API Key

1. Visit https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create new API key
5. Copy to `.env` file

## 📊 Mode Selection Decision Tree

```
Need offline/no API?
  └─> Use Legacy Mode

Need specialized domain expertise?
  └─> Use Agentic Mode

Need fast general responses?
  └─> Use Enhanced Mode

Want to compare approaches?
  └─> Use UI with all modes enabled (default)
```

## 🚨 Troubleshooting

### "Agentic mode not initialized"

**Problem**: Clicked Agentic in UI but it's not available

**Solution**:
```bash
# Restart in UI mode (all modes enabled)
python main.py
```

### "GROQ_API_KEY not set"

**Problem**: LLM modes require API key

**Solution**:
1. Create `.env` file in project root
2. Add: `GROQ_API_KEY=your_key_here`
3. Restart application

Or use Legacy mode (no API key needed):
```bash
python main.py --legacy
```

### Gradio "Data incompatible" error

**Problem**: Chat history format mismatch

**Solution**: This has been fixed in the latest version. If you still see it:
```bash
pip install --upgrade gradio
```

### Import errors (pandas, langchain, etc.)

**Problem**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

### Mode doesn't switch

**Problem**: Wrong startup mode

**Solution**: Restart in UI mode to enable all modes:
```bash
python main.py  # Not python main.py --agentic
```

## 💡 Tips & Best Practices

### For Best Results

1. **Use Agentic mode** for complex, multi-domain questions
2. **Use Enhanced mode** for general queries with adaptive detail
3. **Use Legacy mode** when offline or for simple lookups
4. **Try same query in different modes** to compare approaches
5. **Start with simple queries** to understand each mode

### Performance Tips

- Enhanced mode is faster than Agentic (single LLM call vs multiple)
- Legacy mode is fastest (no LLM calls)
- Complex queries benefit from Agentic mode's specialization
- Simple queries work well in any mode

### Cost Optimization

- Agentic mode: ~3-5 API calls per query (tool calling)
- Enhanced mode: 1 API call per query
- Legacy mode: 0 API calls (free)

## 📈 Example Session

```
Session Start: python main.py
UI Opens: http://localhost:7860

Query 1: "What is the delivery delay rate?"
Mode: Enhanced
Response: "The delivery delay rate is 6.28%."
Agent: Enhanced AI (LLM) | Simple Complexity

Query 2: [Switch to Agentic]
Same Question
Response: Full analysis with state breakdown
Agent: Delay Agent (LangChain) | Multi-Agent System

Query 3: [Switch to Legacy]
Same Question
Response: Basic stats from pattern matching
Agent: Legacy Rule-Based System

Query 4: "Generate comprehensive report"
Mode: Agentic
Response: Multi-agent report combining all agents
Agents Used: Delay, Analytics, Forecasting

Query 5: "Forecast demand for 30 days"
Mode: Agentic
Response: Specialized forecast with trends
Agent: Forecasting Agent (LangChain)
```

## 📚 Additional Resources

- [AGENTIC_ARCHITECTURE.md](AGENTIC_ARCHITECTURE.md) - Detailed architecture guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details
- [README.md](README.md) - Project overview
- [requirements.txt](requirements.txt) - Dependencies

## ✅ Quick Checklist

Before starting:
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] GROQ_API_KEY set in `.env` (for LLM modes)
- [ ] Data files in `data/train/` directory

To run:
- [ ] `python main.py` for UI with all modes
- [ ] Open http://localhost:7860
- [ ] Select mode using radio buttons
- [ ] Ask questions and compare responses!

---

**Need Help?** Check [AGENTIC_ARCHITECTURE.md](AGENTIC_ARCHITECTURE.md) for detailed documentation.

**Want to Extend?** See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details.
