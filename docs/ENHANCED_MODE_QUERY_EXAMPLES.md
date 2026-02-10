# Enhanced Mode Query Examples - With vs Without RAG

**Date**: February 10, 2026
**Mode**: ✨ Enhanced (Single LLM)

---

## Overview

This guide provides example queries for **Enhanced (Single LLM)** mode with expected results for both RAG configurations:
- **📚 With RAG (Policy Documents)** - Comprehensive responses with policy context
- **💾 Without RAG (Data Only)** - Fast, data-focused responses

---

## Query Category 1: Data Queries (Metrics/Statistics)

### Query 1.1: "What is the delivery delay rate?"

#### With RAG (📚)
**Expected Time**: ~45-60 seconds
**Expected Response**:
```
The current delivery delay rate is 6.28%, based on recent order data.

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Performance Standards Policy | Relevance: 0.78

Target Performance:
• On-Time Delivery Target: >95%
• Maximum Acceptable Delay Rate: <5%
• Critical Delay Threshold: >5 business days

───────────────────────────────────────────────────────────

Analysis:
The current delay rate of 6.28% exceeds the policy target of <5%,
indicating performance is below acceptable standards and requires
corrective action.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 52.3s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~25-35 seconds
**Expected Response**:
```
The delivery delay rate is 6.28%.

Based on the analytics data:
• Total Orders: 10,000
• Delayed Orders: 628
• On-Time Orders: 9,372
• On-Time Rate: 93.72%

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 28.5s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ✅ Without RAG: **46% faster** (28.5s vs 52.3s)
- ✅ Without RAG: More focused on actual data
- ✅ With RAG: Includes policy context for comparison

---

### Query 1.2: "Show me total revenue"

#### With RAG (📚)
**Expected Time**: ~48-55 seconds
**Expected Response**:
```
Total Revenue: $1,245,678.90

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Revenue Targets Policy | Relevance: 0.72

Revenue Targets:
• Annual Target: $15,000,000
• Quarterly Target: $3,750,000
• Monthly Target: $1,250,000
• Minimum Product Revenue: $50,000/month

───────────────────────────────────────────────────────────

The current total revenue of $1,245,678.90 is tracking close to
the monthly target of $1,250,000, indicating strong performance.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 51.8s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~26-32 seconds
**Expected Response**:
```
Total Revenue: $1,245,678.90

Revenue Breakdown:
• Product Sales: $1,100,000.00 (88.3%)
• Services: $145,678.90 (11.7%)

Top Products:
1. Product A: $456,789.00
2. Product B: $345,678.00
3. Product C: $234,567.00

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 29.2s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ✅ Without RAG: **44% faster** (29.2s vs 51.8s)
- ✅ Without RAG: More detailed data breakdown
- ✅ With RAG: Includes target comparison

---

### Query 1.3: "How many orders are delayed?"

#### With RAG (📚)
**Expected Time**: ~47-58 seconds
**Expected Response**:
```
There are currently 628 delayed orders out of 10,000 total orders.

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Delay Classification Policy | Relevance: 0.85

Delay Severity Levels:
• Critical Delay: >5 business days (requires escalation)
• Major Delay: 3-5 business days (requires notification)
• Minor Delay: 1-2 business days (monitor)

───────────────────────────────────────────────────────────

Breakdown by Severity:
• Critical Delays: 89 orders (14.2% of delayed)
• Major Delays: 245 orders (39.0% of delayed)
• Minor Delays: 294 orders (46.8% of delayed)

Critical delays require immediate escalation per policy.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 54.1s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~27-34 seconds
**Expected Response**:
```
628 orders are currently delayed.

Delayed Orders:
• Total Delayed: 628 (6.28% of all orders)
• Average Delay: 4.2 days
• Total Orders: 10,000

Status Breakdown:
• In Transit (Late): 342 orders
• Pending Delivery: 286 orders

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 30.7s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ✅ Without RAG: **43% faster** (30.7s vs 54.1s)
- ✅ Without RAG: Focused on actual counts
- ✅ With RAG: Includes severity classification from policy

---

## Query Category 2: Policy Queries (Definitions/Guidelines)

### Query 2.1: "What are severity levels?"

#### With RAG (📚)
**Expected Time**: ~50-62 seconds
**Expected Response**:
```
### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Delay Management Policy | Relevance: 0.92

Delay Severity Levels:

• Critical Delay: >5 business days beyond committed delivery date
  - Requires: Immediate escalation to management
  - Action: Customer notification and expedited resolution
  - SLA Impact: Severe

• Major Delay: 3-5 business days beyond committed delivery date
  - Requires: Customer notification within 24 hours
  - Action: Investigation and corrective plan
  - SLA Impact: Moderate

• Minor Delay: 1-2 business days beyond committed delivery date
  - Requires: Internal tracking and monitoring
  - Action: Standard follow-up procedures
  - SLA Impact: Low

───────────────────────────────────────────────────────────

These severity levels are used to classify and prioritize delay
management activities across the supply chain.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Policy Documents
⏱️ Time: 56.4s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~28-36 seconds
**Expected Response**:
```
Based on the data patterns observed in our system, severity levels
appear to be classified as follows:

• High severity: Orders delayed more than 5 days
• Medium severity: Orders delayed 3-5 days
• Low severity: Orders delayed 1-2 days

Current Distribution:
• High: 89 orders (14.2%)
• Medium: 245 orders (39.0%)
• Low: 294 orders (46.8%)

Note: This classification is inferred from data patterns. For
official policy definitions, please refer to policy documentation.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 32.1s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ⚠️ **Without RAG**: Faster but **INCORRECT** - infers from data instead of policy
- ✅ **With RAG**: Provides **OFFICIAL** policy definitions
- 🎯 **Winner**: With RAG (accuracy matters more than speed for policy)

---

### Query 2.2: "What is the on-time delivery target?"

#### With RAG (📚)
**Expected Time**: ~48-58 seconds
**Expected Response**:
```
### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Performance Standards Policy | Relevance: 0.88

On-Time Delivery Target:

Target: >95% on-time delivery rate

Requirements:
• Orders must be delivered by or before committed delivery date
• Delivery window: Within business hours on scheduled date
• Weather delays: Excluded from on-time calculation (per policy)
• Force majeure: Excluded from SLA compliance

Measurement:
• Calculated monthly
• Reviewed quarterly
• Annual performance bonus tied to 12-month average

───────────────────────────────────────────────────────────

The target of >95% on-time delivery rate is the key performance
indicator for supply chain excellence.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Policy Documents
⏱️ Time: 53.7s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~26-34 seconds
**Expected Response**:
```
Based on current performance data:

Current On-Time Delivery Rate: 93.72%

Historical Performance:
• Last Month: 94.1%
• Last Quarter: 93.8%
• Year to Date: 94.3%

The data suggests a target around 95% based on typical performance
standards, but I cannot confirm the official target without access
to policy documents.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 30.3s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ⚠️ **Without RAG**: Cannot provide official target, only guesses
- ✅ **With RAG**: Provides exact policy target and requirements
- 🎯 **Winner**: With RAG (essential for policy questions)

---

### Query 2.3: "Explain revenue thresholds"

#### With RAG (📚)
**Expected Time**: ~51-63 seconds
**Expected Response**:
```
### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Revenue Management Policy | Relevance: 0.85

Revenue Thresholds:

Annual Thresholds:
• Excellent Performance: >$18,000,000
• Target Performance: $15,000,000 - $18,000,000
• Acceptable Performance: $12,000,000 - $15,000,000
• Below Target: <$12,000,000

Quarterly Thresholds:
• Q1: $3,500,000 (baseline)
• Q2: $3,750,000 (growth)
• Q3: $3,500,000 (seasonal dip)
• Q4: $4,250,000 (peak season)

Product Line Minimums:
• Core Products: >$50,000/month per product
• New Products: >$25,000/month (first 6 months)
• Seasonal Products: Variable by season

───────────────────────────────────────────────────────────

These thresholds guide business decisions and performance evaluation.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Policy Documents
⏱️ Time: 57.2s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~29-37 seconds
**Expected Response**:
```
Based on the revenue data analysis:

Current Revenue: $1,245,678.90

Revenue Distribution:
• Top 20% Products: $850,000 (68.2%)
• Middle 60% Products: $320,000 (25.7%)
• Bottom 20% Products: $75,678 (6.1%)

Average Product Revenue: $26,451/month

I can show you revenue patterns and distributions, but I cannot
provide the official threshold policies without access to policy
documents.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 33.4s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ⚠️ **Without RAG**: Cannot access policy thresholds
- ✅ **With RAG**: Provides complete threshold policy
- 🎯 **Winner**: With RAG (mandatory for policy information)

---

## Query Category 3: Mixed Queries (Data + Policy)

### Query 3.1: "Compare actual delay rate with target policy"

#### With RAG (📚)
**Expected Time**: ~52-65 seconds
**Expected Response**:
```
Performance vs Policy Comparison:

**Current Performance (Actual Data):**
• Delay Rate: 6.28%
• On-Time Rate: 93.72%
• Total Orders: 10,000
• Delayed Orders: 628

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Performance Standards Policy | Relevance: 0.90

Target Performance:
• On-Time Delivery Target: >95%
• Maximum Acceptable Delay Rate: <5%

───────────────────────────────────────────────────────────

**Analysis:**
❌ Performance Below Target
• Current: 93.72% on-time (Target: >95%)
• Gap: -1.28 percentage points
• Delay Rate: 6.28% (Target: <5%)
• Excess Delays: +1.28 percentage points

**Status**: Below acceptable performance standards
**Action Required**: Corrective measures needed to meet policy targets

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 58.9s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~30-38 seconds
**Expected Response**:
```
Current Delay Rate Performance:

**Actual Data:**
• Delay Rate: 6.28%
• On-Time Rate: 93.72%
• Total Orders: 10,000
• Delayed Orders: 628

**Historical Comparison:**
• Last Month: 5.8%
• Last Quarter: 6.1%
• Trend: Stable

I can provide the actual performance data, but I cannot compare
it to policy targets without access to policy documents. Based on
industry standards, a delay rate of 6.28% would typically be
considered above acceptable thresholds (usually <5%).

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 34.6s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ⚠️ **Without RAG**: Missing policy comparison, relies on "industry standards"
- ✅ **With RAG**: Complete comparison with actual policy
- 🎯 **Winner**: With RAG (essential for policy comparison)

---

### Query 3.2: "Are we meeting revenue targets?"

#### With RAG (📚)
**Expected Time**: ~50-62 seconds
**Expected Response**:
```
Revenue Target Analysis:

**Current Performance:**
• Total Revenue: $1,245,678.90

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Revenue Targets Policy | Relevance: 0.87

Monthly Target: $1,250,000

───────────────────────────────────────────────────────────

**Target Comparison:**
• Target: $1,250,000/month
• Actual: $1,245,678.90
• Variance: -$4,321.10 (-0.35%)

**Status**: ✅ Nearly Meeting Target
• Current performance is 99.65% of target
• Within acceptable variance range (<5%)
• Requires minor improvement to fully meet target

**Recommendation**: Continue current performance with minor
optimization to close the small gap.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 56.3s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~28-36 seconds
**Expected Response**:
```
Current Revenue Status:

**Revenue Data:**
• Total Revenue: $1,245,678.90
• Top Product: $456,789.00
• Average Order Value: $124.57

**Historical Performance:**
• Last Month: $1,198,543.00 (+3.9% MoM growth)
• Last Quarter Average: $1,223,456.00 (+1.8% vs Q avg)

The revenue appears to be performing well with positive growth,
but I cannot determine if targets are being met without access
to the official target policies.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 32.8s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ⚠️ **Without RAG**: Cannot answer the actual question (are we meeting targets?)
- ✅ **With RAG**: Direct answer with target comparison
- 🎯 **Winner**: With RAG (question requires policy knowledge)

---

## Query Category 4: Analytical Queries

### Query 4.1: "Show me revenue by state"

#### With RAG (📚)
**Expected Time**: ~49-58 seconds
**Expected Response**:
```
Revenue by State:

| State | Revenue | Percentage | Orders |
|-------|----------|-----------|--------|
| California | $523,456.78 | 42.0% | 4,200 |
| Texas | $345,678.90 | 27.7% | 2,890 |
| New York | $234,567.89 | 18.8% | 1,950 |
| Florida | $142,045.33 | 11.4% | 960 |

### 📚 Policy Documents

───────────────────────────────────────────────────────────
📄 Geographic Performance Standards | Relevance: 0.68

State Performance Targets:
• High-value states (CA, TX, NY): >$200,000/month
• Medium-value states (FL, IL, PA): >$100,000/month
• Other states: >$50,000/month

───────────────────────────────────────────────────────────

**Performance vs Targets:**
✅ California: $523,456 (Target: >$200,000) - Excellent
✅ Texas: $345,678 (Target: >$200,000) - Excellent
✅ New York: $234,567 (Target: >$200,000) - Excellent
✅ Florida: $142,045 (Target: >$100,000) - Excellent

All states meeting or exceeding targets.

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database, Policy Documents
⏱️ Time: 54.2s
────────────────────────────────────────────────────────────
```

#### Without RAG (💾)
**Expected Time**: ~27-35 seconds
**Expected Response**:
```
Revenue by State:

| State | Revenue | Percentage | Avg Order Value |
|-------|----------|-----------|-----------------|
| California | $523,456.78 | 42.0% | $124.63 |
| Texas | $345,678.90 | 27.7% | $119.58 |
| New York | $234,567.89 | 18.8% | $120.29 |
| Florida | $142,045.33 | 11.4% | $147.96 |

**Insights:**
• California generates the highest revenue
• Florida has the highest average order value
• Top 3 states account for 88.5% of total revenue

────────────────────────────────────────────────────────────
🤖 Agent: Enhanced AI (LLM) | ✅ Success
📁 Sources: Database
⏱️ Time: 31.4s
────────────────────────────────────────────────────────────
```

**Comparison**:
- ✅ Without RAG: **42% faster** and sufficient for data analysis
- ✅ With RAG: Adds target comparison
- 🎯 **Tie**: Both useful, depends on whether policy context needed

---

## Summary Comparison Table

| Query Type | Without RAG Time | With RAG Time | Speed Improvement | When to Use Without RAG | When to Use With RAG |
|------------|------------------|---------------|-------------------|------------------------|---------------------|
| **Data Queries** | 26-35s | 48-60s | 42-46% faster | ✅ Need fast metrics | Policy comparison needed |
| **Policy Queries** | 28-37s | 50-63s | 30-40% faster | ❌ Cannot answer correctly | ✅ Required for accuracy |
| **Mixed Queries** | 30-38s | 52-65s | 40-45% faster | ❌ Incomplete answers | ✅ Required for completeness |
| **Analytical Queries** | 27-35s | 49-58s | 40-45% faster | ✅ Pure data analysis | Policy context valuable |

---

## Recommendations

### Use **Without RAG (💾)** When:
1. ✅ Asking for pure metrics/statistics
2. ✅ Need fast responses (demos, quick checks)
3. ✅ Data analysis without policy context
4. ✅ Examples: "What is X?", "Show me Y", "How many Z?"

### Use **With RAG (📚)** When:
1. ✅ Asking about policies, definitions, guidelines
2. ✅ Need to compare actual vs target
3. ✅ Require official policy information
4. ✅ Examples: "What are severity levels?", "Compare actual vs policy", "What is the target?"

### ⚠️ Important Notes

**Policy Questions WITHOUT RAG**:
- Will attempt to answer but results may be inaccurate
- Often says "I cannot confirm without policy documents"
- May infer from data patterns (unreliable)
- **Not recommended for policy questions**

**Data Questions WITH RAG**:
- Slower but includes policy context
- Good for comprehensive understanding
- Useful for training/education
- Overkill for simple metric checks

---

## Testing These Queries

### Step 1: Start Application
```bash
python main.py --init-all
```

### Step 2: Select Enhanced Mode
- Choose "✨ Enhanced (Single LLM)"

### Step 3: Test With RAG
- Select "📚 With RAG (Policy Documents)"
- Try queries from this document
- Note response time and content

### Step 4: Test Without RAG
- Select "💾 Without RAG (Data Only)"
- Try same queries
- Compare response time and content

---

**End of Query Examples Guide**
