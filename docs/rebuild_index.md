# rebuild_index.py - FAISS Index Rebuilding Utility

## Purpose
Utility script for rebuilding the FAISS vector index from scratch. Used for index maintenance, corruption recovery, or embedding model changes.

## Key Components

### Functions

#### `rebuild_index_from_documents(documents_path, index_path, metadata_path)`
Rebuilds complete FAISS index from document directory.

**Parameters:**
- `documents_path` (str): Path to documents directory
- `index_path` (str): Output path for new index
- `metadata_path` (str): Path to metadata JSON

**Returns:** bool (success/failure)

**Process:**
1. Clears existing index files
2. Loads all documents from directory
3. Chunks documents
4. Generates fresh embeddings
5. Builds new FAISS index
6. Saves index and metadata

**Example:**
```python
success = rebuild_index_from_documents(
    documents_path="data/business_docs/documents/",
    index_path="data/vector_index/",
    metadata_path="data/business_docs/documents_metadata.json"
)
```

#### `clear_existing_index(index_path)`
Removes existing index files.

**Parameters:**
- `index_path` (str): Path to index directory

**Removes:**
- index.faiss
- index.pkl
- chunks.json
- Any other index-related files

#### `verify_index(index_path)`
Verifies index integrity after rebuild.

**Parameters:**
- `index_path` (str): Path to index directory

**Returns:** bool (valid/invalid)

**Checks:**
- Index file exists and readable
- Metadata file exists and valid JSON
- Vector count matches chunk count
- Sample similarity search works

## Usage

### Command Line
```bash
python rebuild_index.py
```

### Programmatic
```python
from rebuild_index import rebuild_index_from_documents

# Rebuild index
success = rebuild_index_from_documents(
    documents_path="data/business_docs/documents/",
    index_path="data/vector_index/",
    metadata_path="data/business_docs/documents_metadata.json"
)

if success:
    print("✅ Index rebuilt successfully")
else:
    print("❌ Index rebuild failed")
```

### With Verification
```python
from rebuild_index import rebuild_index_from_documents, verify_index

# Rebuild
rebuild_index_from_documents(...)

# Verify
if verify_index("data/vector_index/"):
    print("✅ Index verified")
else:
    print("❌ Index validation failed")
```

## When to Rebuild Index

### Required Scenarios
1. **Index Corruption**: FAISS index file corrupted or unreadable
2. **Model Change**: Switching to different embedding model
3. **Major Document Updates**: Bulk document additions/removals
4. **Metadata Mismatch**: Index and metadata out of sync

### Optional Scenarios
1. **Performance Optimization**: Rebuild with optimized index type
2. **Regular Maintenance**: Periodic rebuild for consistency
3. **Version Upgrade**: After FAISS version upgrade

## Rebuild Process

### Step-by-Step
```
1. Backup existing index (optional but recommended)
   ├─ Copy index.faiss → index.faiss.backup
   └─ Copy index.pkl → index.pkl.backup

2. Clear existing index files
   ├─ Remove index.faiss
   ├─ Remove index.pkl
   └─ Remove chunks.json

3. Load documents
   ├─ Read all .txt, .md, .pdf files
   └─ Extract text content

4. Chunk documents
   ├─ Split into 500-character chunks
   └─ 50-character overlap

5. Generate embeddings
   ├─ Use sentence-transformers model
   └─ Create 384-dimensional vectors

6. Build FAISS index
   ├─ Create Flat L2 index
   └─ Add all embeddings

7. Save new index
   ├─ Write index.faiss
   ├─ Write index.pkl
   └─ Update metadata.json

8. Verify index
   ├─ Check file existence
   ├─ Validate vector count
   └─ Test sample search
```

## Configuration

### Default Paths
```python
DOCUMENTS_PATH = "data/business_docs/documents/"
INDEX_PATH = "data/vector_index/"
METADATA_PATH = "data/business_docs/documents_metadata.json"
```

### Chunking Parameters
```python
CHUNK_SIZE = 500  # characters
OVERLAP = 50      # characters
```

### Embedding Model
```python
MODEL_NAME = "all-MiniLM-L6-v2"  # Default
# Alternatives:
# "all-mpnet-base-v2"  # Better quality, slower
# "all-MiniLM-L12-v2"  # Balanced
```

## Output

### Console Output
```
🔄 Rebuilding FAISS Index...

📁 Loading documents from: data/business_docs/documents/
✅ Loaded 23 documents

✂️ Chunking documents...
✅ Created 456 chunks

🧮 Generating embeddings...
✅ Generated embeddings (456, 384)

🏗️ Building FAISS index...
✅ Built index with 456 vectors

💾 Saving index...
✅ Index saved to: data/vector_index/

✔️ Verifying index...
✅ Index verified successfully

✅ Index rebuild complete! (52.3 seconds)
```

### Error Output
```
❌ Error: Failed to load documents
   → Check documents path: data/business_docs/documents/

❌ Error: Embedding generation failed
   → Check sentence-transformers installation

❌ Error: Index save failed
   → Check write permissions for: data/vector_index/
```

## Error Handling

### Document Load Failure
- Lists problematic files
- Continues with valid documents
- Logs errors to console/file

### Embedding Generation Failure
- Retries with smaller batches
- Falls back to CPU if GPU fails
- Reports progress and errors

### Index Save Failure
- Creates directories if missing
- Checks write permissions
- Suggests resolution steps

## Performance

### Rebuild Time
- **Small** (10-20 docs): ~10-30 seconds
- **Medium** (50-100 docs): ~1-3 minutes
- **Large** (200+ docs): ~5-10 minutes

**Factors:**
- Number of documents
- Document sizes
- Embedding model speed
- CPU/GPU availability

### Resource Usage
- **CPU**: High during embedding generation
- **Memory**: ~200-500MB (model + data)
- **Disk**: Temporary space for new index

## Best Practices

1. **Backup before rebuild**: Save existing index as .backup
2. **Run during maintenance window**: Can take several minutes
3. **Verify after rebuild**: Ensure index works correctly
4. **Test sample queries**: Validate retrieval quality
5. **Monitor logs**: Check for errors or warnings

## Troubleshooting

### Rebuild Hangs
- Check CPU usage (should be high)
- Verify sufficient memory
- Check for very large documents

### Poor Retrieval After Rebuild
- Verify chunk size appropriate for documents
- Check embedding model loaded correctly
- Test with known good queries

### Index File Not Created
- Check write permissions
- Verify index_path exists
- Check disk space available

## Dependencies

### Required Libraries
- faiss-cpu or faiss-gpu
- sentence-transformers
- numpy
- pathlib
- json

### Internal Modules
- vectorize_documents (reuses functions)

## Integration Points

### Called By
- Manual maintenance scripts
- Automated rebuild jobs
- Document management UI (via main.py)

### Calls
- vectorize_documents.py functions for processing

## Comparison: Rebuild vs Incremental Update

### Full Rebuild
- **Pros**: Clean state, fixes corruption, optimizes index
- **Cons**: Time-consuming, requires downtime
- **When**: Major changes, corruption, model switch

### Incremental Update
- **Pros**: Fast, no downtime, preserves existing index
- **Cons**: Can lead to fragmentation, doesn't fix corruption
- **When**: Single document add/remove

**Recommendation**: Use incremental updates for single documents, rebuild periodically (monthly) or when needed.
