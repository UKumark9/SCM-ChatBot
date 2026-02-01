"""
Comprehensive RAG System Test
Demonstrates end-to-end RAG retrieval with actual content display
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


def test_rag_comprehensive():
    """Comprehensive RAG system test"""
    try:
        print("="*80)
        print("🧪 Comprehensive RAG System Test")
        print("="*80)

        # 1. Load RAG system
        print("\n[1] Loading RAG system...")
        from rag import VectorDatabase, RAGModule

        vector_db = VectorDatabase(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        )
        vector_db.initialize()

        vector_index_path = Path("data/vector_index")
        if not vector_index_path.exists():
            print("   ❌ Vector index not found. Run: python rebuild_index.py")
            return False

        vector_db.load_index(str(vector_index_path))
        print(f"   ✅ Loaded {len(vector_db.documents)} document chunks")

        # 2. Create RAG module with optimized settings
        print("\n[2] Initializing RAG module...")
        rag = RAGModule(
            vector_db=vector_db,
            top_k=5,
            similarity_threshold=2.0  # Optimized threshold
        )
        print("   ✅ RAG module ready")

        # 3. Test specific queries
        print("\n[3] Testing RAG retrieval with various queries...")
        print("="*80)

        test_cases = [
            {
                "query": "What are the severity levels for product delays?",
                "expected_content": ["critical delay", "major delay", "minor delay"],
                "use_expansion": True
            },
            {
                "query": "Critical delay definition",
                "expected_content": ["5 business days", "critical"],
                "use_expansion": False
            },
            {
                "query": "Delay classification",
                "expected_content": ["severity"],
                "use_expansion": True
            }
        ]

        total_tests = len(test_cases)
        passed_tests = 0

        for idx, test_case in enumerate(test_cases, 1):
            query = test_case["query"]
            expected = test_case["expected_content"]
            use_expansion = test_case["use_expansion"]

            print(f"\n{'='*80}")
            print(f"Test Case {idx}/{total_tests}")
            print(f"{'='*80}")
            print(f"\n📝 Query: \"{query}\"")
            print(f"🔍 Query Expansion: {'Enabled' if use_expansion else 'Disabled'}")
            print(f"✓ Expected to find: {', '.join(expected)}")

            # Retrieve context
            context = rag.retrieve_context(query, use_query_expansion=use_expansion)

            print(f"\n📄 Retrieved Context:")
            print("-"*80)

            if context == "No relevant context found.":
                print("❌ No relevant context found!")
                print("\nTest Result: ❌ FAILED\n")
                continue

            # Display context
            print(context[:1000])  # Show first 1000 chars
            if len(context) > 1000:
                print(f"\n... [truncated, total length: {len(context)} characters]")

            # Check if expected content is present
            context_lower = context.lower()
            found_items = []
            missing_items = []

            for item in expected:
                if item.lower() in context_lower:
                    found_items.append(item)
                else:
                    missing_items.append(item)

            # Evaluate test
            print(f"\n📊 Evaluation:")
            print(f"   Found: {', '.join(found_items) if found_items else 'None'}")
            if missing_items:
                print(f"   Missing: {', '.join(missing_items)}")

            test_passed = len(found_items) > 0
            if test_passed:
                passed_tests += 1
                print(f"\n✅ Test Result: PASSED ({len(found_items)}/{len(expected)} items found)")
            else:
                print(f"\n❌ Test Result: FAILED (0/{len(expected)} items found)")

        # 4. Demonstrate actual severity levels retrieval
        print(f"\n{'='*80}")
        print("🎯 Demonstrating Actual Severity Levels Retrieval")
        print("="*80)

        severity_query = "product delay severity levels critical major minor"
        print(f"\n📝 Query: \"{severity_query}\"")

        results = vector_db.search(severity_query, top_k=3)

        for idx, (doc, distance) in enumerate(results, 1):
            similarity = 1 / (1 + distance)
            doc_name = doc.get('metadata', {}).get('doc_name', 'Unknown')

            print(f"\n[{idx}] Document: {doc_name}")
            print(f"    Similarity: {similarity:.3f}")
            print(f"    Content Preview:")
            print("-"*80)

            # Show relevant excerpt
            text = doc['text']
            if 'severity' in text.lower():
                # Find severity section
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'severity' in line.lower():
                        # Show context around severity mention
                        start = max(0, i-2)
                        end = min(len(lines), i+8)
                        excerpt = '\n'.join(lines[start:end])
                        print(excerpt)
                        break
            else:
                print(text[:400])

        # 5. Summary
        print(f"\n{'='*80}")
        print("📊 FINAL SUMMARY")
        print("="*80)

        success_rate = (passed_tests / total_tests) * 100
        print(f"\nTests Passed: {passed_tests}/{total_tests} ({success_rate:.0f}%)")

        if success_rate >= 66:
            print("\n✅ RAG SYSTEM IS WORKING WELL!")
            print("\n✨ Improvements Applied:")
            print("   • Similarity threshold optimized to 2.0")
            print("   • Chunk overlap increased to 100 words")
            print("   • Semantic paragraph-aware chunking")
            print("   • Query expansion enabled")
            print("   • Better context preservation")

            print("\n💡 Usage Tips:")
            print("   • Use specific terms for better results")
            print("   • Include domain context (e.g., 'product delay management')")
            print("   • Query expansion helps with variations")

        elif success_rate >= 33:
            print("\n⚠️  RAG SYSTEM PARTIALLY WORKING")
            print("\n📝 Recommendations:")
            print("   • Try more specific queries")
            print("   • Adjust similarity threshold if needed")
            print("   • Enable query expansion")

        else:
            print("\n❌ RAG SYSTEM NEEDS ATTENTION")
            print("\n📝 Troubleshooting:")
            print("   • Rebuild index: python rebuild_index.py")
            print("   • Check document content")
            print("   • Verify embeddings are correct")

        print()
        return success_rate >= 50

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rag_comprehensive()
    sys.exit(0 if success else 1)
