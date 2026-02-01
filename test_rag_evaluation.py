"""
Test RAG Evaluation Metrics
Demonstrates Context Relevance, Precision, and Recall calculation
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


def main():
    print("="*80)
    print("🧪 RAG EVALUATION METRICS TEST")
    print("="*80)

    # Load RAG system
    print("\n[1] Loading RAG system...")
    from rag import VectorDatabase, RAGModule
    from rag_evaluation import RAGEvaluator, evaluate_rag_system

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
    print(f"   ✅ Loaded {len(vector_db.documents)} documents")

    rag_module = RAGModule(vector_db=vector_db, top_k=5, similarity_threshold=2.0)
    print("   ✅ RAG module initialized")

    # Define test queries with ground truth
    print("\n[2] Preparing test queries...")

    test_queries = [
        {
            'query': 'What are severity levels for product delays?',
            'relevant_doc_ids': [
                # IDs of documents that contain severity level information
                # These would come from your actual document IDs
            ],
            'ground_truth_context': """
            Severity Levels:
            - Critical Delay: >5 business days beyond committed delivery date
            - Major Delay: 3-5 business days beyond committed delivery date
            - Minor Delay: 1-2 business days beyond committed delivery date
            - At-Risk: Products showing indicators of potential delay
            """,
            'expected_doc': '01_Product_Delay_Management_Policy.pdf'
        },
        {
            'query': 'Supplier quality management procedures',
            'relevant_doc_ids': [],
            'ground_truth_context': None,
            'expected_doc': '03_Supplier_Quality_Management_Policy.pdf'
        },
        {
            'query': 'Transportation and logistics policy',
            'relevant_doc_ids': [],
            'ground_truth_context': None,
            'expected_doc': '04_Transportation_Logistics_Policy.pdf'
        },
        {
            'query': 'Inventory management guidelines',
            'relevant_doc_ids': [],
            'ground_truth_context': None,
            'expected_doc': '02_Inventory_Management_Policy.pdf'
        }
    ]

    # Create evaluator
    evaluator = RAGEvaluator(vector_db, rag_module)

    # Test 1: Context Relevance
    print("\n[3] Testing Context Relevance...")
    print("="*80)

    for idx, test_case in enumerate(test_queries, 1):
        query = test_case['query']
        ground_truth = test_case.get('ground_truth_context')
        expected_doc = test_case.get('expected_doc')

        print(f"\nTest {idx}: \"{query}\"")
        print("-"*80)

        # Retrieve documents
        retrieved_docs = vector_db.search(query, top_k=5)

        # Evaluate context relevance
        relevance_metrics = evaluator.evaluate_context_relevance(
            query, retrieved_docs, ground_truth
        )

        print(f"📊 Relevance Metrics:")
        print(f"   Keyword Relevance:    {relevance_metrics['keyword_relevance']:.3f}")
        print(f"   Semantic Relevance:   {relevance_metrics['semantic_relevance']:.3f}")
        print(f"   Position-Weighted:    {relevance_metrics['position_weighted_relevance']:.3f}")

        if ground_truth:
            print(f"   Ground Truth Match:   {relevance_metrics.get('ground_truth_similarity', 0.0):.3f}")

        print(f"   Overall Relevance:    {relevance_metrics['overall_relevance']:.3f}")

        # Check if expected document was retrieved
        top_doc = retrieved_docs[0][0] if retrieved_docs else None
        if top_doc:
            doc_name = top_doc.get('metadata', {}).get('doc_name', 'Unknown')
            if expected_doc and expected_doc in doc_name:
                print(f"   ✅ Correct document retrieved: {doc_name}")
            else:
                print(f"   Top document: {doc_name}")

    # Test 2: Precision and Recall (with manual labeling)
    print("\n" + "="*80)
    print("[4] Testing Precision & Recall")
    print("="*80)

    # For demonstration, let's manually identify relevant docs for severity query
    print("\nDemo: Severity Levels Query")
    print("-"*80)

    severity_query = "What are the severity levels for delays?"
    retrieved_docs = vector_db.search(severity_query, top_k=5)

    # Manually identify which docs actually contain severity info
    relevant_doc_names = ['01_Product_Delay_Management_Policy.pdf']

    # Get IDs of relevant docs
    relevant_ids = []
    for doc in vector_db.documents:
        doc_name = doc.get('metadata', {}).get('doc_name', '')
        if any(rel_name in doc_name for rel_name in relevant_doc_names):
            doc_id = doc.get('id', '')
            if doc_id:
                relevant_ids.append(doc_id)

    print(f"Relevant Documents (ground truth): {len(relevant_ids)}")
    print(f"Retrieved Documents: {len(retrieved_docs)}")

    # Calculate precision and recall
    pr_metrics = evaluator.evaluate_retrieval_precision_recall(
        severity_query,
        retrieved_docs,
        relevant_ids,
        k=5
    )

    print(f"\n📊 Precision & Recall Metrics:")
    print(f"   Precision@5:          {pr_metrics['precision_at_k']:.3f}")
    print(f"   Recall@5:             {pr_metrics['recall_at_k']:.3f}")
    print(f"   F1 Score:             {pr_metrics['f1_score']:.3f}")
    print(f"   Mean Reciprocal Rank: {pr_metrics['mean_reciprocal_rank']:.3f}")
    print(f"   Average Precision:    {pr_metrics['average_precision']:.3f}")

    print(f"\n   True Positives:       {pr_metrics['true_positives']}")
    print(f"   False Positives:      {pr_metrics['false_positives']}")
    print(f"   False Negatives:      {pr_metrics['false_negatives']}")

    # Test 3: NDCG (with manual relevance scores)
    print("\n" + "="*80)
    print("[5] Testing NDCG (Normalized Discounted Cumulative Gain)")
    print("="*80)

    # Manually score relevance of each retrieved doc (0-3 scale)
    # 3 = highly relevant, 2 = relevant, 1 = somewhat relevant, 0 = not relevant

    print("\nManual relevance scoring for retrieved docs:")
    manual_scores = []

    for idx, (doc, distance) in enumerate(retrieved_docs[:5], 1):
        doc_name = doc.get('metadata', {}).get('doc_name', 'Unknown')
        similarity = 1 / (1 + distance)

        # Simple heuristic: if doc name matches expected, score 3, else use similarity
        if '01_Product_Delay_Management_Policy' in doc_name:
            score = 3
        elif 'delay' in doc.get('text', '').lower()[:500]:
            score = 2
        elif similarity > 0.5:
            score = 1
        else:
            score = 0

        manual_scores.append(score)
        print(f"   Doc {idx}: {doc_name[:40]:40s} | Relevance: {score}")

    ndcg = evaluator.evaluate_ndcg(severity_query, retrieved_docs, manual_scores, k=5)
    print(f"\n   NDCG@5: {ndcg:.3f}")

    # Test 4: Comprehensive Evaluation
    print("\n" + "="*80)
    print("[6] Running Comprehensive Evaluation")
    print("="*80)

    # Prepare test queries for comprehensive eval
    comprehensive_test_queries = [
        {
            'query': 'What are severity levels for product delays?',
            'relevant_doc_ids': relevant_ids,
            'ground_truth_context': """
            Severity Levels:
            - Critical Delay: >5 business days
            - Major Delay: 3-5 business days
            - Minor Delay: 1-2 business days
            """
        },
        {
            'query': 'Supplier quality procedures',
            'relevant_doc_ids': [],  # Would need to identify these
        },
        {
            'query': 'Transportation logistics policy',
            'relevant_doc_ids': [],
        }
    ]

    results = evaluator.comprehensive_evaluation(comprehensive_test_queries)

    # Generate and display report
    report = evaluator.generate_evaluation_report(results)
    print(report)

    # Save results
    evaluator.save_evaluation_results(results, "data/rag_evaluation_results.json")
    print("✅ Results saved to: data/rag_evaluation_results.json")

    # Summary
    print("\n" + "="*80)
    print("📊 EVALUATION SUMMARY")
    print("="*80)

    metrics = results['aggregate_metrics']

    print(f"\n✅ Context Relevance:  {metrics['mean_context_relevance']:.3f}")
    print(f"✅ Precision@5:        {metrics['mean_precision']:.3f}")
    print(f"✅ Recall@5:           {metrics['mean_recall']:.3f}")
    print(f"✅ F1 Score:           {metrics['mean_f1_score']:.3f}")
    print(f"✅ MRR:                {metrics['mean_mrr']:.3f}")

    # Interpretation
    avg_score = (metrics['mean_context_relevance'] + metrics['mean_precision'] +
                 metrics['mean_recall']) / 3

    print(f"\n📈 Overall RAG Quality Score: {avg_score:.3f}")

    if avg_score >= 0.7:
        print("   🌟 EXCELLENT - RAG system performing very well!")
    elif avg_score >= 0.5:
        print("   ✅ GOOD - RAG system performing well")
    else:
        print("   ⚠️  FAIR - RAG system may need tuning")

    print("\n" + "="*80)
    print()

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
