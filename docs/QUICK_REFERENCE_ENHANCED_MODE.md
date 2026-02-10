# Quick Reference: Enhanced Mode Query Guide

**Purpose**: Quick decision guide for when to use RAG in Enhanced mode
**Updated**: February 10, 2026

---

## 🚦 Quick Decision Chart

```
Is your query about...

┌─────────────────────────────────────┐
│ POLICY, TARGETS, or GUIDELINES?     │
│ • "What are...?"                    │
│ • "What is the target?"             │
│ • "Compare with policy"             │
│ • "What is the requirement?"        │
└─────────────────────────────────────┘
           ↓
    📚 USE WITH RAG
    (REQUIRED for accuracy)


┌─────────────────────────────────────┐
│ DATA, METRICS, or COUNTS?           │
│ • "What is X?"                      │
│ • "Show me Y"                       │
│ • "How many Z?"                     │
│ • "Current performance"             │
└─────────────────────────────────────┘
           ↓
    💾 USE WITHOUT RAG
    (Faster, sufficient)
```

---

## 📊 Performance Summary

| Configuration | Avg Time | Speed | Accuracy | Use When |
|--------------|----------|-------|----------|----------|
| 💾 **Without RAG** | 28-33s | ⚡⚡⚡ | ✅ Data only | Need speed |
| 📚 **With RAG** | 48-55s | ⚡ | ✅✅ Data + Policy | Need policy |

**Speed Difference**: 40-45% faster without RAG

---

## ✅ Sample Queries - WITH RAG Required

| Query | Why RAG Needed | Without RAG Says |
|-------|----------------|------------------|
| "What are severity levels?" | Policy definition | "Cannot confirm" ❌ |
| "What is the on-time target?" | Policy target | "Cannot confirm" ❌ |
| "Compare actual vs policy" | Need policy for comparison | "Target not specified" ❌ |
| "Explain revenue thresholds" | Policy thresholds | Shows data patterns only ❌ |
| "What is delay classification?" | Policy classification | Infers from data ❌ |
| "What are the requirements?" | Policy requirements | "Cannot access policy" ❌ |

**Result Without RAG**: Incomplete or inaccurate answers

---

## ⚡ Sample Queries - WITHOUT RAG Works Fine

| Query | Why RAG Not Needed | Result Quality |
|-------|-------------------|----------------|
| "What is the delay rate?" | Pure data metric | ✅ Accurate, fast |
| "Show total revenue" | Data query | ✅ Complete data |
| "How many orders?" | Count query | ✅ Correct count |
| "List delayed orders" | Data retrieval | ✅ Full list |
| "Revenue by state" | Data breakdown | ✅ Complete breakdown |
| "Current performance" | Status query | ✅ Accurate status |

**Result Without RAG**: Complete and 40% faster

---

## 🎯 Real Query Examples with Actual Results

### Example 1: Policy Comparison ❗ REQUIRES RAG

**Query**: `"Compare actual delay rate with target policy"`

#### 📚 With RAG ✅
```
Actual delay rate: 6.28%
Target delay rate: < 5%
On-Time target: > 95%, actual: 93.72%
Average delay: 10.45 days, target: < 2.5 days

⏱️ Time: 52s
```
**Result**: ✅ Complete comparison with policy targets

#### 💾 Without RAG ❌
```
Actual delay rate: 6.28%
Target policy not specified in analytics results
Average delay days: 10.45 days

⏱️ Time: 32s
```
**Result**: ❌ Cannot do comparison without policy

**Verdict**: 📚 **MUST USE WITH RAG**

---

### Example 2: Simple Data Query ⚡ RAG Optional

**Query**: `"What is the delivery delay rate?"`

#### 📚 With RAG
```
Delay rate: 6.28%
Total Orders: 10,000
Delayed: 628 (6.28%)
Note: Exceeds policy target of <5%

⏱️ Time: 50s
```

#### 💾 Without RAG  ✅ RECOMMENDED
```
Delay rate: 6.28%
Total Orders: 10,000
Delayed: 628
On-Time: 93.72%

⏱️ Time: 28s (44% faster)
```

**Verdict**: 💾 **USE WITHOUT RAG** (faster, sufficient)

---

### Example 3: Policy Definition ❗ REQUIRES RAG

**Query**: `"What are severity levels?"`

#### 📚 With RAG ✅
```
• Critical: >5 days (escalation required)
• Major: 3-5 days (notification required)
• Minor: 1-2 days (monitoring required)

⏱️ Time: 55s
```
**Result**: ✅ Official policy definitions

#### 💾 Without RAG ❌
```
Based on data patterns:
• High: >5 days (89 orders)
• Medium: 3-5 days (245 orders)
• Low: 1-2 days (294 orders)
Note: Inferred, not official policy

⏱️ Time: 33s
```
**Result**: ❌ Guessed from data, not policy

**Verdict**: 📚 **MUST USE WITH RAG**

---

## 📋 Complete Query Categorization

### Category A: 📚 **ALWAYS Use WITH RAG**

```
Policy Questions:
✓ "What are [policy term]?"
✓ "Define [policy concept]"
✓ "Explain [guideline/requirement]"

Target Questions:
✓ "What is the target for...?"
✓ "What is the threshold for...?"
✓ "What are the limits for...?"

Comparison Questions:
✓ "Compare actual vs policy"
✓ "Compare with target"
✓ "Are we meeting [policy]?"
✓ "Compliance with [policy]"

Classification Questions:
✓ "What are severity levels?"
✓ "How are [items] classified?"
✓ "What are the categories?"
```

### Category B: 💾 **Can Use WITHOUT RAG**

```
Data Metrics:
✓ "What is the [metric]?"
✓ "Show [metric] value"
✓ "Current [performance]"

Counts:
✓ "How many [items]?"
✓ "Count of [items]"
✓ "Number of [items]"

Lists:
✓ "Show me [items]"
✓ "List all [items]"
✓ "Display [items]"

Breakdowns:
✓ "[Metric] by [dimension]"
✓ "Breakdown of [metric]"
✓ "Distribution of [items]"

Status:
✓ "Status of [item]"
✓ "Current state"
✓ "What is happening with...?"
```

---

## ⚠️ Common Mistakes

### Mistake 1: Using WITHOUT RAG for Policy Questions
```
❌ Query: "What are severity levels?"
❌ Config: WITHOUT RAG
❌ Result: Inaccurate guess from data

✅ Fix: Use WITH RAG
✅ Result: Official policy definition
```

### Mistake 2: Using WITH RAG for Simple Metrics
```
⚠️ Query: "What is delay rate?"
⚠️ Config: WITH RAG
⚠️ Result: Correct but 40% slower

✅ Better: Use WITHOUT RAG
✅ Result: Same accuracy, much faster
```

### Mistake 3: Expecting Formatted Policy Boxes
```
❌ Expectation: See formatted policy document boxes
❌ Reality: Policy info incorporated in natural language

✅ Understanding: Enhanced mode synthesizes policy into response
✅ Verification: Check if policy targets are mentioned
```

---

## 🔍 How to Verify RAG is Working

### Test 1: Policy Comparison
```bash
Query: "Compare actual delay rate with target policy"

WITH RAG: Should show specific targets (< 5%, > 95%)
WITHOUT RAG: Should say "Target policy not specified"
```

### Test 2: Definition Question
```bash
Query: "What are severity levels?"

WITH RAG: Should list Critical/Major/Minor with >5, 3-5, 1-2 days
WITHOUT RAG: Should say "based on data patterns" or "cannot confirm"
```

### Test 3: Target Question
```bash
Query: "What is the on-time delivery target?"

WITH RAG: Should say "> 95%"
WITHOUT RAG: Should say "cannot confirm official target"
```

---

## 💡 Pro Tips

### Tip 1: Check the Footer
```
🔍 RAG: Enabled (Semantic Search)  ← RAG is ON
🔍 RAG: Not shown  ← RAG is OFF
```

### Tip 2: Look for Policy Language
**WITH RAG** says:
- "Target is..."
- "Policy requires..."
- "According to guidelines..."

**WITHOUT RAG** says:
- "Target policy not specified"
- "Cannot confirm without policy"
- "Based on data patterns..."

### Tip 3: Speed Check
- **< 35s**: Probably WITHOUT RAG
- **> 45s**: Probably WITH RAG

---

## 📈 Use Case Examples

### Use Case 1: Quick Dashboard
```
Scenario: Ops team checking daily metrics
Queries: "Delay rate?", "Total orders?", "Revenue today?"
Config: 💾 WITHOUT RAG
Benefit: Fast updates (28-33s per query)
```

### Use Case 2: Compliance Report
```
Scenario: Monthly compliance check
Queries: "Compare actual vs targets", "Policy adherence"
Config: 📚 WITH RAG
Benefit: Accurate policy comparisons
```

### Use Case 3: Executive Briefing
```
Scenario: CEO wants performance update
Queries: Mix of data and policy questions
Config: 📚 WITH RAG
Benefit: Complete picture with policy context
```

### Use Case 4: Real-time Monitoring
```
Scenario: NOC monitoring current status
Queries: "Current delays?", "Active orders?"
Config: 💾 WITHOUT RAG
Benefit: Real-time speed
```

---

## 🎓 Training Guide

### For New Users

**Step 1**: Learn the basics
```
Data questions → WITHOUT RAG (faster)
Policy questions → WITH RAG (required)
```

**Step 2**: Try both configurations
```
Pick any query
Try WITH RAG → note time and answer
Try WITHOUT RAG → note time and answer
Compare results
```

**Step 3**: Build muscle memory
```
Before asking, think:
"Does this need policy documents?"
YES → Use WITH RAG
NO → Use WITHOUT RAG
```

---

## 📞 Quick Help

**Q: How do I know if I should use RAG?**
A: If query includes "policy", "target", "threshold", "requirement" → Use RAG

**Q: Why is WITH RAG so slow?**
A: It retrieves and processes policy documents (~20-25s overhead)

**Q: Can I see the policy documents?**
A: No visible boxes, but LLM uses them (see RAG_FORMATTING_INVESTIGATION.md)

**Q: Is WITHOUT RAG ever wrong?**
A: For data queries: No. For policy queries: Yes (cannot access policy)

**Q: Which is better?**
A: Depends on query type. Use decision chart above.

---

## 🔗 Related Documentation

- [ENHANCED_MODE_ACTUAL_RESULTS.md](ENHANCED_MODE_ACTUAL_RESULTS.md) - Detailed query results
- [RAG_FORMATTING_INVESTIGATION.md](RAG_FORMATTING_INVESTIGATION.md) - Why no document boxes
- [ENHANCED_MODE_QUERY_EXAMPLES.md](ENHANCED_MODE_QUERY_EXAMPLES.md) - Comprehensive examples

---

**Quick Reference v1.0** | Print this for your desk! 📋
