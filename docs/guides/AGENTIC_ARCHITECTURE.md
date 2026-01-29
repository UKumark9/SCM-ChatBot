# Multi-Agent Agentic Architecture

## Overview

The SCM Chatbot now supports **two execution modes**:

1. **Agentic Mode** (Multi-Agent) - Uses LangChain framework with specialized agents
2. **Non-Agentic Mode** (Enhanced/Legacy) - Uses direct LLM calls or rule-based patterns

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Interface                          │
│                     (Gradio Web UI / CLI)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Mode Selection                              │
│  🤖 Agentic  │  ✨ Enhanced  │  📊 Legacy                       │
└──────┬──────────────┬──────────────────┬───────────────────────┘
       │              │                  │
       ▼              ▼                  ▼
┌────────────┐ ┌─────────────┐  ┌────────────────┐
│ Orchestrator│ │  Enhanced   │  │   Rule-Based   │
│  (Agentic)  │ │   Chatbot   │  │    System      │
└──────┬──────┘ └─────────────┘  └────────────────┘
       │
       ├─────────────────────────────────────────┐
       │                                         │
       ▼                                         ▼
┌──────────────────────────┐          ┌──────────────────────┐
│    Delay Agent           │          │  Analytics Agent     │
│  (Delivery Analysis)     │          │  (Revenue, Products) │
└──────────────────────────┘          └──────────────────────┘
       │                                         │
       ▼                                         ▼
┌──────────────────────────┐          ┌──────────────────────┐
│  Forecasting Agent       │          │  Data Query Agent    │
│  (Demand Prediction)     │          │  (Raw Data Access)   │
└──────────────────────────┘          └──────────────────────┘
       │                                         │
       └───────────────┬─────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │   Analytics Engine       │
         │   (SCMAnalytics)        │
         └─────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │    Data Warehouse        │
         │  (Orders, Customers,     │
         │   Products, Payments)    │
         └─────────────────────────┘
```

## Specialized Agents

### 1. Delay Agent (`agents/delay_agent.py`)
**Purpose**: Analyze delivery delays and performance

**Tools**:
- `GetDelayStatistics` - Overall delay metrics
- `GetStateDelays` - Geographic delay analysis
- `GetDelayTrends` - Temporal delay patterns

**Queries**:
- "What is the delivery delay rate?"
- "Which states have the most delays?"
- "Show on-time delivery performance"

### 2. Analytics Agent (`agents/analytics_agent.py`)
**Purpose**: Analyze revenue, products, and customers

**Tools**:
- `GetRevenueAnalysis` - Revenue and growth metrics
- `GetProductPerformance` - Product sales analysis
- `GetCustomerBehavior` - Customer patterns and CLV

**Queries**:
- "Show revenue analysis"
- "Analyze product performance"
- "What is the customer repeat rate?"

### 3. Forecasting Agent (`agents/forecasting_agent.py`)
**Purpose**: Predict future demand and trends

**Tools**:
- `ForecastDemand30Days` - 30-day predictions
- `ForecastDemand60Days` - 60-day predictions
- `ForecastDemand90Days` - 90-day predictions

**Queries**:
- "Forecast demand for 30 days"
- "What are the demand trends?"
- "Predict next month's orders"

### 4. Data Query Agent (`agents/data_query_agent.py`)
**Purpose**: Query raw data records

**Tools**:
- `QueryOrders` - Retrieve order records
- `QueryCustomers` - Retrieve customer data
- `QueryProducts` - Retrieve product information
- `GetDataSummary` - Overall data statistics

**Queries**:
- "Show me order details"
- "List customer data"
- "Get data summary"

### 5. Agent Orchestrator (`agents/orchestrator.py`)
**Purpose**: Central coordinator that routes queries to appropriate agents

**Features**:
- Intent analysis
- Intelligent routing
- Multi-agent coordination
- Comprehensive reporting (uses multiple agents)

## Usage

### 1. Agentic Mode (Multi-Agent)

```bash
# Start with agentic mode
python main.py --agentic

# With RAG support
python main.py --agentic --rag

# CLI mode
python main.py --mode cli --agentic
```

**Features**:
- ✅ Specialized agents for different domains
- ✅ LangChain framework with tool calling
- ✅ Intelligent query routing
- ✅ Multi-agent orchestration
- ✅ Comprehensive reports from multiple agents

### 2. Enhanced Mode (Single LLM)

```bash
# Start with enhanced mode (default)
python main.py

# Or explicitly
python main.py --enhanced
```

**Features**:
- ✅ Direct Groq API calls
- ✅ Adaptive response complexity
- ✅ Single LLM for all queries
- ✅ Faster responses
- ✅ Lower API usage

### 3. Legacy Mode (Rule-Based)

```bash
# Start with legacy mode
python main.py --legacy
```

**Features**:
- ✅ No LLM required
- ✅ Pattern-based matching
- ✅ Fast keyword search
- ✅ Works offline

## Web UI Mode Selection

The Gradio UI now includes a **Mode Selector** dropdown:

```
┌─────────────────────────────────────────────┐
│  🤖 SCM Intelligent Chatbot                 │
│  Current Mode: Multi-Agent System           │
├─────────────────────────────────────────────┤
│                                             │
│  [Conversation History]                     │
│                                             │
│  ┌─────────────────────────────────┐       │
│  │ Ask a question...               │       │
│  └─────────────────────────────────┘       │
│                                             │
├─────────────────────────────────────────────┤
│  Mode Selection:                            │
│  ○ 🤖 Agentic (Multi-Agent)                │
│  ○ ✨ Enhanced (Single LLM)                │
│  ○ 📊 Legacy (Rule-Based)                  │
└─────────────────────────────────────────────┘
```

Users can switch modes during the conversation to compare responses.

## Implementation Details

### Agent Communication Flow

1. **User Query** → Gradio UI
2. **Mode Selection** → Determine execution path
3. **Agentic Path**:
   - Query → Orchestrator
   - Orchestrator → Intent Analysis
   - Intent → Route to Specialized Agent
   - Agent → Use LangChain Tools
   - Tools → Analytics Engine
   - Response → Back to User

4. **Enhanced Path**:
   - Query → Enhanced Chatbot
   - Chatbot → Intent Detection
   - Intent → Analytics Data
   - Data + Query → Single LLM Call
   - Response → Back to User

5. **Legacy Path**:
   - Query → Pattern Matching
   - Pattern → Analytics Function
   - Result → Formatted Response

### LangChain Integration

Agentic mode uses LangChain components:

```python
from langchain_groq import ChatGroq
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
```

Each agent has:
- **LLM**: ChatGroq with Llama 3.3 70B
- **Tools**: Specialized functions wrapped as Tools
- **Prompt**: System prompt defining agent expertise
- **Executor**: AgentExecutor to run agent loop

### Non-Agentic Integration

Enhanced mode uses direct API:

```python
from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...]
)
```

## Configuration

### Environment Variables

```bash
# Required for LLM features (both modes)
GROQ_API_KEY=your_api_key_here
```

### Command Line Arguments

```bash
--mode cli|ui          # Interface mode (default: ui)
--data train|test      # Dataset to use (default: train)
--agentic              # Enable multi-agent mode
--enhanced             # Enable enhanced LLM mode (default)
--legacy               # Enable rule-based mode
--rag                  # Enable RAG semantic search
--hide-agent           # Hide agent info in responses
```

## Performance Comparison

| Feature | Agentic | Enhanced | Legacy |
|---------|---------|----------|--------|
| **Response Time** | Medium | Fast | Very Fast |
| **Accuracy** | High | High | Medium |
| **Complexity Handling** | Excellent | Good | Basic |
| **API Calls** | Multiple | Single | None |
| **Cost** | Higher | Medium | Free |
| **Offline Mode** | No | No | Yes |
| **Specialization** | High | Medium | Low |

## When to Use Each Mode

### Use Agentic Mode When:
- ✅ Need specialized domain expertise
- ✅ Complex queries requiring multiple analyses
- ✅ Want comprehensive reports
- ✅ Need tool calling and agentic behavior
- ✅ Have sufficient API budget

### Use Enhanced Mode When:
- ✅ Need fast responses
- ✅ Simple to moderate queries
- ✅ Want adaptive detail levels
- ✅ Limited API budget
- ✅ Single-domain questions

### Use Legacy Mode When:
- ✅ No API key available
- ✅ Need offline operation
- ✅ Simple keyword-based queries
- ✅ Very fast responses required
- ✅ No LLM dependencies desired

## Agent Response Format

All agents include metadata in responses:

```
[Response content here]

────────────────────────────────────────────────────────
🤖 Agent: Delay Agent (LangChain)
🎯 Orchestrator: Multi-Agent System
📊 Intent: delay (confidence: 0.80)
✅ Status: Success
────────────────────────────────────────────────────────
```

Use `--hide-agent` flag to disable metadata display.

## Extending the System

### Adding a New Agent

1. Create new agent file in `agents/`:
```python
# agents/my_agent.py
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

class MyAgent:
    def __init__(self, data_source, llm_client, use_langchain):
        # Initialize agent
        pass

    def query(self, user_query):
        # Process query
        return {'response': '...', 'agent': 'My Agent', 'success': True}
```

2. Register in `agents/orchestrator.py`:
```python
from agents.my_agent import MyAgent

self.my_agent = MyAgent(
    data_source=data,
    llm_client=self.llm_client,
    use_langchain=self.use_langchain
)
```

3. Add routing logic:
```python
def analyze_intent(self, query):
    if 'my_keyword' in query.lower():
        intent['agent'] = 'my_agent'
```

## Troubleshooting

### Agentic Mode Not Available
- Ensure LangChain is installed: `pip install langchain langchain-groq langchain-core`
- Set GROQ_API_KEY in `.env` file
- Restart with `--agentic` flag

### Agent Selection Issues
- Check logs for intent analysis results
- Verify keyword patterns in orchestrator
- Try explicit queries matching agent domains

### Tool Calling Errors
- Verify analytics engine is initialized
- Check data wrapper has required methods
- Review agent tool definitions

## Files Modified

- `agents/delay_agent.py` - Delivery delay specialist
- `agents/analytics_agent.py` - Revenue & customer specialist
- `agents/forecasting_agent.py` - Demand prediction specialist
- `agents/data_query_agent.py` - Raw data query specialist
- `agents/orchestrator.py` - Central coordinator
- `agents/__init__.py` - Package exports
- `main.py` - Added agentic mode support and UI selector

## Next Steps

1. ✅ Test both modes with sample queries
2. ✅ Compare response quality and speed
3. ✅ Optimize agent prompts for better routing
4. ✅ Add more specialized agents (e.g., Supplier Agent, Inventory Agent)
5. ✅ Implement agent memory and conversation history
6. ✅ Add streaming responses in Gradio UI
7. ✅ Create agent performance analytics dashboard

## References

- LangChain Documentation: https://python.langchain.com/
- Groq API: https://console.groq.com/
- Gradio Documentation: https://www.gradio.app/
