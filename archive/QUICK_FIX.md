# 🚨 Quick Fix: "Agentic mode not initialized" Error

## The Problem

You're seeing this error because the orchestrator failed to initialize due to missing dependencies (pandas, etc.).

## ✅ The Solution (Step by Step)

### Option 1: Use the Batch File (Easiest)

1. **Close** the currently running application (Ctrl+C if in terminal, or close browser and terminal)
2. **Double-click** `setup_and_run.bat` in Windows Explorer
3. Wait for dependencies to install
4. Application will start automatically

### Option 2: Manual Fix (3 Commands)

Open a **new terminal** in the project folder and run:

```bash
# Step 1: Activate virtual environment
venv\Scripts\activate

# Step 2: Install dependencies
pip install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core sentence-transformers faiss-cpu

# Step 3: Run application
python main.py
```

### Option 3: Without Virtual Environment

If venv doesn't work, install globally:

```bash
# Install dependencies globally
pip install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core

# Run application
python main.py
```

## 🔍 Verify It's Working

After running, you should see in the console:

```
🚀 SCM Chatbot Starting...
✅ Loaded 96,096 customers
✅ Loaded 89,316 orders
Initializing all modes for UI switching...
✅ Agent Orchestrator initialized      <-- THIS IS KEY!
✅ Enhanced chatbot initialized
✅ Setup complete!

🤖 Multi-Agent System Active:
   • Delay Agent - Delivery analysis
   • Analytics Agent - Revenue & customers
   • Forecasting Agent - Demand predictions
   • Data Query Agent - Raw data access
```

If you see "✅ Agent Orchestrator initialized", you're good to go!

## 🎯 Test It in the UI

1. Open http://localhost:7860
2. Select **🤖 Agentic (Multi-Agent)** mode
3. Ask: "What is the delivery delay rate?"
4. You should see a response with agent info:

```
────────────────────────────────────────────────────────
🤖 Agent: Delay Agent (LangChain)
🎯 Orchestrator: Multi-Agent System
📊 Intent: delay (confidence: 0.80)
✅ Status: Success
────────────────────────────────────────────────────────
```

## ❌ Still Not Working?

Run this diagnostic:

```bash
python check_modes.py
```

This will tell you exactly what's missing. Look for:

- ✅ or ❌ next to each mode
- Any error messages about missing modules
- Whether data loaded successfully

### Common Issues:

**"No module named 'pandas'"**
```bash
pip install pandas
```

**"No module named 'langchain'"**
```bash
pip install langchain langchain-groq langchain-core
```

**"GROQ_API_KEY not set"**
This is optional. The app will work in Legacy mode without it, but for Agentic and Enhanced modes:
1. Get API key from https://console.groq.com/
2. Create `.env` file in project root
3. Add: `GROQ_API_KEY=your_key_here`

**"Data loading failed"**
Make sure you have `data/train/` folder with CSV files:
- df_Customers.csv
- df_Orders.csv
- df_OrderItems.csv
- df_Payments.csv
- df_Products.csv

## 🎊 Success Checklist

- [ ] Dependencies installed (pandas, langchain, etc.)
- [ ] Virtual environment activated (if using venv)
- [ ] Application started with `python main.py`
- [ ] Console shows "Agent Orchestrator initialized"
- [ ] UI opened at http://localhost:7860
- [ ] All 3 mode buttons work (Agentic, Enhanced, Legacy)
- [ ] Agent name displays at bottom of responses

---

**Need more help?** Share the full console output when you run `python main.py`
