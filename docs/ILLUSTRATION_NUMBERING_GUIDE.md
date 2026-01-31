# Quick Guide: Adding Figure and Table Numbers

**Task:** Add proper numbering and titles to all illustrations in your dissertation
**Time Required:** 3-4 hours
**Difficulty:** Easy
**WILP Requirement:** Mandatory

---

## 🎯 Goal

Transform informal mentions like:
> "The architecture diagram shows..."

Into formal WILP-compliant references:
> "Figure 3.1 shows the multi-agent system architecture..."

---

## 📋 Step-by-Step Process

### Step 1: Identify All Visual Elements (30 minutes)

Go through each chapter and mark every place where you need a figure or table:

**Look for:**
- Diagrams and architectures
- Flowcharts and processes
- Data comparisons
- Performance metrics
- Test results
- Any lists of data that should be tabular

**Mark them with:**
```
[FIGURE NEEDED: Architecture diagram]
[TABLE NEEDED: Performance metrics]
```

---

### Step 2: Number Sequentially (30 minutes)

**Numbering Format:**
- Chapter.Sequential → Figure 3.1, 3.2, 4.1, 4.2, etc.
- Same for tables → Table 3.1, 3.2, 4.1, 4.2, etc.

**Example Mapping:**

**Chapter 2 (Literature Review):**
- Table 2.1: Comparison of Chatbot Technologies
- Figure 2.1: Evolution of Multi-Agent Systems

**Chapter 3 (System Design):**
- Figure 3.1: Multi-Agent System Architecture
- Figure 3.2: RAG Integration Workflow
- Table 3.1: Functional Requirements Summary
- Table 3.2: Non-Functional Requirements
- Table 3.3: Technology Stack Comparison

**Chapter 4 (Implementation):**
- Figure 4.1: Database Schema Diagram
- Figure 4.2: Agent Communication Flow
- Figure 4.3: Document Processing Pipeline
- Figure 4.4: Vector Database Structure
- Table 4.1: Database Tables and Fields
- Table 4.2: Agent Capabilities Matrix

**Chapter 5 (Testing):**
- Table 5.1: Unit Test Results
- Table 5.2: Integration Test Cases
- Table 5.3: Multi-Intent Detection Validation
- Figure 5.1: Test Coverage Distribution
- Figure 5.2: RAG Retrieval Accuracy

**Chapter 6 (Results):**
- Table 6.1: Query Performance Metrics
- Table 6.2: RAG Effectiveness Metrics
- Table 6.3: User Satisfaction Scores
- Figure 6.1: Response Time Comparison
- Figure 6.2: Multi-Intent Detection Accuracy
- Figure 6.3: System Throughput Under Load

**Chapter 7 (Deployment):**
- Table 7.1: Cost-Benefit Analysis
- Table 7.2: Scalability Metrics
- Figure 7.1: Enterprise Integration Architecture

---

### Step 3: Add Formal Titles and Captions (1 hour)

**Format for Figures:**
```markdown
**Figure 3.1: Multi-Agent System Architecture**

[Diagram or image]

*This diagram illustrates the interaction between four specialized agents
(Delay, Analytics, Forecasting, Data Query) coordinated by the orchestrator,
with bidirectional data flow from the analytics engine and RAG module.*
```

**Format for Tables:**
```markdown
**Table 5.1: Performance Benchmark Results**

| Query Type | Avg Response Time | Accuracy | Satisfaction |
|------------|------------------|----------|--------------|
| Single-Agent | 2.8s | 94% | 4.2/5 |
| Multi-Agent | 6.5s | 97% | 4.7/5 |
| With RAG | 3.2s | 96% | 4.6/5 |

*Note: Results based on 100 test queries across diverse scenarios.*
```

---

### Step 4: Reference in Text (1 hour)

**Before (informal):**
> "The system architecture has four specialized agents..."

**After (formal):**
> "The system architecture (Figure 3.1) comprises four specialized agents..."

OR

> "Figure 3.1 shows the system architecture with four specialized agents..."

**For Tables:**
> "Performance results are summarized in Table 6.1..."
> "As shown in Table 5.1, unit test coverage exceeded 90%..."

---

### Step 5: Create List of Figures (30 minutes)

**Add after Table of Contents:**

```markdown
## LIST OF FIGURES

Figure 2.1: Evolution of Conversational AI Technologies ................ 8
Figure 3.1: Multi-Agent System Architecture .......................... 20
Figure 3.2: RAG Integration Workflow ................................. 27
Figure 4.1: Database Schema Diagram .................................. 29
Figure 4.2: Agent Communication Flow ................................. 35
Figure 4.3: Document Processing Pipeline ............................. 50
Figure 4.4: Vector Database Structure ................................ 52
Figure 5.1: Test Coverage Distribution ............................... 61
Figure 5.2: RAG Retrieval Accuracy Metrics ........................... 67
Figure 6.1: Query Response Time Comparison ........................... 73
Figure 6.2: Multi-Intent Detection Accuracy .......................... 75
Figure 6.3: System Throughput Under Load ............................. 77
Figure 7.1: Enterprise Integration Architecture ...................... 84
```

---

### Step 6: Create List of Tables (30 minutes)

```markdown
## LIST OF TABLES

Table 2.1: Comparison of Chatbot Technologies ......................... 9
Table 3.1: Functional Requirements Summary ........................... 18
Table 3.2: Non-Functional Requirements ............................... 19
Table 3.3: Technology Stack Comparison ............................... 23
Table 4.1: Database Tables and Fields ................................ 28
Table 4.2: Agent Capabilities Matrix ................................. 36
Table 5.1: Unit Test Results Summary ................................. 60
Table 5.2: Integration Test Cases .................................... 62
Table 5.3: Multi-Intent Detection Validation ......................... 64
Table 6.1: Query Performance Metrics ................................. 72
Table 6.2: RAG Effectiveness Metrics ................................. 76
Table 6.3: User Satisfaction Scores .................................. 78
Table 7.1: Cost-Benefit Analysis ..................................... 82
Table 7.2: Scalability Metrics ....................................... 85
```

---

## 📝 Templates to Use

### Template 1: Simple Figure

```markdown
**Figure 4.2: Agent Communication Flow**

[Insert diagram/flowchart here]

*This flowchart illustrates the message passing sequence when a multi-intent
query is processed. The orchestrator analyzes intent, routes to appropriate
agents in optimal sequence, and synthesizes their responses.*
```

### Template 2: Data Table

```markdown
**Table 6.1: Query Performance Metrics**

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Avg Response Time (Single) | 2.8s | <3s | ✅ Pass |
| Avg Response Time (Multi) | 6.5s | <10s | ✅ Pass |
| Accuracy | 96% | >90% | ✅ Pass |
| Throughput | 45 queries/min | >30 | ✅ Pass |

*Metrics collected over 500 test queries across all agent types.*
```

### Template 3: Comparison Table

```markdown
**Table 2.1: Comparison of Chatbot Technologies**

| Feature | Rule-Based | ML-Based | LLM-Based | This Work |
|---------|------------|----------|-----------|-----------|
| Natural Language | Limited | Good | Excellent | Excellent |
| Domain Knowledge | Fixed | Trained | General | Specialized |
| Accuracy | High | Medium | Variable | High |
| Explainability | High | Low | Low | Medium |
| Cost | Low | Medium | High | Medium |

*Comparison based on typical enterprise implementations.*
```

### Template 4: Results Table

```markdown
**Table 5.3: Multi-Intent Detection Validation Results**

| Test Query | Expected Agents | Detected Agents | Result |
|------------|----------------|-----------------|--------|
| "Show delays and forecast" | Delay, Forecast | Delay, Forecast | ✅ Pass |
| "Revenue and demand trends" | Analytics, Forecast | Analytics, Forecast | ✅ Pass |
| "Order status for customer X" | Data Query | Data Query | ✅ Pass |
| "Delays, revenue, forecast" | All 3 | All 3 | ✅ Pass |

*Success Rate: 98% (49/50 test cases passed)*
```

---

## ✅ Quality Checklist

After completing all steps, verify:

- [ ] Every figure has a number (Figure X.Y)
- [ ] Every table has a number (Table X.Y)
- [ ] Every figure has a descriptive title
- [ ] Every table has a descriptive title
- [ ] Every illustration has a caption/note
- [ ] All figures/tables are referenced in text
- [ ] List of Figures created and complete
- [ ] List of Tables created and complete
- [ ] Page numbers added to lists (after final formatting)
- [ ] Numbering is sequential within chapters
- [ ] No duplicate numbers

---

## 🎯 Priority Order

If you're short on time, do this order:

**Must Have (WILP Required):**
1. ✅ Number all existing diagrams/tables
2. ✅ Add formal titles
3. ✅ Create List of Figures
4. ✅ Create List of Tables

**Should Have:**
5. Add captions/descriptions
6. Reference all figures/tables in text

**Nice to Have:**
7. Add additional diagrams for clarity
8. Create charts for performance data
9. Add screenshots of UI

---

## 🔢 Example Progression

### Current State (Informal):
```markdown
The architecture uses four agents coordinated by an orchestrator.
The technology stack includes Python, LangChain, FAISS, and Gradio.
```

### After Adding Figure:
```markdown
**Figure 3.1: Multi-Agent System Architecture**

[Diagram showing orchestrator, 4 agents, analytics engine, RAG module]

*The architecture (Figure 3.1) comprises four specialized agents coordinated
by an orchestrator. Each agent interfaces with both the analytics engine
for quantitative analysis and the RAG module for contextual information.*

The technology stack (Table 3.3) includes Python, LangChain, FAISS, and Gradio.
```

### Fully Formatted:
```markdown
**Figure 3.1: Multi-Agent System Architecture**

[Diagram]

*This diagram illustrates the multi-agent system architecture showing the
orchestrator's role in routing queries to specialized agents. Bidirectional
arrows indicate data flow between agents and core modules.*

The architecture (Figure 3.1) comprises four specialized agents coordinated
by an orchestrator. Each agent interfaces with both the analytics engine
for quantitative analysis and the RAG module for contextual information.

**Table 3.3: Technology Stack Comparison**

| Component | Technology | Reason for Selection |
|-----------|-----------|---------------------|
| Backend | Python 3.9+ | Rich ML/AI libraries |
| AI Framework | LangChain | Multi-agent support |
| Vector DB | FAISS | Fast similarity search |
| UI | Gradio | Rapid prototyping |

The technology stack (Table 3.3) was selected based on maturity, performance,
and enterprise integration capabilities.
```

---

## 📊 Estimated Figures/Tables Needed

Based on typical dissertation structure:

**Chapter 2:** 1-2 figures, 1-2 tables
**Chapter 3:** 2-3 figures, 3-4 tables
**Chapter 4:** 3-5 figures, 2-3 tables
**Chapter 5:** 1-2 figures, 3-5 tables
**Chapter 6:** 2-3 figures, 3-4 tables
**Chapter 7:** 1-2 figures, 2-3 tables

**Total:** ~12-18 figures, ~15-22 tables

---

## 🚀 Quick Start

1. **Open your dissertation:** `docs/DISSERTATION_REPORT.md`

2. **Search for key terms:**
   - "diagram"
   - "architecture"
   - "table"
   - "comparison"
   - "results"
   - "metrics"

3. **Add numbers as you find them:**
   - First diagram in Chapter 3 = Figure 3.1
   - Second diagram in Chapter 3 = Figure 3.2
   - First table in Chapter 3 = Table 3.1

4. **Keep a running list** in a separate document

5. **Create List of Figures/Tables** at the end

---

**Time Investment:** 3-4 hours
**Result:** Full WILP compliance
**Impact:** Required for submission

**Start with Chapter 3** (has most visual elements) and work through sequentially!

Good luck! 🎓
