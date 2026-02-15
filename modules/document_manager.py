"""
Document Manager - Business Documents Upload and Vector Store Integration
Handles PDF, DOCX, TXT uploads and automatic vectorization
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


def clean_pdf_text(text: str) -> str:
    """
    Clean PDF text by replacing encoding artifacts with proper characters
    """
    if not text:
        return text

    # Replace common PDF encoding artifacts
    replacements = {
        '(cid:127)': '•',
        '(cid:129)': '•',
        '(cid:139)': '‹',
        '(cid:155)': '›',
        '(cid:150)': '–',
        '(cid:151)': '—',
        '(cid:147)': '"',
        '(cid:148)': '"',
        '(cid:145)': ''',
        '(cid:146)': ''',
        '\x00': '',
        '\uf0b7': '•',
        '\uf0a7': '◦',
    }

    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # Remove any remaining (cid:XXX) patterns
    import re
    cleaned = re.sub(r'\(cid:\d+\)', '•', cleaned)

    return cleaned


class DocumentManager:
    """
    Manages business documents and integrates with Vector Store
    Supports PDF, DOCX, TXT files
    """

    def __init__(self, docs_path: str = "data/business_docs", rag_module=None):
        """
        Initialize Document Manager

        Args:
            docs_path: Path to store uploaded documents
            rag_module: RAG module instance for vectorization
        """
        self.docs_path = Path(docs_path)
        self.docs_path.mkdir(parents=True, exist_ok=True)
        self.rag_module = rag_module
        self.metadata_file = self.docs_path / "documents_metadata.json"
        self.metadata = self._load_metadata()

        logger.info(f"✅ Document Manager initialized at {docs_path}")

    def _load_metadata(self) -> Dict:
        """Load documents metadata"""
        if self.metadata_file.exists():
            import json
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {"documents": []}
        return {"documents": []}

    def _save_metadata(self):
        """Save documents metadata"""
        import json
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _get_file_hash(self, file_content: bytes) -> str:
        """Generate hash of file content"""
        return hashlib.md5(file_content).hexdigest()

    def upload_document(self, file_path: str, file_content: bytes,
                       doc_type: str = "general", description: str = "") -> Dict[str, Any]:
        """
        Upload a document and optionally vectorize it

        Args:
            file_path: Original file name
            file_content: File content as bytes
            doc_type: Type of document (policy, procedure, guide, etc.)
            description: Document description

        Returns:
            Dictionary with upload status and document info
        """
        try:
            # Get file extension
            file_name = Path(file_path).name
            file_ext = Path(file_path).suffix.lower()

            # Validate file type
            supported_types = ['.pdf', '.docx', '.txt', '.md']
            if file_ext not in supported_types:
                return {
                    'success': False,
                    'error': f"Unsupported file type. Supported: {', '.join(supported_types)}"
                }

            # Generate unique filename
            file_hash = self._get_file_hash(file_content)
            saved_name = f"{file_hash}_{file_name}"
            saved_path = self.docs_path / saved_name

            # Check if already uploaded
            existing = next((doc for doc in self.metadata['documents']
                           if doc['file_hash'] == file_hash), None)
            if existing:
                return {
                    'success': True,
                    'message': 'Document already exists',
                    'document': existing
                }

            # Save file
            with open(saved_path, 'wb') as f:
                f.write(file_content)

            # Extract text
            text_content = self._extract_text(saved_path, file_ext)

            # Create metadata entry
            doc_metadata = {
                'id': file_hash,
                'file_hash': file_hash,
                'original_name': file_name,
                'saved_name': saved_name,
                'file_type': file_ext[1:],  # Remove dot
                'doc_type': doc_type,
                'description': description,
                'upload_date': datetime.now().isoformat(),
                'size_bytes': len(file_content),
                'text_length': len(text_content) if text_content else 0,
                'vectorized': False
            }

            # Vectorize if RAG module available
            if self.rag_module and text_content:
                try:
                    self._vectorize_document(doc_metadata['id'], text_content)
                    doc_metadata['vectorized'] = True
                    logger.info(f"✅ Vectorized document: {file_name}")
                except Exception as e:
                    logger.warning(f"Failed to vectorize document: {e}")

            # Add to metadata
            self.metadata['documents'].append(doc_metadata)
            self._save_metadata()

            logger.info(f"✅ Uploaded document: {file_name}")
            return {
                'success': True,
                'message': 'Document uploaded successfully',
                'document': doc_metadata
            }

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_text(self, file_path: Path, file_ext: str) -> Optional[str]:
        """Extract text from document"""
        try:
            if file_ext == '.txt' or file_ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            elif file_ext == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        return clean_pdf_text(text)
                except ImportError:
                    logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
                    return None

            elif file_ext == '.docx':
                try:
                    import docx
                    doc = docx.Document(file_path)
                    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    return text
                except ImportError:
                    logger.warning("python-docx not installed. Install with: pip install python-docx")
                    return None

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None

    def _vectorize_document(self, doc_id: str, text_content: str):
        """Vectorize document and add to RAG system with auto-reindexing"""
        if not self.rag_module:
            return

        try:
            # Get document metadata for enrichment
            doc_meta = self.get_document(doc_id)
            if not doc_meta:
                logger.warning(f"Document {doc_id} not found in metadata")
                return

            # Create document chunks
            from rag import DocumentProcessor
            processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)

            # Get text chunks
            text_chunks = processor.chunk_text(text_content)
            logger.info(f"Created {len(text_chunks)} chunks for document {doc_id}")

            # Convert to proper document format for vector database
            rag_documents = []
            for chunk_idx, chunk_text in enumerate(text_chunks):
                rag_doc = {
                    'id': f"{doc_id}_chunk_{chunk_idx}",
                    'text': chunk_text,
                    'type': 'business_document',
                    'metadata': {
                        'doc_id': doc_id,
                        'doc_name': doc_meta['original_name'],
                        'doc_type': doc_meta['doc_type'],
                        'chunk_index': chunk_idx,
                        'total_chunks': len(text_chunks),
                        'source': 'uploaded_document'
                    }
                }
                rag_documents.append(rag_doc)

            # Add to vector database (incremental indexing)
            if hasattr(self.rag_module, 'vector_db'):
                self.rag_module.vector_db.add_documents(rag_documents)
                logger.info(f"✅ Added {len(rag_documents)} chunks to vector database")

                # Save updated index to disk
                from pathlib import Path
                vector_index_path = Path("data/vector_index")
                if vector_index_path.exists():
                    self.rag_module.vector_db.save_index(str(vector_index_path))
                    logger.info(f"✅ Saved updated index to {vector_index_path}")

        except Exception as e:
            logger.error(f"Error vectorizing document {doc_id}: {e}")
            raise

    def list_documents(self, doc_type: Optional[str] = None) -> List[Dict]:
        """
        List all uploaded documents

        Args:
            doc_type: Filter by document type (optional)

        Returns:
            List of document metadata
        """
        docs = self.metadata['documents']
        if doc_type:
            docs = [doc for doc in docs if doc['doc_type'] == doc_type]
        return docs

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document metadata by ID"""
        return next((doc for doc in self.metadata['documents']
                    if doc['id'] == doc_id), None)

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and remove its chunks from the vector index

        Args:
            doc_id: Document ID

        Returns:
            True if deleted successfully
        """
        try:
            doc = self.get_document(doc_id)
            if not doc:
                logger.warning(f"Document {doc_id} not found")
                return False

            doc_name = doc['original_name']
            logger.info(f"Deleting document: {doc_name}")

            # Step 1: Delete physical file
            file_path = self.docs_path / doc['saved_name']
            if file_path.exists():
                file_path.unlink()
                logger.info(f"  ✓ Deleted file: {doc['saved_name']}")

            # Step 2: Remove from metadata
            self.metadata['documents'] = [
                d for d in self.metadata['documents']
                if d['id'] != doc_id
            ]
            self._save_metadata()
            logger.info(f"  ✓ Removed from metadata")

            # Step 3: Remove chunks from vector index
            if self.rag_module and hasattr(self.rag_module, 'vector_db'):
                vector_db = self.rag_module.vector_db

                if vector_db.documents:
                    # Filter out all chunks belonging to this document
                    initial_count = len(vector_db.documents)
                    remaining_docs = [
                        d for d in vector_db.documents
                        if d.get('metadata', {}).get('doc_id') != doc_id
                    ]
                    removed_count = initial_count - len(remaining_docs)

                    if removed_count > 0:
                        logger.info(f"  ✓ Removing {removed_count} chunks from vector index...")

                        # Rebuild index with remaining documents
                        vector_db.documents = []
                        if hasattr(vector_db, 'doc_embeddings'):
                            vector_db.doc_embeddings = None

                        # Reinitialize FAISS index
                        import faiss
                        vector_db.index = faiss.IndexFlatL2(vector_db.dimension)

                        # Rebuild BM25 if enhanced RAG
                        if hasattr(vector_db, 'bm25'):
                            vector_db.bm25 = None
                            vector_db.tokenized_docs = None

                        if remaining_docs:
                            # Rebuild index with remaining documents
                            vector_db.build_index(remaining_docs)
                            logger.info(f"  ✓ Rebuilt index with {len(remaining_docs)} remaining chunks")

                            # Save updated index
                            from pathlib import Path
                            vector_index_path = Path("data/vector_index")
                            if vector_index_path.exists():
                                vector_db.save_index(str(vector_index_path))
                                logger.info(f"  ✓ Saved updated index")
                        else:
                            logger.info(f"  ⚠️  No documents remaining in index")
                    else:
                        logger.info(f"  ℹ️  No chunks found in vector index for this document")

            logger.info(f"✅ Successfully deleted document: {doc_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search documents using vector similarity

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant documents with scores
        """
        if not self.rag_module:
            # Fallback to keyword search in metadata
            query_lower = query.lower()
            results = []
            for doc in self.metadata['documents']:
                score = 0
                if query_lower in doc['original_name'].lower():
                    score += 2
                if query_lower in doc.get('description', '').lower():
                    score += 1
                if score > 0:
                    results.append({**doc, 'score': score})

            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]

        # Use RAG vector search
        try:
            search_results = self.rag_module.retrieve_context(query, top_k=top_k)
            # Map back to documents
            doc_ids = set()
            results = []

            for result in search_results:
                doc_id = result.get('metadata', {}).get('doc_id')
                if doc_id and doc_id not in doc_ids:
                    doc = self.get_document(doc_id)
                    if doc:
                        results.append({
                            **doc,
                            'relevance_score': result.get('score', 0),
                            'snippet': result.get('text', '')[:200] + '...'
                        })
                        doc_ids.add(doc_id)

            return results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get document store statistics"""
        docs = self.metadata['documents']

        stats = {
            'total_documents': len(docs),
            'by_type': {},
            'vectorized_count': sum(1 for doc in docs if doc.get('vectorized', False)),
            'total_size_mb': round(sum(doc.get('size_bytes', 0) for doc in docs) / (1024 * 1024), 2)
        }

        # Count by document type
        for doc in docs:
            doc_type = doc.get('doc_type', 'unknown')
            stats['by_type'][doc_type] = stats['by_type'].get(doc_type, 0) + 1

        return stats


# Example usage
if __name__ == "__main__":
    dm = DocumentManager()

    # Upload a text file
    with open("README.md", "rb") as f:
        content = f.read()

    result = dm.upload_document(
        file_path="README.md",
        file_content=content,
        doc_type="guide",
        description="Project README file"
    )

    print(f"Upload result: {result}")

    # List documents
    docs = dm.list_documents()
    print(f"Total documents: {len(docs)}")

    # Get stats
    stats = dm.get_stats()
    print(f"Stats: {stats}")
