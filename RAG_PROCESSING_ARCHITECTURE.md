# RAG Processing Architecture

**Complete Guide to RAG in the SCM Chatbot**
**Date**: February 7, 2026

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Document Ingestion Pipeline](#document-ingestion-pipeline)
3. [Vector Database Architecture](#vector-database-architecture)
4. [Query Processing & Retrieval](#query-processing--retrieval)
5. [Agent Integration](#agent-integration)
6. [Complete Flow Diagram](#complete-flow-diagram)
7. [Code References](#code-references)

---

## Overview

The RAG (Retrieval-Augmented Generation) system enables the chatbot to answer questions using **policy documents** (PDFs) rather than just database statistics.

### Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PDFs → Text Extraction → Chunking → Embeddings → Index     │
│                                                               │
│  Query → Embedding → Vector Search → Context → Agent → LLM  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **PDF Extraction**: PyPDF2 / pdfplumber
- **Chunking**: Semantic paragraph-aware (500 words, 100-word overlap)

---

## Document Ingestion Pipeline

### Phase 1: PDF Upload & Text Extraction

**File**: `modules/document_manager.py`

```python
def upload_document(self, file_path: str, file_content: bytes):
    """
    1. User uploads PDF through UI or API
    2. File is saved to data/business_docs/
    3. Text is extracted from PDF
    """

    # Extract text using multiple strategies
    text_content = self._extract_text(saved_path, file_ext)

    # Strategies (in order):
    # 1. pdfplumber (best quality)
    # 2. PyPDF2 (fallback)
    # 3. pypdf (alternative)
    # 4. Document name (last resort)
```

**Example**:
```
Input:  01_Product_Delay_Management_Policy.pdf (8 KB)
Output: 5,009 characters of text
        "Product Delay Management Policy
         Document ID: SCM-POL-001
         ...
         2.1 Severity Levels
         • Critical Delay: >5 business days..."
```

---

### Phase 2: Document Chunking

**File**: `rag.py` → `DocumentProcessor.chunk_text()`

```python
def chunk_text(self, text: str, chunk_size: int = 500,
               chunk_overlap: int = 100) -> List[str]:
    """
    Semantic paragraph-aware chunking

    Strategy:
    1. Split by paragraphs (double newline)
    2. Group paragraphs into ~500 word chunks
    3. Overlap 100 words between chunks
    4. Preserve semantic boundaries
    """

    # Split into paragraphs
    paragraphs = re.split(r'\n\s*\n', text)

    # Group into chunks with overlap
    chunks = []
    current_chunk_words = []

    for paragraph in paragraphs:
        words = paragraph.split()
        current_chunk_words.extend(words)

        if len(current_chunk_words) >= chunk_size:
            # Create chunk
            chunk = ' '.join(current_chunk_words[:chunk_size])
            chunks.append(chunk)

            # Keep last 100 words for overlap
            current_chunk_words = current_chunk_words[-chunk_overlap:]

    return chunks
```

**Example**:
```
Input:  5,009 chars from policy PDF
Output: 2 chunks

Chunk 0 (500 words):
  "Product Delay Management Policy ... 2.1 Severity Levels
   • Critical Delay: >5 business days ... [continues]"

Chunk 1 (450 words, overlaps with chunk 0):
  "... [overlap from previous] ... 7. Performance Metrics
   7.1 Key Performance Indicators ..."
```

---

### Phase 3: Vectorization & Indexing

**File**: `rag.py` → `VectorDatabase.build_index()`

```python
def build_index(self, documents: List[Dict]):
    """
    Convert text chunks to vectors and build FAISS index

    Process:
    1. Generate embeddings for all chunks
    2. Create FAISS index
    3. Add vectors to index
    4. Save to disk
    """

    # Generate embeddings
    texts = [doc['text'] for doc in documents]
    embeddings = self.embedding_model.encode(texts)
    # Output shape: (38, 384) = 38 chunks, 384-dimensional vectors

    # Build FAISS index
    self.index = faiss.IndexFlatL2(384)  # L2 distance
    self.index.add(embeddings.astype('float32'))

    # Save to disk
    faiss.write_index(self.index, "data/vector_index/index.faiss")
    pickle.dump(documents, open("data/vector_index/documents.pkl", 'wb'))
```

**Example**:
```
Input:  38 text chunks from 7 PDFs

Processing:
  - Chunk 0: "Product Delay Management..." → [0.234, -0.123, 0.456, ...]
  - Chunk 1: "... Performance Metrics..." → [0.123, -0.234, 0.789, ...]
  - ...
  - Chunk 37: "... Forecasting Policy..." → [-0.456, 0.234, -0.123, ...]

Output: data/vector_index/
        ├── index.faiss       (FAISS index with vectors)
        ├── documents.pkl     (Original text chunks)
        └── embeddings.npy    (Numpy array of embeddings)
```

---

## Vector Database Architecture

**File**: `rag.py` → `VectorDatabase` class

### Data Structure

```python
class VectorDatabase:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None              # FAISS index
        self.documents = []            # List of document chunks
        self.doc_embeddings = None     # Numpy array of embeddings
```

### Storage Format

**Document Chunk**:
```python
{
    'id': '3ef883cc_chunk_0',
    'text': 'Product Delay Management Policy...',
    'type': 'business_document',
    'metadata': {
        'doc_id': '3ef883cc',
        'doc_name': '01_Product_Delay_Management_Policy.pdf',
        'doc_type': 'Policy',
        'chunk_index': 0,
        'total_chunks': 2,
        'source': 'uploaded_document'
    }
}
```

### FAISS Index

- **Type**: `IndexFlatL2` (L2/Euclidean distance)
- **Dimension**: 384
- **Metric**: Smaller distance = higher similarity
- **Speed**: ~1ms for search over 38 vectors

---

## Query Processing & Retrieval

### Step 1: Query Embedding

**File**: `rag.py` → `VectorDatabase.search()`

```python
def search(self, query: str, top_k: int = 5):
    """
    Convert query to vector and find similar documents
    """

    # 1. Embed the query
    query_embedding = self.embedding_model.encode([query])
    # Shape: (1, 384)

    # 2. Search FAISS index
    distances, indices = self.index.search(
        query_embedding.astype('float32'),
        top_k
    )
    # distances: [0.234, 0.456, 0.789, 1.234, 1.567]
    # indices:   [19, 23, 27, 31, 37]

    # 3. Retrieve documents
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        results.append((self.documents[idx], float(distance)))

    return results
```

**Example**:
```python
Query: "What are severity levels?"

# 1. Embed query
query_vector = [0.234, -0.123, 0.456, ...]  # 384 dimensions

# 2. Find nearest neighbors in FAISS
Top 5 matches:
  - Chunk 19 (distance: 0.689) → "Product Delay ... Severity Levels..."
  - Chunk 23 (distance: 0.934) → "... Communication Protocol..."
  - Chunk 27 (distance: 0.987) → "... Escalation Process..."
  - ...

# 3. Return documents with distances
Results: [(doc_19, 0.689), (doc_23, 0.934), ...]
```

---

### Step 2: Query Expansion

**File**: `rag.py` → `RAGModule._expand_query()`

```python
def _expand_query(self, query: str) -> List[str]:
    """
    Generate alternative phrasings for better retrieval
    """

    query_lower = query.lower()
    expansions = [query]

    # Synonym expansion
    if 'delay' in query_lower:
        expansions.append(query.replace('delay', 'late delivery'))

    if 'severity' in query_lower:
        expansions.extend([
            query.replace('severity', 'classification'),
            query.replace('severity levels', 'delay categories')
        ])

    return expansions[:3]  # Limit to top 3
```

**Example**:
```
Original: "What are severity levels?"

Expanded:
  1. "What are severity levels?"
  2. "What are classification levels?"
  3. "What are delay categories?"

All 3 queries are searched, best matches aggregated
```

---

### Step 3: Context Retrieval & Filtering

**File**: `rag.py` → `RAGModule.retrieve_context()`

```python
def retrieve_context(self, query: str) -> str:
    """
    Complete retrieval pipeline with filtering
    """

    # 1. Expand query
    queries = self._expand_query(query)

    # 2. Search with all variants
    all_results = {}
    for q in queries:
        results = self.vector_db.search(q, top_k=5)
        for doc, score in results:
            doc_id = doc['id']
            # Keep best score for each doc
            if doc_id not in all_results or score < all_results[doc_id][1]:
                all_results[doc_id] = (doc, score)

    # 3. Sort by score (lower = better)
    results = sorted(all_results.values(), key=lambda x: x[1])[:5]

    # 4. Filter by threshold
    filtered = [(doc, score) for doc, score in results
                if score < 2.0]  # similarity_threshold

    # 5. Format context
    context_parts = []
    for doc, score in filtered:
        similarity = 1 / (1 + score)  # Convert distance to similarity
        context_parts.append(f"[Relevance: {similarity:.2f}]\n{doc['text']}\n")

    return "\n---\n".join(context_parts)
```

**Example Output**:
```
[Relevance: 0.59]
Product Delay Management Policy Document ID: SCM-POL-001 ...
2.1 Severity Levels
• Critical Delay: >5 business days beyond committed delivery date
• Major Delay: 3-5 business days beyond committed delivery date
• Minor Delay: 1-2 business days beyond committed delivery date
...

---
[Relevance: 0.52]
... Escalation Process
4.1 Tier 1 Response (0-24 hours)
Delay Severity | B2B Customers | B2C Customers
Critical       | 4 hours       | 8 hours
...
```

---

## Agent Integration

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  AGENT QUERY FLOW                         │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  User Query → Orchestrator → Agent Selection              │
│                   ↓                                        │
│              Selected Agent                                │
│                   ↓                                        │
│         ┌─────────┴─────────┐                            │
│         │                   │                             │
│    Is Policy Q?        Is Data Q?                         │
│         │                   │                             │
│    ┌────┴────┐         Database                          │
│    │         │         Query                              │
│   RAG    No RAG                                           │
│  Module   Available                                       │
│    │         │                                             │
│  Policy   Database                                        │
│  Docs     Stats                                           │
│    │         │                                             │
│    └────┬────┘                                            │
│         │                                                  │
│    Format Response                                        │
│         │                                                  │
│    Return to User                                         │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

### Agent RAG Integration Pattern

**Files**: `agents/delay_agent.py`, `agents/analytics_agent.py`, `agents/forecasting_agent.py`

```python
class DelayAgent:
    def __init__(self, analytics_engine, rag_module=None):
        self.analytics = analytics_engine
        self.rag_module = rag_module

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Process query with RAG prioritization
        """

        # STEP 1: Try RAG retrieval
        rag_context = None
        used_rag = False

        if self.rag_module:
            try:
                rag_context = self.rag_module.retrieve_context(user_query)
                if rag_context and len(rag_context.strip()) > 0:
                    used_rag = True
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        # STEP 2: Detect query type
        query_lower = user_query.lower()

        policy_keywords = [
            'severity', 'level', 'classification', 'policy',
            'procedure', 'definition', 'what is', 'what are'
        ]

        is_policy_question = any(
            keyword in query_lower
            for keyword in policy_keywords
        )

        # STEP 3: Route based on type
        if is_policy_question and used_rag:
            # PRIORITY 1: Use RAG for policy questions
            response = f"**Based on policy documents:**\n\n{rag_context[:1500]}"

            return {
                'response': response,
                'agent': 'Delay Agent + RAG',
                'used_rag': True
            }

        elif 'statistics' in query_lower or 'rate' in query_lower:
            # PRIORITY 2: Use database for data questions
            stats = self.analytics.analyze_delivery_delays()
            response = self._format_statistics(stats)

            return {
                'response': response,
                'agent': 'Delay Agent',
                'used_rag': False
            }

        else:
            # Default behavior
            response = self._handle_query(user_query)
            return {'response': response}
```

---

### LangChain Agent Integration

**File**: `agents/delay_agent.py` → `_initialize_langchain_agent()`

```python
def _initialize_langchain_agent(self):
    """
    Initialize LangChain agent with RAG awareness
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a specialized Delivery Delay Analysis Agent.

CRITICAL: Determine if the user is asking about:
1. **POLICY/PROCEDURES** (severity levels, definitions, guidelines)
   → If the input contains "Context from documents:", USE THAT CONTEXT
   → DO NOT query database tools for policy questions

2. **DATA/STATISTICS** (actual delays, counts, rates)
   → Use the available tools to query real operational data

When you see "Context from documents:" in the input, that is RAG-retrieved
policy information. Use it directly to answer the question."""),
        ("human", "{input}"),
    ])

    # When query comes in:
    if used_rag:
        # Augment query with RAG context
        augmented_query = f"""Context from documents:
{rag_context}

User query: {user_query}"""

        response = self.agent_executor.invoke({"input": augmented_query})
    else:
        response = self.agent_executor.invoke({"input": user_query})
```

---

## Complete Flow Diagram

### End-to-End Query Processing

```
USER QUERY: "What are severity levels?"
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. ORCHESTRATOR (main.py)                               │
│    - Receives query                                      │
│    - Analyzes intent                                     │
│    - Routes to Delay Agent                               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 2. DELAY AGENT (agents/delay_agent.py)                  │
│    - Receives query                                      │
│    - Checks if RAG module available                      │
│    - Calls RAG retrieval                                 │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 3. RAG MODULE (rag.py)                                  │
│    a. Query Expansion:                                   │
│       - "What are severity levels?"                      │
│       - "What are classification levels?"                │
│       - "What are delay categories?"                     │
│                                                           │
│    b. Vector Search:                                     │
│       - Embed queries → [0.234, -0.123, ...]           │
│       - Search FAISS index                               │
│       - Find top-k nearest vectors                       │
│                                                           │
│    c. Document Retrieval:                                │
│       - Get chunks: [19, 23, 27, 31, 37]               │
│       - Calculate similarity scores                      │
│       - Filter by threshold (2.0)                        │
│                                                           │
│    d. Context Formatting:                                │
│       - Format with relevance scores                     │
│       - Return formatted context                         │
└────────────────────┬────────────────────────────────────┘
                     ↓
              RAG Context
┌─────────────────────────────────────────────────────────┐
│ [Relevance: 0.59]                                        │
│ Product Delay Management Policy                          │
│ 2.1 Severity Levels                                      │
│ • Critical Delay: >5 business days                       │
│ • Major Delay: 3-5 business days                         │
│ • Minor Delay: 1-2 business days                         │
│ ...                                                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 4. DELAY AGENT (continued)                               │
│    - Detects policy keywords: "severity", "levels"       │
│    - RAG context available: YES                          │
│    - Decision: Use RAG (not database)                    │
│    - Format response with context                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 5. ORCHESTRATOR (main.py)                               │
│    - Receives agent response                             │
│    - Adds agent info                                     │
│    - Adds metrics                                        │
│    - Returns to UI                                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
              FINAL OUTPUT
┌─────────────────────────────────────────────────────────┐
│ Based on policy documents:                               │
│                                                           │
│ [Relevance: 0.59]                                        │
│ Product Delay Management Policy                          │
│                                                           │
│ 2.1 Severity Levels                                      │
│ • Critical Delay: >5 business days beyond committed      │
│   delivery date                                           │
│ • Major Delay: 3-5 business days beyond committed        │
│   delivery date                                           │
│ • Minor Delay: 1-2 business days beyond committed        │
│   delivery date                                           │
│ • At-Risk: Products showing indicators of potential      │
│   delay                                                   │
│                                                           │
│ ────────────────────────────────────────────────────────│
│ 🤖 Agent: Delay Agent | 📚 RAG | ✅ Success             │
│ ⏱️ 562ms | 📊📚                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Code References

### Core RAG Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| **[rag.py](rag.py)** | Main RAG implementation | `VectorDatabase`, `RAGModule`, `DocumentProcessor` |
| **[modules/document_manager.py](modules/document_manager.py)** | PDF upload & management | `upload_document()`, `_extract_text()` |
| **[vectorize_documents.py](vectorize_documents.py)** | Batch document vectorization | `vectorize_uploaded_documents()` |
| **[rebuild_index.py](rebuild_index.py)** | Force index rebuild | Main rebuild script |

### Agent Integration Files

| File | RAG Integration | Policy Detection |
|------|----------------|------------------|
| **[agents/delay_agent.py](agents/delay_agent.py)** | ✅ Full | ✅ Implemented |
| **[agents/analytics_agent.py](agents/analytics_agent.py)** | ✅ Full | ✅ Implemented |
| **[agents/forecasting_agent.py](agents/forecasting_agent.py)** | ✅ Full | ✅ Implemented |
| **[agents/data_query_agent.py](agents/data_query_agent.py)** | ⚠️ Basic | ❌ Not implemented |

### Application Entry Point

| File | Purpose | RAG Loading |
|------|---------|-------------|
| **[main.py](main.py:287-331)** | Application initialization | Loads pre-built index from `data/vector_index` |

---

## Key Configuration Parameters

### Document Processing
```python
chunk_size = 500          # Words per chunk
chunk_overlap = 100       # Overlap between chunks
```

### Vector Search
```python
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
dimension = 384           # Embedding dimension
top_k = 5                 # Number of results
similarity_threshold = 2.0  # Distance threshold (lower = stricter)
```

### Distance to Similarity Conversion
```python
similarity = 1 / (1 + distance)

Examples:
  distance=0.689 → similarity=0.59 (59%)
  distance=0.934 → similarity=0.52 (52%)
  distance=1.500 → similarity=0.40 (40%)
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Index Size** | 38 chunks (7 PDFs) |
| **Index Build Time** | ~10 seconds |
| **Query Latency** | 1-5ms (vector search only) |
| **End-to-End Latency** | 300-600ms (with LLM) |
| **Embedding Time** | ~50ms per query |
| **Memory Usage** | ~100MB (loaded index) |

---

## Troubleshooting

### Issue: Wrong documents retrieved
**Solution**: Rebuild index with better chunking
```bash
python rebuild_index.py
```

### Issue: No RAG context
**Check**:
1. Vector index exists: `data/vector_index/index.faiss`
2. Application loaded index: Check startup logs
3. Documents vectorized: Check `documents_metadata.json`

### Issue: Order data instead of policies
**Cause**: Application building index from CSV instead of loading PDFs
**Solution**: Check `main.py` loads from `data/vector_index`

---

## Summary

The RAG system processes queries through a **6-step pipeline**:

1. **Document Ingestion**: PDFs → Text extraction
2. **Chunking**: Semantic splitting with overlap
3. **Vectorization**: Text → 384-dim embeddings
4. **Indexing**: FAISS index creation
5. **Query Processing**: Query → Vector search → Context retrieval
6. **Agent Integration**: Policy detection → RAG or Database

**Key Insight**: The system intelligently routes queries:
- **Policy questions** → RAG retrieves from PDF documents
- **Data questions** → Database queries return statistics

This dual-mode approach ensures accurate, contextually appropriate responses.

---

**Documentation Complete** | Last Updated: February 7, 2026
