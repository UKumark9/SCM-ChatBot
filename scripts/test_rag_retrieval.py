"""
Test RAG Document Retrieval
Diagnose why specific documents aren't being retrieved
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def check_uploaded_documents():
    """Check what documents are uploaded"""
    try:
        from document_manager import DocumentManager

        print("="*70)
        print("📚 Checking Uploaded Documents")
        print("="*70)

        dm = DocumentManager(docs_path="data/business_docs")

        # Get all documents
        all_docs = dm.list_documents()

        if not all_docs:
            print("\n⚠️  NO DOCUMENTS UPLOADED!")
            print("\nTo upload documents:")
            print("1. Open UI: http://localhost:7860")
            print("2. Go to 'Documents' tab")
            print("3. Upload your PDF/DOCX/TXT files")
            return False

        print(f"\n✅ Found {len(all_docs)} uploaded document(s):\n")

        for doc in all_docs:
            print(f"📄 {doc['original_name']}")
            print(f"   • Type: {doc['file_type']}")
            print(f"   • Category: {doc['doc_type']}")
            print(f"   • Size: {doc['size_bytes']:,} bytes")
            print(f"   • Vectorized: {'✅ Yes' if doc.get('vectorized') else '❌ No'}")
            print(f"   • Upload Date: {doc['upload_date'][:19]}")
            print()

        return True

    except Exception as e:
        print(f"❌ Error checking documents: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_rag_initialization():
    """Check if RAG is properly initialized"""
    try:
        print("\n" + "="*70)
        print("🔍 Checking RAG Initialization")
        print("="*70)

        # Check dependencies
        print("\n1. Checking dependencies...")
        try:
            from sentence_transformers import SentenceTransformer
            print("   ✅ sentence-transformers installed")
        except ImportError:
            print("   ❌ sentence-transformers NOT installed")
            print("   Install: pip install sentence-transformers")
            return False

        try:
            import faiss
            print("   ✅ faiss installed")
        except ImportError:
            print("   ❌ faiss NOT installed")
            print("   Install: pip install faiss-cpu")
            return False

        # Check RAG module
        print("\n2. Checking RAG module...")
        from rag import DocumentProcessor, VectorDatabase, RAGModule

        print("   ✅ RAG module can be imported")

        return True

    except Exception as e:
        print(f"❌ RAG initialization check failed: {e}")
        return False


def test_rag_search(query: str = "approved purchasing procedures"):
    """Test RAG search for specific query"""
    try:
        print("\n" + "="*70)
        print("🔎 Testing RAG Search")
        print("="*70)

        print(f"\n📝 Test Query: \"{query}\"")

        # Initialize RAG with uploaded documents
        from rag import DocumentProcessor, VectorDatabase, RAGModule
        from document_manager import DocumentManager

        dm = DocumentManager(docs_path="data/business_docs")

        # Check if there are uploaded documents
        docs = dm.list_documents()
        if not docs:
            print("\n❌ No documents to search!")
            print("   Please upload documents first.")
            return False

        print(f"\n✅ {len(docs)} documents available for search")

        # Try to initialize RAG (simplified test)
        print("\n🔨 Testing vector search...")

        # Create a simple test
        doc_processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)

        # Create test documents from uploaded files
        test_documents = []
        for doc in docs[:5]:  # Test with first 5 docs
            test_documents.append({
                'id': doc['id'],
                'text': f"Document: {doc['original_name']} - {doc.get('description', '')}",
                'type': 'document',
                'metadata': doc
            })

        if not test_documents:
            print("❌ No documents to test with")
            return False

        print(f"✅ Created {len(test_documents)} test documents")

        # Initialize vector DB
        vector_db = VectorDatabase(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        )

        print("🔄 Initializing embedding model (this may take a moment)...")
        vector_db.initialize()

        print("🔄 Building vector index...")
        vector_db.build_index(test_documents)

        # Search
        print(f"\n🔍 Searching for: \"{query}\"")
        results = vector_db.search(query, top_k=5)

        if not results:
            print("\n❌ NO RESULTS FOUND!")
            print("\nPossible reasons:")
            print("1. Query doesn't match document content")
            print("2. Document not uploaded or vectorized")
            print("3. Similarity threshold too high")
            return False

        print(f"\n✅ Found {len(results)} results:")
        for i, (doc, distance) in enumerate(results, 1):
            similarity = 1 / (1 + distance)
            print(f"\n{i}. Similarity: {similarity:.3f} (distance: {distance:.3f})")
            print(f"   Document: {doc.get('text', 'N/A')[:200]}...")

        return True

    except Exception as e:
        print(f"\n❌ RAG search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test complete RAG pipeline with actual system"""
    try:
        print("\n" + "="*70)
        print("🔬 Testing Full RAG Pipeline")
        print("="*70)

        # This requires the main app to be set up
        print("\nℹ️  This test requires the application to be running.")
        print("   To test manually:")
        print("   1. Start app: python main.py")
        print("   2. Ask query in UI")
        print("   3. Check if RAG is used (footer shows 'Agent + RAG')")

    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")


def main():
    """Run all RAG diagnostics"""
    print("="*70)
    print("🧪 RAG Retrieval Diagnostics")
    print("="*70)

    # Step 1: Check uploaded documents
    has_docs = check_uploaded_documents()

    # Step 2: Check RAG initialization
    rag_ok = check_rag_initialization()

    # Step 3: Test RAG search (only if deps available)
    if rag_ok and has_docs:
        test_rag_search("approved purchasing procedures")
    else:
        print("\n⚠️  Skipping RAG search test (missing dependencies or documents)")

    # Step 4: Guidance
    test_full_pipeline()

    print("\n" + "="*70)
    print("📋 Summary")
    print("="*70)
    print(f"Documents Uploaded: {'✅ Yes' if has_docs else '❌ No'}")
    print(f"RAG Dependencies: {'✅ OK' if rag_ok else '❌ Missing'}")

    if not has_docs:
        print("\n💡 Next Steps:")
        print("1. Upload 'approved purchasing procedures' document:")
        print("   - Open UI: http://localhost:7860")
        print("   - Go to 'Documents' tab")
        print("   - Upload your PDF/DOCX/TXT file")
        print("   - Category: 'Policy' or 'Procedure'")
        print("   - Description: 'Approved purchasing procedures'")
        print("\n2. Restart app to re-index:")
        print("   - Stop app (Ctrl+C)")
        print("   - Run: python main.py")
        print("\n3. Test query:")
        print("   - Ask: 'What are the approved purchasing procedures?'")
        print("   - Check footer for 'Agent + RAG'")

    elif not rag_ok:
        print("\n💡 Next Steps:")
        print("1. Install RAG dependencies:")
        print("   pip install sentence-transformers faiss-cpu")
        print("\n2. Restart app:")
        print("   python main.py")

    else:
        print("\n✅ RAG system appears functional!")
        print("\n💡 If still not retrieving:")
        print("1. Check query matches document content")
        print("2. Try broader queries: 'purchasing', 'procurement', 'approval'")
        print("3. Lower similarity threshold in rag.py (currently 0.7)")


if __name__ == "__main__":
    main()
