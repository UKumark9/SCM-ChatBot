"""
Rebuild Vector Index with Improved Chunking
Forces re-vectorization of all documents
"""

import sys
import os
from pathlib import Path
import logging

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def rebuild_index():
    """Rebuild vector index from scratch with improved chunking"""
    try:
        print("="*70)
        print("🔨 Rebuilding Vector Index with Improved Chunking")
        print("="*70)

        # Import modules
        from modules.document_manager import DocumentManager
        from rag import DocumentProcessor, VectorDatabase, RAGModule

        # Initialize document manager
        print("\n1. Loading documents...")
        dm = DocumentManager(docs_path="data/business_docs")
        all_docs = dm.list_documents()

        if not all_docs:
            print("   ⚠️  No documents found!")
            return False

        print(f"   ✅ Found {len(all_docs)} documents")

        # Reset vectorized status
        print("\n2. Resetting vectorization status...")
        for doc in dm.metadata['documents']:
            doc['vectorized'] = False
        dm._save_metadata()
        print("   ✅ Reset complete")

        # Initialize vector database
        print("\n3. Initializing vector database with improved settings...")
        vector_db = VectorDatabase(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        )
        vector_db.initialize()
        print("   ✅ Vector database initialized")

        # Process all documents with improved chunking
        print(f"\n4. Vectorizing {len(all_docs)} document(s) with improved chunking...")
        doc_processor = DocumentProcessor(
            chunk_size=500,
            chunk_overlap=100  # Increased overlap for better context
        )

        successful = 0
        failed = 0
        all_documents = []

        # Import PDF extraction function
        from vectorize_documents import extract_pdf_text

        for idx, doc in enumerate(all_docs, 1):
            print(f"\n   [{idx}/{len(all_docs)}] {doc['original_name']}")

            try:
                # Read document file
                file_path = Path("data/business_docs") / doc['saved_name']

                if not file_path.exists():
                    print(f"      ❌ File not found")
                    failed += 1
                    continue

                # Extract text
                if doc['file_type'] == 'pdf':
                    text_content = extract_pdf_text(file_path)
                else:
                    text_content = dm._extract_text(file_path, f".{doc['file_type']}")

                if not text_content or len(text_content.strip()) < 10:
                    print(f"      ❌ Could not extract meaningful text")
                    failed += 1
                    continue

                text_length = len(text_content)
                print(f"      • {text_length:,} characters extracted")

                # Create document chunks with improved strategy
                chunks = doc_processor.chunk_text(text_content)
                print(f"      • {len(chunks)} chunks created (improved chunking)")

                # Create RAG documents
                for chunk_idx, chunk in enumerate(chunks):
                    rag_doc = {
                        'id': f"{doc['id']}_chunk_{chunk_idx}",
                        'text': chunk,
                        'type': 'business_document',
                        'metadata': {
                            'doc_id': doc['id'],
                            'doc_name': doc['original_name'],
                            'doc_type': doc['doc_type'],
                            'chunk_index': chunk_idx,
                            'total_chunks': len(chunks),
                            'source': 'uploaded_document'
                        }
                    }
                    all_documents.append(rag_doc)

                # Update metadata
                doc['vectorized'] = True
                doc['text_length'] = text_length
                dm.metadata['documents'] = [
                    d if d['id'] != doc['id'] else doc
                    for d in dm.metadata['documents']
                ]
                dm._save_metadata()

                print(f"      ✅ Vectorized successfully")
                successful += 1

            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
                failed += 1
                continue

        # Build vector index
        if all_documents:
            print(f"\n5. Building vector index with {len(all_documents)} chunks...")
            try:
                vector_db.build_index(all_documents)
                print(f"   ✅ Vector index built")

                # Create RAG module with improved threshold
                rag_module = RAGModule(
                    vector_db=vector_db,
                    top_k=5,
                    similarity_threshold=2.0  # Improved threshold
                )

                print("   ✅ RAG module created")

                # Save index to disk
                print("\n6. Saving vector index to disk...")
                vector_db.save_index("data/vector_index")
                print("   ✅ Index saved")

            except Exception as e:
                print(f"   ❌ Error building index: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return False

        # Print summary
        print("\n" + "="*70)
        print("✅ INDEX REBUILD COMPLETE")
        print("="*70)
        print(f"\nResults:")
        print(f"  • Successfully vectorized: {successful}/{len(all_docs)}")
        print(f"  • Failed: {failed}")
        print(f"  • Total chunks indexed: {len(all_documents)}")

        # Show improvements
        print(f"\n✨ Improvements applied:")
        print(f"  • Increased chunk overlap: 50 → 100 words")
        print(f"  • Semantic paragraph-aware chunking")
        print(f"  • Better similarity threshold: 0.7 → 2.0")
        print(f"  • Query expansion enabled")

        print()
        return successful > 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = rebuild_index()
    sys.exit(0 if success else 1)
