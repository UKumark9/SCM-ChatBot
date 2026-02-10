# rag.py - Retrieval-Augmented Generation Module

## Purpose
Implements RAG (Retrieval-Augmented Generation) for semantic document retrieval using FAISS vector indexing and sentence transformers for embedding generation.

## Key Components

### Class: RAGModule
Main class for document retrieval and context generation.

**Initialization Parameters:**
- `index_path` (str): Path to FAISS vector index directory
- `documents_path` (str): Path to business documents directory
- `metadata_path` (str): Path to document metadata JSON file
- `model_name` (str): Sentence transformer model name (default: "all-MiniLM-L6-v2")

## Core Methods

### `__init__(index_path, documents_path, metadata_path, model_name)`
Initializes RAG module with vector index and document paths.

**Features:**
- Loads FAISS vector index
- Loads document metadata
- Initializes sentence transformer model
- Sets up retrieval pipeline

### `retrieve_context(query, top_k=3)`
Retrieves most relevant document chunks for a query.

**Parameters:**
- `query` (str): User's question
- `top_k` (int): Number of top documents to retrieve (default: 3)

**Returns:** str (formatted context with document excerpts)

**Process:**
1. Generates query embedding using sentence transformer
2. Searches FAISS index for similar vectors
3. Retrieves top_k most relevant documents
4. Formats results with relevance scores

**Example:**
```python
rag = RAGModule(index_path="data/vector_index/")
context = rag.retrieve_context("What are severity levels?", top_k=3)
# Returns formatted context with policy document excerpts
```

### `add_document(document_text, metadata)`
Adds a new document to the vector index.

**Parameters:**
- `document_text` (str): Full document text
- `metadata` (dict): Document metadata (title, source, date, etc.)

**Process:**
1. Chunks document into passages
2. Generates embeddings for each chunk
3. Adds to FAISS index
4. Updates metadata JSON

### `delete_document(doc_id)`
Removes a document from the vector index.

**Parameters:**
- `doc_id` (str): Document identifier

**Process:**
1. Removes document vectors from FAISS index
2. Updates metadata JSON
3. Saves updated index

### `rebuild_index()`
Rebuilds entire FAISS index from documents.

**Use Cases:**
- After bulk document updates
- Index corruption recovery
- Changing embedding model

**Process:**
1. Clears existing index
2. Re-processes all documents
3. Generates fresh embeddings
4. Builds new FAISS index

## Helper Methods

### `_chunk_document(text, chunk_size=500, overlap=50)`
Splits document into overlapping chunks.

**Parameters:**
- `text` (str): Full document text
- `chunk_size` (int): Target chunk size in characters
- `overlap` (int): Overlap between chunks

**Returns:** List[str] (document chunks)

**Strategy:**
- Sentence-aware chunking
- Maintains context with overlap
- Preserves semantic coherence

### `_generate_embeddings(texts)`
Generates vector embeddings for text passages.

**Parameters:**
- `texts` (List[str]): Text passages to embed

**Returns:** numpy.ndarray (embedding vectors)

**Features:**
- Uses sentence-transformers model
- Batch processing for efficiency
- 384-dimensional vectors (MiniLM-L6-v2)

### `_format_retrieved_context(results)`
Formats retrieved documents for LLM consumption.

**Parameters:**
- `results` (List[tuple]): (text, score, metadata) tuples

**Returns:** str (formatted context)

**Format:**
```
Document 1 (Relevance: 0.85):
[Document excerpt...]

Document 2 (Relevance: 0.72):
[Document excerpt...]
```

## Technical Details

### Vector Index
- **Technology**: FAISS (Facebook AI Similarity Search)
- **Index Type**: Flat L2 (exact search)
- **Dimension**: 384 (sentence-transformers MiniLM-L6-v2)
- **Similarity Metric**: L2 distance (lower is better)

### Embedding Model
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Embedding Dimension**: 384
- **Max Sequence Length**: 512 tokens
- **Speed**: ~3000 sentences/second on CPU

### Document Processing
- **Chunking**: 500 characters with 50-character overlap
- **Metadata**: Stored separately in JSON
- **Format**: Supports .txt, .pdf, .docx

## Dependencies

### External Libraries
- `faiss-cpu`: Vector similarity search
- `sentence-transformers`: Text embedding generation
- `numpy`: Array operations
- `json`: Metadata management

### Internal Modules
- None (standalone module)

## Usage Examples

### Basic Retrieval
```python
from rag import RAGModule

# Initialize
rag = RAGModule(
    index_path="data/vector_index/",
    documents_path="data/business_docs/documents/",
    metadata_path="data/business_docs/documents_metadata.json"
)

# Retrieve context
context = rag.retrieve_context("What is the delay policy?", top_k=3)
print(context)
```

### Add New Document
```python
# Add document
rag.add_document(
    document_text="Policy text here...",
    metadata={
        "title": "Delay Management Policy",
        "source": "policy_docs",
        "date": "2026-01-15"
    }
)
```

### Rebuild Index
```python
# Rebuild entire index
rag.rebuild_index()
```

## File Structure

```
data/
├── vector_index/
│   ├── index.faiss           # FAISS index file
│   └── index.pkl             # Metadata pickle
├── business_docs/
│   ├── documents/            # Source documents
│   └── documents_metadata.json  # Document metadata
```

## Performance Characteristics

### Retrieval Speed
- **Query embedding**: ~10ms
- **FAISS search**: ~5ms for 1000 documents
- **Total**: ~15-20ms per query

### Memory Usage
- **Model**: ~100MB (sentence-transformers)
- **Index**: ~1MB per 1000 documents
- **Total**: ~100-200MB

### Accuracy
- **Semantic similarity**: High (transformer-based)
- **Cross-domain**: Good (pre-trained on diverse corpus)
- **Domain-specific**: Excellent after fine-tuning

## Error Handling

### Index Not Found
- Returns empty context
- Logs warning
- Continues operation

### Document Processing Error
- Skips problematic document
- Logs error with details
- Continues with remaining documents

### Embedding Generation Error
- Falls back to keyword search (if available)
- Returns error context
- Logs exception

## Optimization Tips

1. **Batch Processing**: Process multiple documents at once
2. **Index Tuning**: Use IVF index for >100k documents
3. **Chunking Strategy**: Adjust chunk_size based on document type
4. **Model Selection**: Use larger model for better accuracy, smaller for speed

## Integration Points

### Used By
- `enhanced_chatbot.py`: Context retrieval for LLM
- `agents/delay_agent.py`: Policy document retrieval
- `agents/analytics_agent.py`: Policy context for analytics
- `main.py`: Document management UI

### Integrates With
- FAISS vector index
- Sentence transformers
- Document metadata storage
