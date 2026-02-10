# RAG Implementation Analysis & Improvements

**Date**: February 7, 2026
**Purpose**: Critical analysis and enhancement suggestions for RAG system

---

## 📊 Current Implementation Assessment

### ✅ What's Implemented Well

| Component | Implementation | Quality | Industry Standard |
|-----------|----------------|---------|-------------------|
| **Embedding Model** | sentence-transformers/all-MiniLM-L6-v2 | ✅ Good | ✅ Standard choice |
| **Vector Database** | FAISS IndexFlatL2 | ✅ Good | ✅ Production-ready |
| **Chunking Strategy** | Semantic paragraph-aware | ✅ Good | ⚠️ Can improve |
| **Query Expansion** | Keyword-based synonyms | ⚠️ Basic | ❌ Needs improvement |
| **Re-ranking** | None | ❌ Missing | ⚠️ Recommended |
| **Metadata Filtering** | Basic | ⚠️ Limited | ⚠️ Should enhance |
| **Hybrid Search** | Vector only | ❌ Missing | ⚠️ Recommended |

**Overall Grade**: 🟡 **B- (Good Foundation, Needs Enhancement)**

---

## ❌ Issues with Current Implementation

### 1. **Query Expansion is Too Simple**

**Current Code** ([rag.py:361-379](rag.py)):
```python
def _expand_query(self, query: str) -> List[str]:
    """Expand query with related terms"""
    query_lower = query.lower()
    expansions = [query]

    # Simple keyword substitution
    if 'delay' in query_lower:
        expansions.append(query.replace('delay', 'late delivery'))

    if 'severity' in query_lower:
        expansions.extend([
            query.replace('severity', 'classification'),
            query.replace('severity levels', 'delay categories')
        ])

    return expansions[:3]
```

**Problems**:
- ❌ Hard-coded keyword replacements
- ❌ Only handles specific terms
- ❌ Doesn't understand semantic meaning
- ❌ Misses related concepts

**Better Approach**: Use semantic expansion with embeddings

---

### 2. **No Re-Ranking After Initial Retrieval**

**Current Flow**:
```
Query → Embedding → Vector Search → Top-K Results → Return
```

**Problem**: Initial vector search may not perfectly rank results for the specific query intent.

**Industry Standard**:
```
Query → Embedding → Vector Search → Top-20 Results → Re-rank → Top-5 → Return
```

---

### 3. **Single Retrieval Strategy (Vector Only)**

**Current**: Only uses dense vector search (FAISS)

**Missing**:
- ❌ Keyword/BM25 search
- ❌ Hybrid search combining both
- ❌ Metadata filtering

**Industry Best Practice**: Hybrid retrieval combining:
- Dense vectors (semantic similarity)
- Sparse vectors (keyword matching)
- Metadata filters (doc type, date, etc.)

---

### 4. **Fixed Chunk Size Without Context**

**Current** ([rag.py:168-170](rag.py)):
```python
chunk_size = 500  # Fixed word count
chunk_overlap = 100
```

**Problems**:
- ❌ Some concepts need larger context
- ❌ Some queries need smaller, focused chunks
- ❌ No adaptive chunking based on content

---

### 5. **No Query Classification**

**Current**: Assumes all queries need same retrieval approach

**Missing**:
- Short factual queries → Need precise answers
- Comparison queries → Need multiple relevant chunks
- Procedural queries → Need step-by-step content
- Exploratory queries → Need broad context

---

### 6. **Similarity Threshold is Static**

**Current**:
```python
similarity_threshold = 2.0  # Fixed for all queries
```

**Problem**: Different query types need different thresholds
- Precise questions → Stricter threshold
- Broad questions → Looser threshold

---

### 7. **No Contextual Compression**

**Current**: Returns full 500-word chunks

**Problem**:
- Dilutes important information
- Increases LLM token usage
- May confuse the model with irrelevant context

**Better**: Extract only relevant sentences from chunks

---

### 8. **Limited Metadata Utilization**

**Current Metadata**:
```python
{
    'doc_id': '3ef883cc',
    'doc_name': '01_Product_Delay_Management_Policy.pdf',
    'doc_type': 'Policy',
    'chunk_index': 0
}
```

**Missing Useful Metadata**:
- Document sections/headings
- Creation/update dates
- Importance/priority scores
- Document relationships

---

## ✨ Recommended Improvements

### Priority 1: Add Re-Ranking (High Impact, Medium Effort)

**Implementation**:

```python
# Add to rag.py

class RAGModule:
    def __init__(self, vector_db, top_k=5, rerank_model=None):
        self.vector_db = vector_db
        self.top_k = top_k

        # Initialize re-ranker
        if rerank_model:
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder(rerank_model)
        else:
            self.reranker = None

    def retrieve_context(self, query: str) -> str:
        # 1. Initial retrieval (get more candidates)
        initial_k = self.top_k * 4  # Get 20 if top_k=5
        results = self.vector_db.search(query, top_k=initial_k)

        # 2. Re-rank with cross-encoder
        if self.reranker:
            reranked = self._rerank_results(query, results)
            results = reranked[:self.top_k]
        else:
            results = results[:self.top_k]

        return self._format_context(results)

    def _rerank_results(self, query: str, results: List[Tuple]) -> List[Tuple]:
        """Re-rank results using cross-encoder"""
        # Prepare pairs
        pairs = [(query, doc['text']) for doc, score in results]

        # Get re-ranking scores
        scores = self.reranker.predict(pairs)

        # Sort by re-ranking scores
        reranked = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc_score for (doc_score, _) in reranked]
```

**Models to use**:
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast, good quality)
- `cross-encoder/ms-marco-electra-base` (slower, better quality)

**Expected Improvement**: +15-25% retrieval accuracy

---

### Priority 2: Implement Hybrid Search (High Impact, High Effort)

**Current**: Vector-only search
**Improved**: Combine vector + keyword search

```python
# Add to rag.py

import rank_bm25

class VectorDatabase:
    def __init__(self):
        self.index = None  # FAISS
        self.bm25 = None   # BM25 for keyword search
        self.documents = []

    def build_index(self, documents: List[Dict]):
        # Build FAISS index (existing)
        self.documents = documents
        embeddings = self.embed_documents(documents)
        self.index.add(embeddings)

        # Build BM25 index (new)
        tokenized_docs = [doc['text'].lower().split() for doc in documents]
        self.bm25 = rank_bm25.BM25Okapi(tokenized_docs)

    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.5):
        """
        Hybrid search combining vector and keyword matching

        alpha: Weight for vector search (1-alpha for BM25)
               alpha=1.0 → pure vector search
               alpha=0.0 → pure keyword search
               alpha=0.5 → balanced hybrid
        """

        # 1. Vector search scores
        vector_results = self.search(query, top_k=top_k*2)
        vector_scores = {}
        for doc, distance in vector_results:
            similarity = 1 / (1 + distance)
            vector_scores[doc['id']] = similarity

        # 2. BM25 keyword search scores
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)

        # Normalize BM25 scores
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        bm25_normalized = {
            self.documents[i]['id']: score / max_bm25
            for i, score in enumerate(bm25_scores)
        }

        # 3. Combine scores
        all_doc_ids = set(vector_scores.keys()) | set(bm25_normalized.keys())

        hybrid_scores = {}
        for doc_id in all_doc_ids:
            vector_score = vector_scores.get(doc_id, 0)
            bm25_score = bm25_normalized.get(doc_id, 0)

            hybrid_scores[doc_id] = (
                alpha * vector_score +
                (1 - alpha) * bm25_score
            )

        # 4. Sort and return top-k
        sorted_docs = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = []
        for doc_id, score in sorted_docs:
            doc = next(d for d in self.documents if d['id'] == doc_id)
            results.append((doc, 1 - score))  # Convert back to distance

        return results
```

**Usage**:
```python
# For factual queries (favor exact matches)
results = vector_db.hybrid_search(query, alpha=0.3)

# For semantic queries (favor meaning)
results = vector_db.hybrid_search(query, alpha=0.7)

# Balanced
results = vector_db.hybrid_search(query, alpha=0.5)
```

**Expected Improvement**: +20-30% for keyword-heavy queries

---

### Priority 3: Add Contextual Compression (Medium Impact, Low Effort)

**Problem**: Returning 500-word chunks when only 2-3 sentences are relevant

**Solution**: Extract relevant sentences from chunks

```python
# Add to rag.py

from sentence_transformers import util

class RAGModule:
    def _compress_context(self, query: str, doc_text: str, top_sentences: int = 3):
        """
        Extract most relevant sentences from chunk
        """
        # Split into sentences
        sentences = doc_text.split('. ')

        # Embed query and sentences
        query_emb = self.vector_db.embedding_model.encode(query)
        sent_embs = self.vector_db.embedding_model.encode(sentences)

        # Calculate similarities
        similarities = util.cos_sim(query_emb, sent_embs)[0]

        # Get top-N sentences
        top_indices = similarities.argsort(descending=True)[:top_sentences]
        top_sentences_sorted = [sentences[i] for i in sorted(top_indices)]

        return '. '.join(top_sentences_sorted)

    def retrieve_context(self, query: str, compress: bool = True) -> str:
        results = self.vector_db.search(query, top_k=5)

        context_parts = []
        for doc, score in results:
            if compress:
                # Extract only relevant sentences
                compressed_text = self._compress_context(
                    query,
                    doc['text'],
                    top_sentences=3
                )
                context_parts.append(compressed_text)
            else:
                # Use full chunk
                context_parts.append(doc['text'])

        return '\n---\n'.join(context_parts)
```

**Expected Improvement**: +10-15% answer accuracy, -30% token usage

---

### Priority 4: Semantic Query Expansion (Medium Impact, Medium Effort)

**Current**: Hard-coded keyword substitution
**Improved**: Use embeddings to find similar queries

```python
# Add to rag.py

class RAGModule:
    def __init__(self, vector_db, top_k=5):
        self.vector_db = vector_db
        self.top_k = top_k

        # Pre-computed query templates for common patterns
        self.query_templates = {
            'severity_levels': [
                "What are the severity classifications?",
                "What are the delay categories?",
                "How are delays categorized?",
                "What are the priority levels?"
            ],
            'procedures': [
                "What is the process?",
                "What are the steps?",
                "What is the procedure?",
                "How do we handle this?"
            ]
        }

    def _semantic_query_expansion(self, query: str, num_expansions: int = 2):
        """
        Generate semantically similar queries using embedding similarity
        """
        # Embed original query
        query_emb = self.vector_db.embedding_model.encode(query)

        # Find most similar templates
        best_templates = []
        for template_type, templates in self.query_templates.items():
            template_embs = self.vector_db.embedding_model.encode(templates)
            similarities = util.cos_sim(query_emb, template_embs)[0]

            # Get top similar templates
            for i, sim in enumerate(similarities):
                if sim > 0.7:  # Similarity threshold
                    best_templates.append((templates[i], sim.item()))

        # Sort by similarity
        best_templates.sort(key=lambda x: x[1], reverse=True)

        # Return original + top N expansions
        expansions = [query]
        expansions.extend([t for t, _ in best_templates[:num_expansions]])

        return expansions
```

**Alternative**: Use LLM for query expansion

```python
def _llm_query_expansion(self, query: str):
    """Generate query variations using LLM"""
    prompt = f"""Generate 2 alternative ways to ask this question while keeping the same meaning:

Original: "{query}"

Alternative 1:
Alternative 2:"""

    # Call LLM (Groq/OpenAI)
    response = self.llm_client.complete(prompt)
    alternatives = response.split('\n')[:2]

    return [query] + alternatives
```

**Expected Improvement**: +10-15% recall

---

### Priority 5: Query Classification for Adaptive Retrieval (High Impact, Medium Effort)

**Classify queries to use different retrieval strategies**

```python
# Add to rag.py

class QueryClassifier:
    """Classify query type to optimize retrieval"""

    def classify(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()

        # Factual query (needs precise answer)
        factual_patterns = ['what is', 'define', 'how many', 'when']
        is_factual = any(p in query_lower for p in factual_patterns)

        # Comparison query (needs multiple sources)
        comparison_patterns = ['difference', 'compare', 'versus', 'vs']
        is_comparison = any(p in query_lower for p in comparison_patterns)

        # Procedural query (needs steps)
        procedural_patterns = ['how to', 'steps', 'process', 'procedure']
        is_procedural = any(p in query_lower for p in procedural_patterns)

        # List query (needs enumeration)
        list_patterns = ['list', 'what are', 'types of', 'categories']
        is_list = any(p in query_lower for p in list_patterns)

        # Determine query type
        if is_factual:
            query_type = 'factual'
            retrieval_params = {
                'top_k': 3,
                'threshold': 1.5,  # Stricter
                'compress': True,
                'alpha': 0.4  # Favor keywords
            }
        elif is_comparison:
            query_type = 'comparison'
            retrieval_params = {
                'top_k': 6,
                'threshold': 2.5,
                'compress': False,
                'alpha': 0.6  # Favor semantics
            }
        elif is_procedural:
            query_type = 'procedural'
            retrieval_params = {
                'top_k': 4,
                'threshold': 2.0,
                'compress': False,
                'alpha': 0.5
            }
        elif is_list:
            query_type = 'list'
            retrieval_params = {
                'top_k': 5,
                'threshold': 2.0,
                'compress': True,
                'alpha': 0.3  # Strong keyword matching
            }
        else:
            query_type = 'general'
            retrieval_params = {
                'top_k': 5,
                'threshold': 2.0,
                'compress': False,
                'alpha': 0.5
            }

        return {
            'type': query_type,
            'params': retrieval_params
        }

# Usage in RAGModule
class RAGModule:
    def __init__(self, vector_db, top_k=5):
        self.vector_db = vector_db
        self.classifier = QueryClassifier()

    def retrieve_context(self, query: str) -> str:
        # Classify query
        classification = self.classifier.classify(query)
        params = classification['params']

        # Use adaptive parameters
        if hasattr(self.vector_db, 'hybrid_search'):
            results = self.vector_db.hybrid_search(
                query,
                top_k=params['top_k'],
                alpha=params['alpha']
            )
        else:
            results = self.vector_db.search(query, top_k=params['top_k'])

        # Apply contextual compression if needed
        if params['compress']:
            context = self._compressed_context(query, results)
        else:
            context = self._format_context(results)

        return context
```

**Expected Improvement**: +15-20% overall accuracy

---

### Priority 6: Add Metadata Filtering (Low Impact, Low Effort)

**Enable filtering by document properties**

```python
# Enhanced search with filters
def search_with_filters(
    self,
    query: str,
    top_k: int = 5,
    doc_type: Optional[str] = None,
    date_range: Optional[Tuple[str, str]] = None
):
    """Search with metadata filters"""

    # Initial vector search (broader)
    results = self.search(query, top_k=top_k*3)

    # Filter by metadata
    filtered = []
    for doc, score in results:
        metadata = doc.get('metadata', {})

        # Doc type filter
        if doc_type and metadata.get('doc_type') != doc_type:
            continue

        # Date range filter
        if date_range:
            doc_date = metadata.get('upload_date')
            if doc_date:
                if not (date_range[0] <= doc_date <= date_range[1]):
                    continue

        filtered.append((doc, score))

        if len(filtered) >= top_k:
            break

    return filtered
```

**Usage**:
```python
# Search only in policy documents
results = vector_db.search_with_filters(
    query="severity levels",
    doc_type="Policy"
)

# Search recent documents
results = vector_db.search_with_filters(
    query="new procedures",
    date_range=("2026-01-01", "2026-12-31")
)
```

---

### Priority 7: Implement Parent-Child Chunking (Medium Impact, High Effort)

**Problem**: 500-word chunks may lose context

**Solution**: Store both small chunks (for retrieval) and large chunks (for context)

```python
class DocumentProcessor:
    def create_hierarchical_chunks(self, text: str):
        """
        Create parent-child chunk relationships

        - Child chunks: 200 words (for retrieval)
        - Parent chunks: 800 words (for context)
        """

        # Create parent chunks (large)
        parent_chunks = self.chunk_text(
            text,
            chunk_size=800,
            chunk_overlap=100
        )

        # Create child chunks (small)
        child_chunks = self.chunk_text(
            text,
            chunk_size=200,
            chunk_overlap=50
        )

        # Map children to parents
        hierarchical = []
        for child_idx, child in enumerate(child_chunks):
            # Find which parent contains this child
            parent_idx = child_idx // 4  # Roughly 4 children per parent

            if parent_idx < len(parent_chunks):
                hierarchical.append({
                    'child_text': child,
                    'parent_text': parent_chunks[parent_idx],
                    'child_id': child_idx,
                    'parent_id': parent_idx
                })

        return hierarchical

# During retrieval
def retrieve_with_context(self, query: str):
    # Search using child chunks (precise)
    results = self.vector_db.search(query, top_k=5)

    # But return parent chunks (full context)
    context_parts = []
    for doc, score in results:
        parent_text = doc['metadata'].get('parent_text', doc['text'])
        context_parts.append(parent_text)

    return '\n---\n'.join(context_parts)
```

**Expected Improvement**: +10-15% answer completeness

---

## 📈 Implementation Priority Matrix

```
High Impact │ ┌─────────────────┐  ┌──────────────┐
            │ │  Re-Ranking     │  │ Hybrid       │
            │ │  (Priority 1)   │  │ Search       │
            │ └─────────────────┘  │ (Priority 2) │
            │                      └──────────────┘
            │
Medium      │ ┌───────────────┐   ┌──────────────┐
Impact      │ │ Query         │   │ Contextual   │
            │ │ Classification│   │ Compression  │
            │ │ (Priority 5)  │   │ (Priority 3) │
            │ └───────────────┘   └──────────────┘
            │
Low Impact  │                     ┌──────────────┐
            │                     │ Metadata     │
            │                     │ Filtering    │
            │                     │ (Priority 6) │
            │                     └──────────────┘
            └─────────────────────────────────────
              Low Effort   Medium    High Effort
```

---

## 🚀 Quick Wins (Implement First)

### 1. Add Re-Ranking (2-3 hours)
```bash
pip install sentence-transformers
# Then implement _rerank_results() method
```

### 2. Add Contextual Compression (1-2 hours)
```python
# Just add _compress_context() method
# Immediate 30% token savings
```

### 3. Improve Query Expansion (1 hour)
```python
# Replace hard-coded keywords with semantic templates
```

---

## 📊 Expected Overall Improvement

| Metric | Before | After All Improvements | Gain |
|--------|--------|----------------------|------|
| **Precision@5** | 40% | 65-75% | +25-35% |
| **Recall@5** | 100% | 100% | Maintained |
| **Answer Accuracy** | 60-70% | 80-90% | +20-30% |
| **Token Usage** | 1500 avg | 1000 avg | -33% |
| **Response Time** | 562ms | 650ms | +88ms (acceptable) |

---

## 🎯 Recommended Implementation Order

### Phase 1 (Week 1): Quick Wins
1. ✅ Add re-ranking with cross-encoder
2. ✅ Implement contextual compression
3. ✅ Improve query expansion

**Expected**: +30% improvement, 4-6 hours work

### Phase 2 (Week 2): Core Enhancements
4. ✅ Implement hybrid search (vector + BM25)
5. ✅ Add query classification
6. ✅ Add metadata filtering

**Expected**: +20% improvement, 8-12 hours work

### Phase 3 (Week 3): Advanced Features
7. ✅ Implement parent-child chunking
8. ✅ Add dynamic threshold adjustment
9. ✅ Implement feedback loop for continuous improvement

**Expected**: +10% improvement, 12-16 hours work

---

## 💻 Quick Implementation Template

```python
# Enhanced RAGModule with improvements

class EnhancedRAGModule(RAGModule):
    def __init__(self, vector_db, top_k=5):
        super().__init__(vector_db, top_k)

        # Load re-ranker
        from sentence_transformers import CrossEncoder
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        # Query classifier
        self.classifier = QueryClassifier()

    def retrieve_context(self, query: str) -> str:
        # 1. Classify query
        classification = self.classifier.classify(query)
        params = classification['params']

        # 2. Expand query semantically
        expanded_queries = self._semantic_query_expansion(query)

        # 3. Hybrid search with adaptive parameters
        all_results = {}
        for q in expanded_queries:
            results = self.vector_db.hybrid_search(
                q,
                top_k=params['top_k'] * 4,
                alpha=params['alpha']
            )

            for doc, score in results:
                doc_id = doc['id']
                if doc_id not in all_results or score < all_results[doc_id][1]:
                    all_results[doc_id] = (doc, score)

        # 4. Re-rank results
        sorted_results = sorted(all_results.values(), key=lambda x: x[1])
        top_candidates = sorted_results[:params['top_k'] * 2]

        reranked = self._rerank_results(query, top_candidates)
        final_results = reranked[:params['top_k']]

        # 5. Compress context if needed
        if params['compress']:
            context = self._compressed_context(query, final_results)
        else:
            context = self._format_context(final_results)

        return context
```

---

## 📚 Additional Reading

- **Hybrid Search**: [Weaviate Hybrid Search Guide](https://weaviate.io/blog/hybrid-search-explained)
- **Re-ranking**: [Pinecone Re-ranking Guide](https://www.pinecone.io/learn/series/rag/reranking/)
- **Advanced RAG**: [LlamaIndex Advanced RAG](https://docs.llamaindex.ai/en/stable/examples/low_level/oss_ingestion_retrieval.html)

---

## ✅ Summary

**Current Implementation**: ✅ Solid foundation, works well for basic queries

**Main Issues**:
1. ❌ Simple query expansion
2. ❌ No re-ranking
3. ❌ Vector-only search
4. ❌ Fixed retrieval parameters

**Quick Wins** (4-6 hours):
1. Add re-ranking (+15-25%)
2. Add contextual compression (+10-15%, -30% tokens)
3. Improve query expansion (+10-15%)

**Total Potential Improvement**: **+35-55% retrieval accuracy**

---

**Next Steps**: Start with Priority 1 (Re-Ranking) for immediate 15-25% improvement! 🚀
