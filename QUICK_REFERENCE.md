# SCM Chatbot - Quick Reference Guide

## 🚀 What's New in Version 2.2

### ✨ Automatic RAG Integration
- **RAG now enabled by default** - No `--rag` flag needed!
- All agents automatically use RAG for better answers
- System gracefully works without RAG if dependencies missing

### 👥 Enhanced Multi-Agent Display
- See which agents were executed
- See which agents used RAG
- Clear multi-agent query handling

### 🎯 Improved Query Understanding
- Compound queries automatically route to multiple agents
- Example: "Show delays and forecast demand" → Runs both agents!

---

## 🤖 Agents in the System

| Agent | Role | What It Does |
|-------|------|--------------|
| **Delay Agent** | Logistics Manager | Delivery delays, on-time performance, carrier analysis |
| **Analytics Agent** | Business Analyst | Revenue, sales, customer behavior, product performance |
| **Forecasting Agent** | Demand Planner | Demand predictions (30/60/90 days), trend analysis |
| **Data Query Agent** | Operations Manager | Order lookups, customer records, raw data queries |

---

## 📝 Example Queries

### Single Agent Queries

```
"What is the delivery delay rate?"
→ Delay Agent + RAG

"Show revenue analysis"
→ Analytics Agent + RAG

"Forecast demand for next month"
→ Forecasting Agent + RAG

"Find order #12345"
→ Data Query Agent + RAG
```

### Multi-Agent Queries (NEW!)

```
"Show delays and forecast demand"
→ Delay Agent + Forecasting Agent + RAG

"Revenue analysis and customer behavior"
→ Analytics Agent + RAG

"Show delays, revenue, and demand forecast"
→ All agents + RAG
```

---

## 📊 Understanding the Output

### Single Agent Response

```
Delay Statistics:
- Delay Rate: 6.28%
- On-Time Rate: 93.72%

📚 Additional Context from Documents:
[Context from uploaded policy documents...]

────────────────────────────────────────────────────────────
🤖 Agent: Delay Agent + RAG
📚 RAG: Enabled (context retrieved from documents)
🎯 Orchestrator: Multi-Agent System
📊 Intent: Delay (confidence: 0.20)
✅ Status: Success
────────────────────────────────────────────────────────────
```

**What This Means:**
- ✅ Delay Agent ran
- ✅ RAG retrieved relevant context from documents
- ✅ Response combines analytics + document context

### Multi-Agent Response

```
📊 DELIVERY PERFORMANCE
Delay Rate: 6.28%
...

📈 DEMAND FORECAST
30-Day Forecast: 12,450 units
...

────────────────────────────────────────────────────────────
🤖 Agents Executed: Delay, Forecasting
📚 RAG Used By: Delay, Forecasting
────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
🤖 Agent: Multi-Agent Orchestrator (2 agents)
👥 Agents Executed: Delay, Forecasting
📚 RAG Used By: Delay, Forecasting
🎯 Orchestrator: Multi-Agent System
📊 Intent: Multi-Intent Query
✅ Status: Success
────────────────────────────────────────────────────────────
```

**What This Means:**
- ✅ Both Delay and Forecasting agents ran
- ✅ Both agents used RAG to find relevant context
- ✅ Response shows output from each agent

---

## 🔧 Startup

### Quick Start

```bash
# Just run - RAG enabled automatically!
python main.py

# Open browser
http://localhost:7860
```

### With RAG (Recommended)

```bash
# Install RAG dependencies first
pip install sentence-transformers faiss-cpu

# Run application
python main.py
```

**Output:**
```
✅ RAG module initialized successfully
   📊 Indexed documents: 1000
   🔍 Vector search: Enabled
   📚 Agents will use RAG + Analytics
```

### Without RAG

```bash
# If dependencies missing, system continues without RAG
python main.py
```

**Output:**
```
⚠️  RAG dependencies missing
📊 Continuing without RAG - agents will use analytics only
```

**System works fine! Agents use analytics only.**

---

## 📚 Uploading Documents

### Via UI

1. Open UI: http://localhost:7860
2. Go to **"Documents"** tab
3. Select file (PDF, DOCX, TXT, MD)
4. Choose category (Policy, Procedure, Guide, etc.)
5. Add description (optional)
6. Click **"Upload Document"**

**Uploaded documents are automatically:**
- ✅ Stored in `data/business_docs/`
- ✅ Text extracted
- ✅ Vectorized for RAG search
- ✅ Available to all agents immediately

### Document Storage

```
scm_chatbot/
├── data/
│   ├── business_docs/           ← Your uploaded documents
│   │   ├── {hash}_filename.pdf
│   │   ├── {hash}_policy.docx
│   │   └── documents_metadata.json
```

---

## 🎯 When to Use Each Mode

### Agentic Mode (Multi-Agent) 🤖
**Best For:**
- Complex questions requiring multiple perspectives
- Comprehensive analysis
- When accuracy is critical

**Example:**
```
"Give me a complete supply chain report"
→ All 4 agents run + RAG
```

### Enhanced Mode (Single LLM) ✨
**Best For:**
- Quick questions
- General inquiries
- When speed matters

**Example:**
```
"What's the average delay?"
→ Fast LLM response + analytics
```

### Legacy Mode (Rule-Based) 📊
**Best For:**
- Offline operation
- No API key available
- Simple keyword queries

**Example:**
```
"delay rate"
→ Fast keyword match
```

---

## 📁 Project Structure

```
scm_chatbot/
├── main.py                      # Main application
├── agents/                      # Multi-agent system
│   ├── delay_agent.py          # Delivery delays
│   ├── analytics_agent.py      # Revenue & analytics
│   ├── forecasting_agent.py    # Demand forecasting
│   ├── data_query_agent.py     # Data queries
│   └── orchestrator.py         # Agent coordinator
├── rag.py                       # RAG module
├── feature_store.py             # ML feature caching
├── document_manager.py          # Document upload/management
├── data_connectors.py           # Database connectors
├── data/
│   ├── train/                   # Training data (CSV)
│   ├── business_docs/           # Uploaded documents
│   └── feature_store/           # Cached ML features
└── docs/
    ├── RAG_AUTO_DETECTION.md    # Technical details
    ├── REAL_WORLD_APPLICATION.md # Business impact
    └── MULTI_INTENT_FIX.md      # Multi-agent fix
```

---

## 🆘 Troubleshooting

### "RAG dependencies missing"

**Solution:**
```bash
pip install sentence-transformers faiss-cpu
```

Then restart:
```bash
python main.py
```

### "Multi-intent not detected"

**Your Query:**
```
"delays and forecast"  # Too short
```

**Better Query:**
```
"What is the delivery delay rate? Forecast demand for 30 days"
```

Each intent needs **≥2 keyword matches** for detection.

### "Agents not showing"

Check the footer of the response:
```
────────────────────────────────────────────────────────────
👥 Agents Executed: Delay, Forecasting
📚 RAG Used By: Delay
────────────────────────────────────────────────────────────
```

This shows which agents ran!

---

## 📊 Statistics & Monitoring

### Via UI

1. Go to **"Statistics"** tab
2. Click **"Refresh Statistics"**

**Shows:**
- Total documents uploaded
- Vectorized documents
- Feature store size
- Documents by category

---

## 🎯 Tips for Best Results

### Writing Good Queries

✅ **Good:**
```
"What is the delivery delay rate? Forecast demand for 30 days"
→ Clear, specific, multiple intents
```

❌ **Avoid:**
```
"delays and stuff"
→ Vague, won't trigger multi-agent
```

### Using RAG Effectively

1. **Upload Relevant Documents**
   - Company policies
   - Product catalogs
   - Historical reports
   - SOPs and procedures

2. **Use Descriptive Names**
   - `return_policy_2026.pdf` ✅
   - `document1.pdf` ❌

3. **Add Categories**
   - Helps organize documents
   - Improves search relevance

---

## 📞 Support

### Documentation

- **[RAG_AUTO_DETECTION.md](docs/RAG_AUTO_DETECTION.md)** - Full RAG technical details
- **[REAL_WORLD_APPLICATION.md](docs/REAL_WORLD_APPLICATION.md)** - Business impact & use cases
- **[MULTI_INTENT_FIX.md](docs/MULTI_INTENT_FIX.md)** - Multi-agent query handling

### Diagnostics

```bash
# Test new features
python scripts/diagnostics/test_new_features.py

# Test multi-intent detection
python scripts/test_multi_intent.py
```

---

## 🎉 Summary

**What Changed:**
- ✅ RAG enabled automatically
- ✅ All agents use RAG
- ✅ Multi-agent queries work
- ✅ Clear agent execution display
- ✅ RAG usage transparency

**How to Use:**
1. Start application: `python main.py`
2. Ask questions naturally
3. System automatically uses right agents + RAG
4. See which agents ran in the footer

**That's it! The system handles everything else automatically.** 🚀

---

**Version:** 2.2 (RAG Auto-Detection)
**Last Updated:** January 29, 2026
