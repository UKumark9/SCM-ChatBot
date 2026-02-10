# enhanced_rag.py - Enhanced RAG Implementation

## Purpose
Enhanced version of RAG module with improved retrieval strategies, re-ranking, and advanced document processing capabilities.

## Key Components

### Class: EnhancedRAG
Advanced RAG implementation with multiple retrieval strategies.

**Initialization Parameters:**
- `index_path` (str): Path to vector index
- `documents_path` (str): Path to documents
- `metadata_path` (str): Path to metadata
- `model_name` (str): Embedding model name
- `use_reranking` (bool): Enable re-ranking (default: False)

## Core Methods

### `retrieve_context(query, top_k=3, strategy='hybrid')`
Retrieves context using enhanced retrieval strategies.

**Parameters:**
- `query` (str): User's question
- `top_k` (int): Number of documents to retrieve
- `strategy` (str): Retrieval strategy

**Strategies:**
- `'semantic'`: Pure vector similarity (default in rag.py)
- `'keyword'`: BM25 keyword search
- `'hybrid'`: Combines semantic + keyword
- `'mmr'`: Maximal Marginal Relevance (diversity)

**Returns:** str (formatted context)

### `rerank_results(query, results, top_k=3)`
Re-ranks retrieved results for better relevance.

**Parameters:**
- `query` (str): User's question
- `results` (list): Initial retrieval results
- `top_k` (int): Number to return after re-ranking

**Returns:** list (re-ranked results)

**Re-ranking Methods:**
- Cross-encoder models
- Query-document similarity
- Diversity scoring

### `retrieve_with_mmr(query, top_k=3, lambda_param=0.5)`
Maximal Marginal Relevance retrieval for diversity.

**Parameters:**
- `query` (str): User's question
- `top_k` (int): Number of documents
- `lambda_param` (float): Relevance vs diversity balance (0-1)

**Returns:** list (diverse results)

**Balance:**
- lambda=1.0: Pure relevance (like standard retrieval)
- lambda=0.5: Balanced relevance and diversity
- lambda=0.0: Pure diversity (not recommended)

### `retrieve_with_feedback(query, feedback, top_k=3)`
Retrieval with relevance feedback.

**Parameters:**
- `query` (str): User's question
- `feedback` (dict): User feedback on previous results
- `top_k` (int): Number of documents

**Returns:** list (refined results)

**Feedback Format:**
```python
{
    'relevant_docs': [doc_id1, doc_id2],
    'irrelevant_docs': [doc_id3]
}
```

## Advanced Features

### Hybrid Search
Combines semantic and keyword search:
```python
rag = EnhancedRAG(index_path, use_reranking=True)
context = rag.retrieve_context(
    "What is delay policy?",
    strategy='hybrid'
)
# Uses both vector similarity and BM25
```

### MMR for Diversity
Reduces redundancy in results:
```python
context = rag.retrieve_with_mmr(
    "What are delay categories?",
    top_k=5,
    lambda_param=0.5
)
# Returns diverse, non-redundant documents
```

### Re-ranking
Improves relevance:
```python
rag = EnhancedRAG(index_path, use_reranking=True)
context = rag.retrieve_context("policy question")
# Initial retrieval → Re-ranking → Top results
```

## Configuration

### Enable Re-ranking
```python
rag = EnhancedRAG(
    index_path="data/vector_index/",
    use_reranking=True  # Enable cross-encoder re-ranking
)
```

### Hybrid Search Weights
```python
# Adjust in retrieve_context method
semantic_weight = 0.7  # Vector similarity
keyword_weight = 0.3   # BM25 score
```

### MMR Parameters
```python
# Balance relevance vs diversity
lambda_param = 0.5  # 50% relevance, 50% diversity
```

## Performance Characteristics

### Standard Retrieval
- **Time**: ~15-20ms
- **Strategy**: Pure vector similarity
- **Quality**: Good for semantic queries

### Hybrid Search
- **Time**: ~30-40ms
- **Strategy**: Vector + keyword
- **Quality**: Better for mixed queries

### With Re-ranking
- **Time**: ~100-150ms
- **Strategy**: Initial retrieval + re-ranking
- **Quality**: Best relevance

### MMR
- **Time**: ~40-60ms
- **Strategy**: Iterative selection for diversity
- **Quality**: Best for comprehensive coverage

## Dependencies

### Required Libraries
```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from rank_bm25 import BM25Okapi  # For keyword search
```

### Optional Libraries
```python
from sentence_transformers import CrossEncoder  # For re-ranking
```

## Use Cases

### When to Use EnhancedRAG

1. **Hybrid Search**: Queries with both semantic and keyword components
2. **Diversity Needed**: Want non-redundant documents
3. **High Precision Required**: Re-ranking for best relevance
4. **Complex Queries**: Multi-faceted questions

### When Standard RAG is Sufficient

1. **Simple Queries**: Straightforward semantic search
2. **Speed Priority**: Need fastest retrieval
3. **Small Document Set**: Less than 100 documents
4. **Clear Query Intent**: Well-defined questions

## Comparison: Standard vs Enhanced RAG

| Feature | Standard RAG | Enhanced RAG |
|---------|--------------|--------------|
| Retrieval Strategy | Vector similarity only | Multiple strategies |
| Speed | Fast (~15ms) | Slower (~100ms with re-rank) |
| Relevance | Good | Excellent |
| Diversity | No | Yes (MMR) |
| Keyword Support | No | Yes (hybrid) |
| Re-ranking | No | Optional |
| Complexity | Simple | Advanced |
| Best For | Most queries | Complex/critical queries |

## Integration Points

### Could Replace
- `rag.py`: Can be used as drop-in replacement

### Requires
- FAISS index (same as standard RAG)
- Sentence transformers
- Optional: BM25, CrossEncoder

## Migration from Standard RAG

### Step 1: Install Dependencies
```bash
pip install rank-bm25
pip install sentence-transformers
```

### Step 2: Update Initialization
```python
# Old
from rag import RAGModule
rag = RAGModule(index_path)

# New
from enhanced_rag import EnhancedRAG
rag = EnhancedRAG(index_path, use_reranking=True)
```

### Step 3: Update Retrieval Calls
```python
# Old
context = rag.retrieve_context(query, top_k=3)

# New (hybrid)
context = rag.retrieve_context(query, top_k=3, strategy='hybrid')

# Or MMR
context = rag.retrieve_with_mmr(query, top_k=3, lambda_param=0.5)
```

## Performance Tuning

### For Speed
```python
# Disable re-ranking
rag = EnhancedRAG(index_path, use_reranking=False)

# Use semantic only
context = rag.retrieve_context(query, strategy='semantic')
```

### For Quality
```python
# Enable re-ranking
rag = EnhancedRAG(index_path, use_reranking=True)

# Use hybrid search
context = rag.retrieve_context(query, strategy='hybrid')
```

### For Diversity
```python
# Use MMR
context = rag.retrieve_with_mmr(
    query,
    top_k=5,
    lambda_param=0.3  # More diversity
)
```

## Note

This module provides advanced RAG capabilities but may not be currently integrated into the main application. The standard `rag.py` module is used in production for its simplicity and speed. Consider using EnhancedRAG for specific use cases requiring advanced retrieval strategies.
