# Glossary Section - WILP Writing Guide

**Status:** ⚠️ **Not Yet Created**
**Priority:** Medium (Required for WILP compliance)
**Estimated Time:** 1-2 hours
**Chapter Number:** 11 (Final section of dissertation)

---

## 📋 WILP Requirements for Glossary

According to WILP guidelines, the Glossary should include:

### ✅ Required Elements:

1. **List of technical words and terms** used in the report
2. **Meaning/definition** of each word or term
3. **Page number(s)** where the term occurs in the text

**Purpose:** Help readers understand specialized terminology used throughout the dissertation

---

## 📊 Format and Structure

### Standard Glossary Format:

```markdown
## GLOSSARY

**[Term]** (Page X, Y, Z)
Definition or explanation of the term in clear, accessible language.

**[Next Term]** (Page X, Y)
Definition or explanation...
```

### Example Entry:

```markdown
**Agent Orchestrator** (Pages 20, 35, 44, 75)
A central coordination component that analyzes user queries, determines which
specialized agents should handle the request, routes queries to appropriate
agents, and synthesizes their responses into a coherent answer. The orchestrator
implements multi-intent detection to handle compound queries requiring multiple
agents.

**FAISS (Facebook AI Similarity Search)** (Pages 27, 50, 52, 66)
An open-source library developed by Facebook for efficient similarity search
and clustering of dense vectors. Used in this system for semantic search across
vectorized document embeddings to retrieve relevant context for queries.

**Hallucination** (Pages 14, 42, 70, 95)
In the context of large language models, the generation of plausible-sounding
but factually incorrect or unsupported information. The system uses grounding
techniques and RAG to minimize hallucination risk.
```

---

## 📝 Terms to Include in Your Glossary

Based on your dissertation, here are technical terms that should be defined:

### Core System Terms

**Agent**
A specialized software component designed to handle specific types of queries or tasks within the multi-agent system.

**Agent Orchestrator**
Central coordination component managing multi-agent query routing and response synthesis.

**Agentic Mode**
Operational mode using the multi-agent architecture for query processing.

**Analytics Engine**
Core component performing quantitative analysis on structured supply chain data using pandas and NumPy.

### AI/ML Terms

**Embeddings**
Dense vector representations of text that capture semantic meaning, enabling similarity comparisons.

**Enhanced Mode**
Operational mode using a single large language model for query processing with LangChain integration.

**FAISS (Facebook AI Similarity Search)**
Open-source library for efficient similarity search in vector spaces.

**Hallucination**
Generation of factually incorrect information by language models.

**Intent Detection**
Process of analyzing user queries to determine which agent(s) should respond.

**LangChain**
Framework for developing applications powered by language models, providing abstractions for chains, agents, and tools.

**Large Language Model (LLM)**
Neural network model trained on vast text corpora capable of understanding and generating natural language.

**Multi-Intent Query**
User query requiring responses from multiple specialized agents (e.g., "Show delays and forecast demand").

**Natural Language Processing (NLP)**
Field of artificial intelligence focused on enabling computers to understand, interpret, and generate human language.

**Prompt Engineering**
Technique of crafting input prompts to guide language model behavior and output quality.

**RAG (Retrieval-Augmented Generation)**
Technique combining information retrieval with text generation to ground responses in factual content.

**Semantic Search**
Search technique that understands query meaning rather than just keyword matching.

**Sentence Transformers**
Neural network architecture for generating semantically meaningful sentence embeddings.

**Vector Database**
Database optimized for storing and searching high-dimensional vector representations.

### Supply Chain Terms

**Delay Rate**
Percentage of orders delivered after the promised/expected delivery date.

**Demand Forecasting**
Statistical prediction of future product demand based on historical patterns.

**ERP (Enterprise Resource Planning)**
Integrated software systems managing core business processes across an organization.

**KPI (Key Performance Indicator)**
Measurable value indicating organizational performance against objectives.

**On-Time Delivery Rate**
Percentage of orders delivered on or before the promised delivery date.

**Order Fulfillment**
Complete process from receiving a customer order to delivering the product.

**SCM (Supply Chain Management)**
Management of goods and services flow from raw materials to final delivery.

**SKU (Stock Keeping Unit)**
Unique identifier for each distinct product and service that can be purchased.

**WMS (Warehouse Management System)**
Software application supporting day-to-day warehouse operations.

### Technical Implementation Terms

**API (Application Programming Interface)**
Set of protocols and tools for building software applications and enabling system integration.

**Feature Store**
Repository for storing and managing machine learning features with caching capabilities.

**Gradio**
Python library for building web-based user interfaces for machine learning models.

**JSON (JavaScript Object Notation)**
Lightweight data interchange format that is easy for humans to read and machines to parse.

**Pandas**
Python library providing data structures and analysis tools for tabular data manipulation.

**Query Decomposition**
Process of breaking compound queries into agent-specific sub-queries for targeted processing.

**REST API**
Architectural style for networked applications using standard HTTP methods.

**SQL (Structured Query Language)**
Standard language for managing and querying relational databases.

**Token**
In NLP, the basic unit of text (word, subword, or character) processed by language models.

**Vector Similarity**
Measure of how close two vector representations are in vector space, indicating semantic similarity.

### System-Specific Terms

**Cross-Agent Insights**
Synthesized recommendations generated by combining outputs from multiple specialized agents.

**Conjunction Detection**
Identification of connecting words ("and", "also", "plus") signaling multi-intent queries.

**Context Retrieval**
Process of fetching relevant organizational documents to augment query responses.

**Document Chunking**
Breaking documents into smaller segments for embedding and retrieval.

**Graceful Degradation**
System's ability to maintain basic functionality when advanced features are unavailable.

**Intent Scoring**
Numerical assessment of query relevance to each agent's specialty.

**Phrase-Based Detection**
Intent detection approach weighting multi-word patterns higher than individual keywords.

**Query Routing**
Directing user queries to appropriate agent(s) based on intent analysis.

---

## 📏 Complete Glossary Template

```markdown
## CHAPTER 11: GLOSSARY

This glossary defines technical terms, acronyms, and specialized terminology
used throughout this dissertation. Page numbers indicate where each term appears
in the text.

---

**Agent** (Pages 19, 20, 34-42, 75, 89)
A specialized software component designed to handle specific types of queries
or tasks within the multi-agent system. This dissertation implements four
agents: Delay Agent (delivery performance), Analytics Agent (business metrics),
Forecasting Agent (demand prediction), and Data Query Agent (data retrieval).

**Agent Orchestrator** (Pages 20, 35, 44-47, 75, 90)
Central coordination component that analyzes user queries, determines which
specialized agents should handle the request, routes queries to appropriate
agents in optimal sequence, and synthesizes their responses. Implements
multi-intent detection for compound queries.

**Agentic Mode** (Pages 16, 19, 56, 72)
Operational mode utilizing the multi-agent architecture where queries are
automatically routed to specialized agents based on intent analysis.

**Analytics Engine** (Pages 28, 30, 34, 68)
Core component performing quantitative analysis on structured supply chain
data using pandas and NumPy libraries for aggregations, filtering, and
statistical computations.

**API (Application Programming Interface)** (Pages 22, 30, 54, 82)
Set of protocols and tools enabling different software applications to
communicate and integrate with each other.

**Compound Query** (Pages 3, 44, 64, 75, 92)
User question spanning multiple analytical domains requiring coordination
of multiple agents (e.g., "Show delays and forecast demand").

**Conjunction Detection** (Pages 45, 65, 93)
Automated identification of connecting words ("and", "also", "plus", "with")
indicating multi-intent queries requiring multiple agents.

**Context Retrieval** (Pages 26, 52, 66, 78)
Process of fetching relevant organizational documents from the vector database
to augment query responses with contextual information.

**Cross-Agent Insights** (Pages 46, 76, 94, 99)
Synthesized recommendations generated by analyzing outputs from multiple
specialized agents to provide holistic perspectives spanning domains.

**Delay Rate** (Pages 2, 34, 60, 73, 87)
Percentage of orders delivered after the promised or expected delivery date,
calculated as (delayed orders / total orders) × 100.

**Document Chunking** (Pages 48, 50)
Process of dividing large documents into smaller segments (typically 500-1000
characters) for embedding generation and efficient retrieval.

**Embeddings** (Pages 26, 50, 51, 66)
Dense vector representations of text (typically 384 or 768 dimensions) that
capture semantic meaning, enabling similarity-based retrieval.

**Enhanced Mode** (Pages 16, 19, 56, 72)
Operational mode using a single large language model with LangChain integration
for query processing, without multi-agent specialization.

**Enterprise Resource Planning (ERP)** (Pages 2, 17, 30, 80, 83)
Integrated software systems managing core business processes including inventory,
procurement, finance, and logistics across an organization.

**FAISS (Facebook AI Similarity Search)** (Pages 27, 50, 52, 66)
Open-source library for efficient similarity search and clustering of dense
vectors, used for semantic search across document embeddings.

**Feature Store** (Pages 32, 54, 68)
Repository for storing and managing pre-computed analytical features with
caching capabilities to improve query performance.

**Forecasting Agent** (Pages 20, 40-42, 75, 88)
Specialized agent responsible for demand prediction, trend analysis, and
statistical forecasting using historical supply chain data.

**Graceful Degradation** (Pages 18, 42, 71, 85)
System design principle ensuring basic functionality continues when advanced
features (like external LLM APIs or RAG) are unavailable.

**Gradio** (Pages 22, 56, 58)
Python library for rapidly building web-based user interfaces for machine
learning models and data science applications.

**Hallucination** (Pages 14, 42, 70, 95)
In large language models, the generation of plausible-sounding but factually
incorrect or unsupported information. Mitigated through grounding and RAG.

**Intent Detection** (Pages 44-45, 64-65, 90)
Automated analysis of user queries to determine which specialized agent(s)
should handle the request based on keyword and phrase matching.

**Intent Scoring** (Pages 44, 65)
Numerical assessment (0-10 scale) of query relevance to each agent's domain
expertise, used for routing decisions.

**Key Performance Indicator (KPI)** (Pages 2, 17, 73)
Measurable value indicating how effectively an organization achieves business
objectives.

**LangChain** (Pages 22, 38, 42, 54, 86)
Framework for developing applications powered by language models, providing
abstractions for chains, agents, tools, and prompts.

**Large Language Model (LLM)** (Pages 3, 14-15, 38, 42, 70, 95)
Neural network model trained on vast text corpora (billions of parameters)
capable of understanding and generating natural language.

**Multi-Agent System** (Pages 3, 10-11, 19-20, 34-47, 89-94)
Architecture employing multiple specialized software agents that coordinate
to solve complex problems requiring diverse expertise.

**Multi-Intent Query** (Pages 3, 44-47, 64-65, 75-76, 92-94)
User question requiring responses from multiple specialized agents, detected
through conjunction analysis and intent scoring.

**Natural Language Processing (NLP)** (Pages 8, 12-13, 44, 90)
Field of artificial intelligence focused on enabling computers to understand,
interpret, and generate human language.

**On-Time Delivery Rate** (Pages 34, 60, 73, 87)
Percentage of orders delivered on or before the promised delivery date,
calculated as (on-time orders / total orders) × 100.

**Orchestrator** (See **Agent Orchestrator**)

**Pandas** (Pages 22, 28, 30, 68)
Python library providing DataFrame data structures and analysis tools for
efficient manipulation of tabular data.

**Phrase-Based Detection** (Pages 45, 65, 93)
Intent detection approach that weights multi-word patterns (e.g., "delivery
delay") twice as heavily as individual keywords for improved accuracy.

**Prompt Engineering** (Pages 38, 42, 86)
Technique of designing and optimizing input prompts to guide language model
behavior, output format, and response quality.

**Query Decomposition** (Pages 46, 76, 94)
Process of breaking compound queries into agent-specific sub-queries, enabling
targeted processing by specialized agents.

**Query Routing** (Pages 44, 65, 90)
Directing user queries to appropriate specialized agent(s) based on intent
analysis and domain relevance scoring.

**RAG (Retrieval-Augmented Generation)** (Pages 3, 12-13, 26-27, 48-53, 66-67, 78)
Technique combining information retrieval (semantic search) with text generation
to ground LLM responses in factual, organizational content.

**Semantic Search** (Pages 26, 50, 52, 66, 78)
Search technique that understands query meaning and intent rather than relying
solely on exact keyword matching, using vector similarity.

**Sentence Transformers** (Pages 27, 50, 66)
Neural network architecture optimized for generating semantically meaningful
embeddings for sentences and short text passages.

**Supply Chain Management (SCM)** (Pages 1-2, 6-8, 17, 89)
Oversight of materials, information, and finances as they move from supplier
to manufacturer to wholesaler to retailer to consumer.

**Token** (Pages 38, 68, 86)
Basic unit of text processed by language models, typically representing words,
subwords, or characters. LLM costs and context limits measured in tokens.

**Vector Database** (Pages 26-27, 50-52, 66)
Database system optimized for storing and searching high-dimensional vector
representations, enabling efficient similarity searches.

**Vector Similarity** (Pages 51, 66)
Measure (typically cosine similarity) of how close two vector representations
are in high-dimensional space, indicating semantic relatedness.

**Warehouse Management System (WMS)** (Pages 2, 30, 80, 83)
Software application designed to support and optimize warehouse operations
including inventory tracking, picking, packing, and shipping.

---

**Note:** Page numbers will be finalized after document layout and formatting
are complete. Update all page references before final submission.
```

---

## ✅ Glossary Creation Checklist

### Step 1: Identify Terms (30 minutes)
- [ ] Go through entire dissertation
- [ ] Mark all technical terms, acronyms, specialized words
- [ ] Note page numbers where each term appears
- [ ] Group similar terms together

### Step 2: Write Definitions (1 hour)
- [ ] Define each term clearly
- [ ] Use accessible language
- [ ] Explain in context of your work
- [ ] Keep definitions concise (2-4 sentences)

### Step 3: Add Page Numbers (15 minutes)
- [ ] List all pages where term appears
- [ ] Use format: (Pages X, Y, Z) or (Page X)
- [ ] Update after final pagination

### Step 4: Organize Alphabetically (15 minutes)
- [ ] Sort all entries A-Z
- [ ] Double-check alphabetical order
- [ ] Ensure consistent formatting

### Step 5: Quality Check (15 minutes)
- [ ] All acronyms defined
- [ ] All technical terms included
- [ ] Definitions clear and accurate
- [ ] Page numbers correct
- [ ] Formatting consistent

---

## 💡 Tips for Writing Good Definitions

### DO:
✅ Use clear, accessible language
✅ Define in context of your dissertation
✅ Explain what it does, not just what it is
✅ Keep concise (2-4 sentences)
✅ Include all variants of a term together

### DON'T:
❌ Use overly technical language in definitions
❌ Assume reader knows related concepts
❌ Make definitions too long (save details for main text)
❌ Forget to include page numbers
❌ Define common words (only specialized terms)

---

## 📊 Example: Good vs. Poor Definitions

### Poor Definition:
**RAG**
Retrieval-Augmented Generation.

### Good Definition:
**RAG (Retrieval-Augmented Generation)** (Pages 3, 12-13, 26-27, 48-53, 66-67, 78)
Technique that enhances large language model responses by first retrieving
relevant information from a knowledge base (documents, databases), then using
that retrieved content to ground the generated response in factual information.
Reduces hallucination risk by connecting LLM outputs to verifiable sources.

---

### Poor Definition:
**Agent**
Software component.

### Good Definition:
**Agent** (Pages 19, 20, 34-42, 75, 89)
A specialized software component designed to handle specific types of queries
or tasks within the multi-agent system. This dissertation implements four
agents: Delay Agent (delivery performance), Analytics Agent (business metrics),
Forecasting Agent (demand prediction), and Data Query Agent (data retrieval).
Each agent possesses domain-specific knowledge and analytical capabilities.

---

## 📏 Estimated Content

**Number of Terms:** 40-60 (based on typical technical dissertation)
**Length:** 4-6 pages
**Format:** Alphabetical list with definitions and page numbers

---

## 🎯 Priority Level

**WILP Requirement:** Mandatory
**Current Status:** Not created
**Time Required:** 1-2 hours
**Difficulty:** Easy (straightforward listing and definition task)
**Priority:** Medium (required but can be done near end)

**Best Time to Create:** After all chapters are written and before final formatting, so page numbers are accurate.

---

## 📝 Quick Creation Process

### Fastest Approach (1 hour):

1. **Extract acronyms from abbreviations list** (5 min)
   - You already have List of Abbreviations
   - Use those as starting point

2. **Identify technical terms** (15 min)
   - Skim through each chapter
   - Mark specialized SCM, AI/ML, technical terms
   - Note page numbers

3. **Write definitions** (30 min)
   - Use template format
   - Keep definitions 2-4 sentences
   - Explain in dissertation context

4. **Alphabetize and format** (10 min)
   - Sort A-Z
   - Ensure consistent format
   - Verify all have page numbers

---

## 📚 Resources to Help

### Already Created:
- **List of Abbreviations** - Use as foundation
- **Chapter 1-3** - Source of technical terms
- **Your code documentation** - Technical definitions

### Reference Example:
See complete template glossary above with 40+ terms already defined for your dissertation.

---

**Status:** Not yet created, but straightforward task
**When to Do:** After Chapters 4-8 are written (so page numbers are known)
**Time:** 1-2 hours
**Impact:** Required for WILP compliance

You can create this toward the end of your dissertation writing process! 📚
