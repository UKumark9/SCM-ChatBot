# SCM Chatbot - Quick Reference Card

## 🚀 Quick Start

```bash
# Start the chatbot (Enhanced AI)
python main.py

# CLI mode
python main.py --mode cli

# With semantic search
python main.py --rag
```

---

## 📊 Top 20 Most Useful Queries

### Delivery Performance (5 queries)
1. `What is the delivery delay rate?`
2. `Show on-time delivery performance`
3. `Which states have the most delays?`
4. `What's the average delay time?`
5. `Compare delivery performance by region`

### Revenue Analysis (5 queries)
6. `Show revenue trends`
7. `What's the total revenue?`
8. `What is the monthly growth rate?`
9. `Which month had highest revenue?`
10. `Analyze revenue by state`

### Product Insights (3 queries)
11. `Analyze product performance`
12. `What are the top selling categories?`
13. `Show product statistics`

### Customer Behavior (3 queries)
14. `Analyze customer behavior`
15. `What's the repeat customer rate?`
16. `Show customer lifetime value`

### Forecasting (2 queries)
17. `Forecast demand for next 30 days`
18. `What are the demand trends?`

### Comprehensive (2 queries)
19. `Generate comprehensive report`
20. `What are the key supply chain insights?`

---

## 🎯 Query Templates

### Pattern: Delivery
```
"What is [metric] for [geography]?"
"Show [delivery/delay/on-time] [performance/rate]"
"Which [states/regions] have [most/least] [delays]?"
```

### Pattern: Revenue
```
"What is the [total/average] revenue [for time]?"
"Show revenue [trends/growth/analysis]"
"Compare revenue [across regions/over time]"
```

### Pattern: Analysis
```
"Analyze [product/customer/delivery] [performance/behavior]"
"What insights do you have about [topic]?"
"Show me [comprehensive/detailed] [report/analysis]"
```

---

## 🔧 Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--mode cli` | Command line interface | `python main.py --mode cli` |
| `--mode ui` | Web interface (default) | `python main.py --mode ui` |
| `--rag` | Enable semantic search | `python main.py --rag` |
| `--legacy` | Rule-based only | `python main.py --legacy` |
| `--data train` | Use training data | `python main.py --data train` |
| `--data test` | Use test data | `python main.py --data test` |

---

## 💡 Natural Language Examples

### Conversational Style
```
"How is our supply chain doing?"
"What should I focus on improving?"
"Explain the delivery performance"
"What patterns do you see in the data?"
"Help me understand customer behavior"
```

### Comparison Style
```
"Compare delays across states"
"Which is better: North or South region?"
"Show the difference between Q1 and Q2"
"Revenue vs last year?"
```

### Analytical Style
```
"What causes delivery delays?"
"Why is revenue growing/declining?"
"Identify bottlenecks"
"What are the main issues?"
"Root cause of delays"
```

---

## 📈 Expected Response Format

### Delivery Query
```
📊 Delivery Performance Analysis:
- Total Orders: 95,329
- Delayed Orders: 11,921
- Delay Rate: 12.51%
- Average Delay: 8.3 days
```

### Revenue Query
```
💰 Revenue Analysis:
- Total Revenue: $15.4M
- Average Order Value: $161.89
- Growth Rate: 3.45%
```

### Comprehensive Report
```
📋 Comprehensive Supply Chain Report
## Delivery: 12.5% delay rate
## Revenue: $15.4M total
## Products: 32,951 unique
## Customers: 96,096 active
```

---

## ⚡ Tips for Best Results

### DO ✅
- Be specific in your queries
- Use natural language
- Ask follow-up questions
- Request comparisons
- Ask for insights

### DON'T ❌
- Use vague terms like "show data"
- Ask without context
- Expect exact keywords
- Ignore follow-up options

---

## 🔑 Environment Setup

```bash
# Required for AI features
export GROQ_API_KEY="your_key_here"

# Windows
set GROQ_API_KEY=your_key_here
```

Get free key: https://console.groq.com/

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data" | Check CSV files in `data/train/` |
| "Analytics not initialized" | Verify data loading succeeded |
| LLM not working | Set `GROQ_API_KEY` or use `--legacy` |
| RAG errors | Install: `pip install faiss-cpu sentence-transformers` |
| Slow responses | Use `--legacy` for faster rule-based mode |

---

## 📚 More Resources

- **Detailed Guide**: See `PROMPTS_GUIDE.md`
- **Improvements**: See `IMPROVEMENTS_SUMMARY.md`
- **Code**: Check inline documentation

---

## 🎓 Learning Path

### Beginner Queries
1. "What is the delivery delay rate?"
2. "Show revenue analysis"
3. "Analyze product performance"

### Intermediate Queries
4. "Which states have most delays?"
5. "Compare revenue across regions"
6. "Show demand forecast"

### Advanced Queries
7. "What insights can you provide?"
8. "Explain the revenue trends"
9. "Identify supply chain bottlenecks"

---

## 📞 Quick Support

**Console shows errors?**
- Check data files exist
- Verify API key set
- Try `--legacy` mode

**Want faster responses?**
- Use `--legacy` mode
- Disable RAG
- Use specific queries

**Need better insights?**
- Enable `--rag`
- Use conversational queries
- Ask follow-up questions

---

## 🔗 Quick Links

- Start chatbot: `python main.py`
- CLI mode: `python main.py --mode cli`
- Full docs: `PROMPTS_GUIDE.md`
- Get API key: https://console.groq.com/

---

**Version**: 2.0 Enhanced | **Updated**: 2026-01-27
