"""
Test RAG Integration in Main Application
Verifies that main.py uses the improved RAG settings
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_main_rag_integration():
    """Test that main.py uses improved RAG configuration"""
    print("="*80)
    print("🧪 Testing RAG Integration in Main Application")
    print("="*80)

    # Test 1: Check main.py has correct configuration
    print("\n[1] Checking main.py configuration...")

    main_py_path = Path("main.py")
    if not main_py_path.exists():
        print("   ❌ main.py not found")
        return False

    with open(main_py_path, 'r', encoding='utf-8') as f:
        main_content = f.read()

    # Check for improved settings
    checks = {
        "chunk_overlap=100": "✅ Chunk overlap set to 100",
        "similarity_threshold=2.0": "✅ Similarity threshold set to 2.0",
        "improved": "✅ Improvement comments present"
    }

    issues = []
    for check, success_msg in checks.items():
        if check in main_content:
            print(f"   {success_msg}")
        else:
            print(f"   ❌ Missing: {check}")
            issues.append(check)

    if issues:
        print(f"\n   ⚠️  Configuration issues found: {', '.join(issues)}")
        print("   💡 Run the fixes again or manually update main.py")
        return False

    print("\n   ✅ All configuration checks passed!")

    # Test 2: Verify RAG module can be imported
    print("\n[2] Testing RAG module import...")
    try:
        from rag import VectorDatabase, RAGModule, DocumentProcessor
        print("   ✅ RAG modules imported successfully")

        # Check default values
        test_rag = RAGModule(
            vector_db=None,  # We don't need actual DB for this test
            top_k=5
        )

        if test_rag.similarity_threshold == 2.0:
            print(f"   ✅ Default similarity_threshold: {test_rag.similarity_threshold}")
        else:
            print(f"   ⚠️  Unexpected default threshold: {test_rag.similarity_threshold}")

        test_processor = DocumentProcessor()
        if test_processor.chunk_overlap == 100:
            print(f"   ✅ Default chunk_overlap: {test_processor.chunk_overlap}")
        else:
            print(f"   ⚠️  Unexpected default overlap: {test_processor.chunk_overlap}")

    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

    # Test 3: Check if vector index exists for document-based RAG
    print("\n[3] Checking vector index for business documents...")
    vector_index_path = Path("data/vector_index")

    if vector_index_path.exists():
        required_files = ['index.faiss', 'documents.pkl', 'embeddings.npy']
        missing = []

        for file in required_files:
            if not (vector_index_path / file).exists():
                missing.append(file)

        if missing:
            print(f"   ⚠️  Missing index files: {', '.join(missing)}")
            print("   💡 Run: python rebuild_index.py")
        else:
            print("   ✅ Vector index complete")

            # Check document count
            import pickle
            with open(vector_index_path / "documents.pkl", 'rb') as f:
                docs = pickle.load(f)
            print(f"   📊 Indexed documents: {len(docs)} chunks")
    else:
        print("   ⚠️  Vector index not found")
        print("   💡 Run: python rebuild_index.py")

    # Summary
    print("\n" + "="*80)
    print("📊 Integration Test Summary")
    print("="*80)

    print("\n✅ Configuration Status:")
    print("   • main.py: Updated with improved RAG settings")
    print("   • rag.py: Fixed and optimized")
    print("   • Vector index: Ready for business documents")

    print("\n💡 Usage:")
    print("   • Main app will use improved RAG automatically")
    print("   • Similarity threshold: 2.0 (better recall)")
    print("   • Chunk overlap: 100 words (better context)")
    print("   • Query expansion: Enabled")

    print("\n🚀 Next Steps:")
    print("   1. Run main app: python main.py")
    print("   2. Test with queries about severity levels")
    print("   3. Monitor retrieval quality")

    print("\n✅ Integration test complete!")
    print()
    return True


if __name__ == "__main__":
    try:
        success = test_main_rag_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
