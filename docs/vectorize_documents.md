# vectorize_documents.py - Document Vectorization Utility

## Purpose
Utility script for converting text documents into vector embeddings and building FAISS index. Used for initial RAG setup and document ingestion.

## Key Components

### Functions

#### `load_documents(documents_path)`
Loads all text documents from directory.

**Parameters:**
- `documents_path` (str): Path to documents directory

**Returns:** list of (filename, content) tuples

**Supported Formats:**
- .txt files
- .md files
- .pdf files (if PyPDF2 available)

#### `chunk_documents(documents, chunk_size=500, overlap=50)`
Splits documents into overlapping chunks.

**Parameters:**
- `documents` (list): List of (filename, content) tuples
- `chunk_size` (int): Target chunk size in characters
- `overlap` (int): Overlap between chunks

**Returns:** list of chunk dicts

**Chunk Structure:**
```python
{
    'text': str,
    'source': str (filename),
    'chunk_id': int
}
```

**Chunking Strategy:**
- Sentence-aware splitting
- Maintains context with overlap
- Preserves document boundaries

#### `generate_embeddings(chunks, model_name='all-MiniLM-L6-v2')`
Generates vector embeddings for text chunks.

**Parameters:**
- `chunks` (list): List of chunk dicts
- `model_name` (str): Sentence transformer model

**Returns:** numpy.ndarray (embedding matrix)

**Embedding Model:**
- Default: all-MiniLM-L6-v2
- Dimension: 384
- Speed: ~3000 sentences/second

#### `build_faiss_index(embeddings)`
Builds FAISS index from embeddings.

**Parameters:**
- `embeddings` (numpy.ndarray): Embedding matrix

**Returns:** faiss.Index

**Index Configuration:**
- Type: Flat L2 (exact search)
- Metric: L2 distance
- Dimension: 384 (for MiniLM-L6-v2)

#### `save_index(index, chunks, metadata, index_path)`
Saves FAISS index and metadata to disk.

**Parameters:**
- `index` (faiss.Index): FAISS index
- `chunks` (list): Document chunks
- `metadata` (dict): Document metadata
- `index_path` (str): Output directory path

**Saves:**
- `index.faiss`: FAISS index file
- `index.pkl`: Metadata pickle file
- `chunks.json`: Chunk information

#### `main()`
Main execution function.

**Process:**
1. Load documents from directory
2. Chunk documents into passages
3. Generate embeddings
4. Build FAISS index
5. Save index and metadata

## Usage

### Command Line
```bash
python vectorize_documents.py
```

### Configuration
Edit paths in script:
```python
DOCUMENTS_PATH = "data/business_docs/documents/"
INDEX_PATH = "data/vector_index/"
METADATA_PATH = "data/business_docs/documents_metadata.json"
```

### Custom Parameters
```python
# Adjust chunking
chunks = chunk_documents(docs, chunk_size=1000, overlap=100)

# Use different model
embeddings = generate_embeddings(chunks, model_name='all-mpnet-base-v2')
```

## Example Workflow

```python
from vectorize_documents import *

# 1. Load documents
docs = load_documents("data/business_docs/documents/")
print(f"Loaded {len(docs)} documents")

# 2. Chunk documents
chunks = chunk_documents(docs, chunk_size=500, overlap=50)
print(f"Created {len(chunks)} chunks")

# 3. Generate embeddings
embeddings = generate_embeddings(chunks)
print(f"Generated embeddings: {embeddings.shape}")

# 4. Build index
index = build_faiss_index(embeddings)
print(f"Built FAISS index: {index.ntotal} vectors")

# 5. Save
save_index(index, chunks, metadata, "data/vector_index/")
print("Index saved successfully")
```

## Output Files

### index.faiss
- Binary FAISS index file
- Contains vector embeddings
- Used for similarity search

### index.pkl
- Pickled Python object
- Contains metadata and chunk information
- Maps index IDs to source documents

### documents_metadata.json
- JSON file with document information
- Titles, sources, dates
- Used for display in UI

## Performance

### Processing Time
- **10 documents**: ~5-10 seconds
- **50 documents**: ~30-60 seconds
- **100 documents**: ~2-3 minutes

**Factors:**
- Document size
- Chunk count
- Embedding model size
- CPU/GPU availability

### Memory Usage
- **Model**: ~100MB (sentence-transformers)
- **Embeddings**: ~1MB per 1000 chunks
- **Index**: Similar to embeddings

## Dependencies

### Required Libraries
```python
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os
from pathlib import Path
```

### Optional Libraries
```python
import PyPDF2  # For PDF support
import docx    # For Word document support
```

## Error Handling

### Document Load Error
- Skips problematic files
- Logs error with filename
- Continues with remaining documents

### Embedding Generation Error
- Retries with smaller batch
- Falls back to simpler model (if available)
- Logs error details

### Index Save Error
- Creates directory if doesn't exist
- Logs error with path
- Suggests checking permissions

## Best Practices

1. **Pre-process documents**: Remove headers, footers, irrelevant content
2. **Optimal chunk size**: 300-800 characters for most documents
3. **Overlap**: 50-100 characters to maintain context
4. **Batch processing**: Process documents in batches for large collections
5. **Validate output**: Check index size and sample retrievals

## Troubleshooting

### "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### "FAISS not installed"
```bash
pip install faiss-cpu  # For CPU
# or
pip install faiss-gpu  # For GPU
```

### "Out of memory"
- Reduce batch size in embedding generation
- Process documents in smaller batches
- Use smaller embedding model

## Integration Points

### Used By
- `main.py`: Document upload/vectorization
- `rebuild_index.py`: Index reconstruction

### Creates Data For
- `rag.py`: RAG module uses the index for retrieval
