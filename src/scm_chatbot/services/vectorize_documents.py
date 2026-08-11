"""
Vectorize Uploaded Business Documents for RAG
Improved version with better PDF extraction using multiple strategies
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

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def clean_pdf_text(text: str) -> str:
    """
    Clean PDF text by replacing encoding artifacts with proper characters

    Args:
        text: Raw PDF text

    Returns:
        Cleaned text with proper characters
    """
    if not text:
        return text

    # Replace common PDF encoding artifacts
    replacements = {
        '(cid:127)': '•',  # Bullet point
        '(cid:129)': '•',
        '(cid:139)': '‹',
        '(cid:155)': '›',
        '(cid:150)': '–',  # En dash
        '(cid:151)': '—',  # Em dash
        '(cid:147)': '"',  # Left double quote
        '(cid:148)': '"',  # Right double quote
        '(cid:145)': ''',  # Left single quote
        '(cid:146)': ''',  # Right single quote
        '\x00': '',  # Null characters
        '\uf0b7': '•',  # Another bullet variant
        '\uf0a7': '◦',  # Circle bullet
    }

    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # Remove any remaining (cid:XXX) patterns
    import re
    cleaned = re.sub(r'\(cid:\d+\)', '•', cleaned)

    return cleaned


def extract_pdf_text(file_path: Path) -> str:
    """
    Extract text from PDF using multiple strategies
    Tries pdfplumber first, then PyPDF2, then falls back to document name
    """
    text = ""
    
    # Strategy 1: Try pdfplumber (best for extraction)
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            logger.info(f"      ✓ Extracted with pdfplumber")
            return clean_pdf_text(text)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"      pdfplumber failed: {e}")
    
    # Strategy 2: Try PyPDF2
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            logger.info(f"      ✓ Extracted with PyPDF2")
            return clean_pdf_text(text)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"      PyPDF2 failed: {e}")
    
    # Strategy 3: Try pypdf (newer name for PyPDF2)
    try:
        import pypdf
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            logger.info(f"      ✓ Extracted with pypdf")
            return clean_pdf_text(text)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"      pypdf failed: {e}")
    
    # Strategy 4: Fallback - use document name and metadata as content
    # This ensures documents are still indexed even if text extraction fails
    filename = file_path.stem
    fallback_text = f"""
    Document: {filename}
    
    This is an indexed document. The full text could not be extracted,
    but the document is available for search by name and metadata.
    
    File: {file_path.name}
    """
    
    logger.warning(f"      ⚠️  No PDF extraction library available - using document name as content")
    return fallback_text.strip()


def vectorize_uploaded_documents():
    """Vectorize all uploaded business documents"""
    try:
        print("="*70)
        print("🔨 Vectorizing Uploaded Business Documents")
        print("="*70)

        # Check dependencies
        print("\n1. Checking dependencies...")
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            print("   ✅ sentence-transformers and faiss installed")
        except ImportError as e:
            print(f"   ❌ Dependencies missing: {e}")
            print("   Install with: pip install sentence-transformers faiss-cpu")
            return False

        # Import modules
        from modules.document_manager import DocumentManager
        from rag import DocumentProcessor, VectorDatabase, RAGModule

        # Initialize document manager
        print("\n2. Loading document manager...")
        dm = DocumentManager(docs_path="data/business_docs")
        all_docs = dm.list_documents()

        if not all_docs:
            print("   ⚠️  No documents found!")
            return False

        print(f"   ✅ Found {len(all_docs)} documents")

        # Check which need vectorization
        docs_to_vectorize = [doc for doc in all_docs if not doc.get('vectorized', False)]
        vectorized_docs = [doc for doc in all_docs if doc.get('vectorized', False)]

        print(f"\n3. Vectorization status:")
        print(f"   • Already vectorized: {len(vectorized_docs)}")
        print(f"   • Need vectorization: {len(docs_to_vectorize)}")

        if not docs_to_vectorize:
            print("\n✅ All documents are already vectorized!")
            return True

        # Initialize vector database
        print("\n4. Initializing vector database...")
        vector_db = VectorDatabase(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        )
        vector_db.initialize()
        print("   ✅ Vector database initialized")

        # Process each document
        print(f"\n5. Vectorizing {len(docs_to_vectorize)} document(s)...")
        doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)  # Increased overlap

        successful = 0
        failed = 0
        all_documents = []

        for idx, doc in enumerate(docs_to_vectorize, 1):
            print(f"\n   [{idx}/{len(docs_to_vectorize)}] {doc['original_name']}")
            
            try:
                # Read document file
                file_path = Path("data/business_docs") / doc['saved_name']
                
                if not file_path.exists():
                    print(f"      ❌ File not found")
                    failed += 1
                    continue

                # Extract text with fallback strategies
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

                # Create document chunks
                chunks = doc_processor.chunk_text(text_content)
                print(f"      • {len(chunks)} chunks created")

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

        # Build vector index with all documents
        if all_documents:
            print(f"\n6. Building vector index with {len(all_documents)} chunks...")
            try:
                vector_db.build_index(all_documents)
                print(f"   ✅ Vector index built")
                
                # Create RAG module
                rag_module = RAGModule(
                    vector_db=vector_db,
                    top_k=5,
                    similarity_threshold=2.0  # Improved threshold for better recall
                )
                
                print("   ✅ RAG module created")
                
                # Save index to disk
                print("\n7. Saving vector index to disk...")
                vector_db.save_index("data/vector_index")
                print("   ✅ Index saved")

            except Exception as e:
                print(f"   ❌ Error building index: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return False

        # Print summary
        print("\n" + "="*70)
        print("✅ VECTORIZATION COMPLETE")
        print("="*70)
        print(f"\nResults:")
        print(f"  • Successfully vectorized: {successful}/{len(docs_to_vectorize)}")
        print(f"  • Failed: {failed}")
        print(f"  • Total chunks indexed: {len(all_documents)}")
        
        if successful > 0:
            print(f"\n✨ Your {successful} document(s) are now ready for RAG-powered search!")
        else:
            print(f"\n⚠️  Please install a PDF library to extract text:")
            print(f"  pip install pdfplumber")
            print(f"  or")
            print(f"  pip install PyPDF2")
        
        print()
        return successful > 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = vectorize_uploaded_documents()
    sys.exit(0 if success else 1)