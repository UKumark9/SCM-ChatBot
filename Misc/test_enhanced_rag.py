"""
Test Enhanced RAG System
Compares basic RAG vs Enhanced RAG with re-ranking, compression, and hybrid search
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path (works from any subdirectory)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from rag import VectorDatabase, RAGModule
from enhanced_rag import EnhancedVectorDatabase, EnhancedRAGModule
import time


def test_rag_comparison():
    print("="*80)
    print("🧪 Enhanced RAG System Test - Basic vs Enhanced")
    print("="*80)

    # Test queries
    test_queries = [
        "What are severity levels?",
        "Define critical delay",
        "What are the delay management procedures?",
        "Supplier quality requirements"
    ]

    vector_index_path = Path("data/vector_index")
    if not vector_index_path.exists():
        print("❌ Vector index not found. Run: python rebuild_index.py")
        return False

    # ========================================================================
    # BASIC RAG SYSTEM
    # ========================================================================
    print("\n" + "="*80)
    print("📊 BASIC RAG SYSTEM (Baseline)")
    print("="*80)

    print("\n[1] Loading basic RAG system...")
    basic_vdb = VectorDatabase()
    basic_vdb.initialize()
    basic_vdb.load_index(str(vector_index_path))
    basic_rag = RAGModule(vector_db=basic_vdb, top_k=5, similarity_threshold=2.0)
    print(f"   ✅ Loaded {len(basic_vdb.documents)} chunks")

    basic_results = {}
    for idx, query in enumerate(test_queries, 1):
        print(f"\n[{idx}] Query: \"{query}\"")
        print("-"*80)

        start_time = time.time()
        context = basic_rag.retrieve_context(query)
        elapsed = (time.time() - start_time) * 1000

        # Count results
        num_results = context.count('[Relevance:')
        has_severity = 'Severity Levels' in context or 'severity' in context.lower()

        print(f"   Results: {num_results} documents")
        print(f"   Time: {elapsed:.0f}ms")
        print(f"   Contains target: {has_severity}")
        print(f"   Context length: {len(context)} chars")

        basic_results[query] = {
            'num_results': num_results,
            'time_ms': elapsed,
            'has_target': has_severity,
            'context_length': len(context),
            'preview': context[:300]
        }

    # ========================================================================
    # ENHANCED RAG SYSTEM
    # ========================================================================
    print("\n\n" + "="*80)
    print("✨ ENHANCED RAG SYSTEM (Re-ranking + Compression + Hybrid)")
    print("="*80)

    print("\n[1] Loading enhanced RAG system...")
    enhanced_vdb = EnhancedVectorDatabase()
    enhanced_vdb.initialize()
    enhanced_vdb.load_index(str(vector_index_path))
    enhanced_rag = EnhancedRAGModule(
        vector_db=enhanced_vdb,
        top_k=5,
        similarity_threshold=2.0,
        enable_reranking=True,
        enable_compression=True
    )
    print(f"   ✅ Loaded {len(enhanced_vdb.documents)} chunks")
    print("   ✅ Re-ranking enabled (cross-encoder)")
    print("   ✅ Contextual compression enabled")
    print("   ✅ Hybrid search enabled (Vector + BM25)")

    enhanced_results = {}
    for idx, query in enumerate(test_queries, 1):
        print(f"\n[{idx}] Query: \"{query}\"")
        print("-"*80)

        start_time = time.time()
        context = enhanced_rag.retrieve_context(
            query,
            use_query_expansion=True,
            use_hybrid=True,
            alpha=0.5  # Balanced hybrid search
        )
        elapsed = (time.time() - start_time) * 1000

        # Count results
        num_results = context.count('[Relevance:')
        has_severity = 'Severity Levels' in context or 'severity' in context.lower()

        print(f"   Results: {num_results} documents")
        print(f"   Time: {elapsed:.0f}ms")
        print(f"   Contains target: {has_severity}")
        print(f"   Context length: {len(context)} chars")

        # Token savings
        token_savings = (1 - len(context) / basic_results[query]['context_length']) * 100 if query in basic_results else 0

        print(f"   Token savings: {token_savings:.1f}%")

        enhanced_results[query] = {
            'num_results': num_results,
            'time_ms': elapsed,
            'has_target': has_severity,
            'context_length': len(context),
            'token_savings': token_savings,
            'preview': context[:300]
        }

    # ========================================================================
    # COMPARISON SUMMARY
    # ========================================================================
    print("\n\n" + "="*80)
    print("📊 COMPARISON SUMMARY")
    print("="*80)

    print("\n" + "="*80)
    print("Query-by-Query Comparison:")
    print("="*80)

    for query in test_queries:
        basic = basic_results.get(query, {})
        enhanced = enhanced_results.get(query, {})

        print(f"\n📝 \"{query}\"")
        print("-"*80)

        # Time comparison
        time_diff = enhanced.get('time_ms', 0) - basic.get('time_ms', 0)
        time_change = "+" if time_diff > 0 else ""
        print(f"Time:    {basic.get('time_ms', 0):.0f}ms → {enhanced.get('time_ms', 0):.0f}ms ({time_change}{time_diff:.0f}ms)")

        # Context length comparison
        basic_len = basic.get('context_length', 0)
        enhanced_len = enhanced.get('context_length', 0)
        savings = (1 - enhanced_len / basic_len) * 100 if basic_len > 0 else 0
        print(f"Context: {basic_len} → {enhanced_len} chars ({savings:.1f}% reduction)")

        # Target presence
        basic_target = "✅" if basic.get('has_target') else "❌"
        enhanced_target = "✅" if enhanced.get('has_target') else "❌"
        print(f"Target:  {basic_target} → {enhanced_target}")

    # Overall statistics
    print("\n" + "="*80)
    print("Overall Statistics:")
    print("="*80)

    total_basic_time = sum(r['time_ms'] for r in basic_results.values())
    total_enhanced_time = sum(r['time_ms'] for r in enhanced_results.values())
    avg_token_savings = sum(r['token_savings'] for r in enhanced_results.values()) / len(enhanced_results)

    basic_target_found = sum(1 for r in basic_results.values() if r['has_target'])
    enhanced_target_found = sum(1 for r in enhanced_results.values() if r['has_target'])

    print(f"\nAverage Time:")
    print(f"  Basic:    {total_basic_time / len(basic_results):.0f}ms")
    print(f"  Enhanced: {total_enhanced_time / len(enhanced_results):.0f}ms")

    print(f"\nAverage Token Savings:")
    print(f"  {avg_token_savings:.1f}% reduction in context length")

    print(f"\nTarget Found:")
    print(f"  Basic:    {basic_target_found}/{len(test_queries)}")
    print(f"  Enhanced: {enhanced_target_found}/{len(test_queries)}")

    # ========================================================================
    # DETAILED EXAMPLE
    # ========================================================================
    print("\n\n" + "="*80)
    print("📄 DETAILED EXAMPLE - Context Compression")
    print("="*80)

    example_query = test_queries[0]  # "What are severity levels?"

    print(f"\nQuery: \"{example_query}\"")
    print("\n" + "-"*80)
    print("BASIC RAG (Full Chunks):")
    print("-"*80)
    print(basic_results[example_query]['preview'])
    print(f"... ({basic_results[example_query]['context_length']} total chars)")

    print("\n" + "-"*80)
    print("ENHANCED RAG (Compressed - Relevant Sentences Only):")
    print("-"*80)
    print(enhanced_results[example_query]['preview'])
    print(f"... ({enhanced_results[example_query]['context_length']} total chars)")

    # ========================================================================
    # VERDICT
    # ========================================================================
    print("\n\n" + "="*80)
    print("🎯 VERDICT")
    print("="*80)

    if avg_token_savings > 20:
        print(f"\n✅ Contextual Compression: SIGNIFICANT IMPROVEMENT ({avg_token_savings:.0f}% token reduction)")
    elif avg_token_savings > 10:
        print(f"\n✅ Contextual Compression: MODERATE IMPROVEMENT ({avg_token_savings:.0f}% token reduction)")
    else:
        print(f"\n⚠️  Contextual Compression: MINOR IMPROVEMENT ({avg_token_savings:.0f}% token reduction)")

    if enhanced_target_found >= basic_target_found:
        print("✅ Target Retrieval: MAINTAINED OR IMPROVED")
    else:
        print("⚠️  Target Retrieval: DECREASED (may need tuning)")

    time_overhead = ((total_enhanced_time - total_basic_time) / total_basic_time) * 100
    if time_overhead < 20:
        print(f"✅ Performance Overhead: ACCEPTABLE (+{time_overhead:.0f}% latency)")
    else:
        print(f"⚠️  Performance Overhead: HIGH (+{time_overhead:.0f}% latency)")

    print("\n" + "="*80)
    print("✨ Enhanced RAG Features:")
    print("="*80)
    print("1. ✅ Re-ranking with cross-encoder (improves relevance)")
    print("2. ✅ Contextual compression (reduces tokens)")
    print("3. ✅ Hybrid search (combines vector + keyword matching)")
    print("4. ✅ Enhanced query expansion (better semantic coverage)")
    print("\n" + "="*80)

    return True


if __name__ == "__main__":
    try:
        success = test_rag_comparison()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
