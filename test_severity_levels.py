"""
Test RAG Response for Specific Query
Check if RAG can retrieve content about "Severity Levels"
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

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_rag_retrieval_for_severity_levels():
    """Test RAG retrieval specifically for 'Severity Levels' content"""
    try:
        print("="*70)
        print("🔍 Testing RAG Retrieval for 'Severity Levels'")
        print("="*70)

        # Step 1: Check dependencies
        print("\n1. Checking dependencies...")
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            print("   ✅ All dependencies available")
        except ImportError as e:
            print(f"   ❌ Missing dependency: {e}")
            return False

        # Step 2: Load vector index
        print("\n2. Loading vector index...")
        from rag import VectorDatabase, RAGModule
        
        vector_index_path = Path("data/vector_index")
        
        if not vector_index_path.exists():
            print(f"   ⚠️  Vector index not found at {vector_index_path}")
            print("   Please run: python vectorize_documents.py")
            return False
        
        vector_db = VectorDatabase(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        )
        vector_db.initialize()
        
        try:
            vector_db.load_index(str(vector_index_path))
            print(f"   ✅ Index loaded with {len(vector_db.documents)} documents")
        except Exception as e:
            print(f"   ❌ Error loading index: {e}")
            return False

        # Step 3: Create RAG module
        print("\n3. Initializing RAG module...")
        rag_module = RAGModule(
            vector_db=vector_db,
            top_k=5,
            similarity_threshold=2.0  # Increased for better recall
        )
        print(f"   ✅ RAG module initialized (threshold: 2.0)")

        # Step 4: Test queries
        print("\n4. Testing RAG retrieval...")

        test_queries = [
            "Severity Levels",
            "What are severity levels?",
            "Critical delay and major delay definitions",
            "Delay classification categories",
            "Product delay management severity",
            "What defines different severity levels?"
        ]

        all_results = {}
        found_severity = False
        query_success_count = 0

        for query in test_queries:
            print(f"\n   Query: \"{query}\"")
            print(f"   {'-'*60}")

            try:
                # Use RAG module retrieve_context for better results
                context = rag_module.retrieve_context(query, use_query_expansion=True)

                if context == "No relevant context found.":
                    print(f"   ⚠️  No relevant context found")
                    continue

                # Also get raw search results for analysis
                results = vector_db.search(query, top_k=5)

                if not results:
                    print(f"   ⚠️  No results found")
                    continue

                # Check if results contain severity
                query_found_severity = False
                for idx, (doc, distance) in enumerate(results, 1):
                    # Calculate similarity score (inverse of distance)
                    similarity = 1 / (1 + distance)
                    doc_text = doc['text'][:200].replace('\n', ' ')

                    # Check if this contains "Severity"
                    contains_severity = 'severity' in doc['text'].lower()
                    if contains_severity:
                        query_found_severity = True
                        found_severity = True

                    status = "✅" if contains_severity else "  "
                    print(f"\n   [{idx}] Similarity: {similarity:.3f} {status}")
                    print(f"       Document: {doc.get('metadata', {}).get('doc_name', 'Unknown')}")
                    print(f"       Type: {doc.get('type', 'unknown')}")
                    print(f"       Text preview: {doc_text}...")

                if query_found_severity:
                    query_success_count += 1
                    print(f"\n   ✅ Query successfully retrieved severity content!")

                all_results[query] = results

            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()

        # Step 5: Summary
        print("\n" + "="*70)
        print("📊 Test Summary")
        print("="*70)

        success_rate = (query_success_count / len(test_queries)) * 100 if test_queries else 0

        print(f"\nQueries tested: {len(test_queries)}")
        print(f"Successful retrievals: {query_success_count}")
        print(f"Success rate: {success_rate:.1f}%")

        if found_severity and success_rate >= 50:
            print("\n✅ SUCCESS! RAG system is working well")
            print("\nRelevant documents retrieved:")
            seen_docs = set()
            for query, results in all_results.items():
                for doc, distance in results:
                    if 'severity' in doc['text'].lower():
                        doc_name = doc.get('metadata', {}).get('doc_name', 'Unknown')
                        if doc_name not in seen_docs:
                            similarity = 1 / (1 + distance)
                            print(f"  • {doc_name} (similarity: {similarity:.3f})")
                            seen_docs.add(doc_name)

            print("\n💡 Tips for better results:")
            print("  • Use specific terms like 'critical delay' or 'major delay'")
            print("  • Include context like 'product delay management'")
            print("  • Query expansion is enabled automatically")

        elif found_severity:
            print("\n⚠️  PARTIAL SUCCESS - Some queries found severity content")
            print(f"\nOnly {query_success_count}/{len(test_queries)} queries succeeded")
            print("\nTips to improve:")
            print("  • Adjust similarity threshold (current: 2.0)")
            print("  • Try different query formulations")
            print("  • Enable query expansion")

        else:
            print("\n❌ RAG did not find 'Severity Levels' content")
            print("\nPossible reasons:")
            print("  1. Documents don't contain 'Severity Levels' text")
            print("  2. Vector embeddings not yet built from documents")
            print("  3. Similarity threshold is too high")

            print("\nDocuments in index:")
            for doc in vector_db.documents[:10]:
                doc_name = doc.get('metadata', {}).get('doc_name', 'Unknown')
                print(f"  • {doc_name}")

        print()
        return found_severity and success_rate >= 50

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rag_retrieval_for_severity_levels()
    sys.exit(0 if success else 1)