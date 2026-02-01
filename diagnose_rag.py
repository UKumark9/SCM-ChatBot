"""
Comprehensive RAG Diagnostic Tool
Identifies and reports all issues with RAG retrieval
"""

import sys
import os
from pathlib import Path
import numpy as np

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def diagnose_rag():
    """Run comprehensive RAG diagnostics"""
    print("="*80)
    print("🔬 RAG SYSTEM DIAGNOSTIC TOOL")
    print("="*80)

    issues = []
    warnings = []
    successes = []

    # 1. Check dependencies
    print("\n[1] Checking dependencies...")
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        print("    ✅ Dependencies installed correctly")
        successes.append("Dependencies OK")
    except ImportError as e:
        print(f"    ❌ Missing dependency: {e}")
        issues.append(f"Missing dependency: {e}")
        return

    # 2. Check vector index
    print("\n[2] Checking vector index...")
    vector_index_path = Path("data/vector_index")

    if not vector_index_path.exists():
        print("    ❌ Vector index not found")
        issues.append("Vector index missing")
        return

    required_files = ['index.faiss', 'documents.pkl', 'embeddings.npy']
    for file in required_files:
        if not (vector_index_path / file).exists():
            print(f"    ❌ Missing file: {file}")
            issues.append(f"Missing index file: {file}")
        else:
            print(f"    ✅ Found {file}")

    # 3. Load and analyze index
    print("\n[3] Loading and analyzing vector index...")
    try:
        import pickle

        # Load documents
        with open(vector_index_path / "documents.pkl", 'rb') as f:
            documents = pickle.load(f)

        print(f"    ✅ Loaded {len(documents)} document chunks")
        successes.append(f"{len(documents)} chunks indexed")

        # Load embeddings
        with open(vector_index_path / "embeddings.npy", 'rb') as f:
            embeddings = np.load(f)

        print(f"    ✅ Embeddings shape: {embeddings.shape}")

        # Analyze document distribution
        doc_names = {}
        for doc in documents:
            name = doc.get('metadata', {}).get('doc_name', 'Unknown')
            doc_names[name] = doc_names.get(name, 0) + 1

        print(f"\n    📊 Document distribution:")
        for name, count in doc_names.items():
            print(f"       • {name}: {count} chunks")

    except Exception as e:
        print(f"    ❌ Error loading index: {e}")
        issues.append(f"Index loading error: {e}")
        return

    # 4. Check for severity content
    print("\n[4] Analyzing content for 'Severity Levels'...")
    severity_chunks = []
    severity_keywords = ['severity', 'critical delay', 'major delay', 'minor delay']

    for i, doc in enumerate(documents):
        text_lower = doc['text'].lower()
        if any(keyword in text_lower for keyword in severity_keywords):
            severity_chunks.append((i, doc))

    if severity_chunks:
        print(f"    ✅ Found {len(severity_chunks)} chunks with severity-related content")
        successes.append(f"{len(severity_chunks)} severity chunks found")

        print("\n    📄 Severity content preview:")
        for idx, doc in severity_chunks[:2]:
            doc_name = doc.get('metadata', {}).get('doc_name', 'Unknown')
            print(f"\n       Chunk {idx} from {doc_name}:")
            preview = doc['text'][:300].replace('\n', ' ')
            print(f"       {preview}...")
    else:
        print("    ⚠️  No severity-related content found in index")
        warnings.append("No severity content in index")

    # 5. Test embedding model
    print("\n[5] Testing embedding model...")
    try:
        from rag import VectorDatabase

        vector_db = VectorDatabase(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        )
        vector_db.initialize()
        print("    ✅ Embedding model initialized")

        # Test query embedding
        test_query = "What are severity levels?"
        query_embedding = vector_db.embedding_model.encode([test_query])
        print(f"    ✅ Query embedding shape: {query_embedding.shape}")

    except Exception as e:
        print(f"    ❌ Error with embedding model: {e}")
        issues.append(f"Embedding model error: {e}")
        return

    # 6. Test similarity search
    print("\n[6] Testing similarity search...")
    try:
        vector_db.load_index(str(vector_index_path))

        test_queries = [
            "Severity Levels",
            "Critical delay definition",
            "Major delay",
            "Delay classification"
        ]

        print("\n    🔍 Search results:")
        for query in test_queries:
            results = vector_db.search(query, top_k=3)

            print(f"\n       Query: \"{query}\"")
            if results:
                best_score = 1 / (1 + results[0][1])
                print(f"       Top result similarity: {best_score:.3f}")

                # Check if top result contains severity
                if 'severity' in results[0][0]['text'].lower():
                    print(f"       ✅ Top result contains severity content")
                    successes.append(f"Query '{query}' found severity content")
                else:
                    doc_name = results[0][0].get('metadata', {}).get('doc_name', 'Unknown')
                    print(f"       ⚠️  Top result: {doc_name} (no severity content)")
                    warnings.append(f"Query '{query}' didn't retrieve severity content")
            else:
                print(f"       ❌ No results")
                issues.append(f"No results for query: {query}")

    except Exception as e:
        print(f"    ❌ Search error: {e}")
        issues.append(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return

    # 7. Test with different similarity thresholds
    print("\n[7] Testing RAG module with different thresholds...")
    try:
        from rag import RAGModule

        thresholds = [0.5, 0.7, 1.0, 1.5, 2.0]
        query = "What are the severity levels for delays?"

        print(f"\n    Query: \"{query}\"")
        print(f"\n    {'Threshold':<12} {'Results':<10} {'Has Severity':<15}")
        print(f"    {'-'*40}")

        for threshold in thresholds:
            rag = RAGModule(vector_db=vector_db, top_k=5, similarity_threshold=threshold)
            context = rag.retrieve_context(query)

            has_severity = 'severity' in context.lower()
            result_count = len(context.split('---')) if context != "No relevant context found." else 0

            status = "✅" if has_severity else "❌"
            print(f"    {threshold:<12} {result_count:<10} {status}")

            if has_severity and threshold not in [0.7, 1.5]:
                successes.append(f"Threshold {threshold} retrieves severity content")

    except Exception as e:
        print(f"    ❌ RAG module error: {e}")
        issues.append(f"RAG module error: {e}")

    # 8. Summary
    print("\n" + "="*80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*80)

    print(f"\n✅ Successes ({len(successes)}):")
    for success in successes:
        print(f"   • {success}")

    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"   • {warning}")

    if issues:
        print(f"\n❌ Issues ({len(issues)}):")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print(f"\n✅ No critical issues found!")

    # 9. Recommendations
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)

    if len(severity_chunks) > 0 and warnings:
        print("\n1. SIMILARITY THRESHOLD TOO STRICT")
        print("   Problem: Documents contain severity content but aren't being retrieved")
        print("   Solution: Increase similarity_threshold in RAG module")
        print("   Current: 0.7 (test) / 1.5 (default)")
        print("   Recommended: 2.0 or higher for better recall")

    if doc_names:
        print("\n2. DOCUMENT CHUNKING")
        print("   Ensure important content isn't split across chunks")
        print("   Current chunk size: 500 words")
        print("   Consider: Semantic chunking or larger chunks for policy documents")

    print("\n3. QUERY FORMULATION")
    print("   Try different query variations:")
    print("   • 'delay severity classification'")
    print("   • 'critical major minor delay levels'")
    print("   • 'product delay management severity'")

    print("\n" + "="*80)
    print()

    return len(issues) == 0


if __name__ == "__main__":
    success = diagnose_rag()
    sys.exit(0 if success else 1)
