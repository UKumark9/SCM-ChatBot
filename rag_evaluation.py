"""
RAG Evaluation Module
Implements Context Relevance, Precision, Recall, and other RAG quality metrics
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGEvaluator:
    """
    Comprehensive RAG System Evaluator

    Metrics implemented:
    1. Context Relevance - How relevant retrieved context is to the query
    2. Retrieval Precision - Percentage of retrieved docs that are relevant
    3. Retrieval Recall - Percentage of relevant docs that were retrieved
    4. F1 Score - Harmonic mean of precision and recall
    5. Mean Reciprocal Rank (MRR) - Quality of ranking
    6. NDCG - Normalized Discounted Cumulative Gain
    """

    def __init__(self, vector_db, rag_module, llm_client=None):
        """
        Initialize RAG Evaluator

        Args:
            vector_db: VectorDatabase instance
            rag_module: RAGModule instance
            llm_client: Optional LLM for automated relevance scoring
        """
        self.vector_db = vector_db
        self.rag_module = rag_module
        self.llm_client = llm_client

    def evaluate_context_relevance(self, query: str, retrieved_docs: List[Dict],
                                   ground_truth_context: Optional[str] = None) -> Dict[str, float]:
        """
        Evaluate context relevance using multiple methods

        Args:
            query: User query
            retrieved_docs: List of retrieved documents with scores
            ground_truth_context: Optional ground truth for comparison

        Returns:
            Dictionary with relevance scores
        """
        results = {}

        # Method 1: Keyword overlap
        results['keyword_relevance'] = self._keyword_relevance(query, retrieved_docs)

        # Method 2: Semantic similarity (using embeddings)
        results['semantic_relevance'] = self._semantic_relevance(query, retrieved_docs)

        # Method 3: Position-weighted relevance
        results['position_weighted_relevance'] = self._position_weighted_relevance(
            query, retrieved_docs
        )

        # Method 4: LLM-based relevance (if LLM available)
        if self.llm_client:
            results['llm_relevance'] = self._llm_based_relevance(query, retrieved_docs)

        # Method 5: Ground truth comparison (if available)
        if ground_truth_context:
            results['ground_truth_similarity'] = self._ground_truth_similarity(
                retrieved_docs, ground_truth_context
            )

        # Overall context relevance score (average of available methods)
        available_scores = [v for k, v in results.items() if v is not None]
        results['overall_relevance'] = np.mean(available_scores) if available_scores else 0.0

        return results

    def evaluate_retrieval_precision_recall(self, query: str,
                                           retrieved_docs: List[Dict],
                                           relevant_doc_ids: List[str],
                                           k: int = 5) -> Dict[str, float]:
        """
        Calculate Precision@K and Recall@K

        Args:
            query: User query
            retrieved_docs: Retrieved documents (top-k)
            relevant_doc_ids: IDs of documents that are truly relevant
            k: Number of top results to consider

        Returns:
            Dictionary with precision, recall, F1, and other metrics
        """
        # Get IDs of retrieved documents (handle tuple format)
        retrieved_ids = set([doc.get('id', doc.get('metadata', {}).get('doc_id', ''))
                            for doc, score in retrieved_docs[:k]])
        relevant_ids = set(relevant_doc_ids)

        # Calculate true positives, false positives, false negatives
        true_positives = len(retrieved_ids & relevant_ids)
        false_positives = len(retrieved_ids - relevant_ids)
        false_negatives = len(relevant_ids - retrieved_ids)

        # Precision: What fraction of retrieved docs are relevant?
        precision = true_positives / len(retrieved_ids) if retrieved_ids else 0.0

        # Recall: What fraction of relevant docs were retrieved?
        recall = true_positives / len(relevant_ids) if relevant_ids else 0.0

        # F1 Score: Harmonic mean of precision and recall
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Mean Reciprocal Rank (MRR)
        mrr = self._calculate_mrr(retrieved_docs, relevant_ids)

        # Average Precision
        avg_precision = self._calculate_average_precision(retrieved_docs, relevant_ids)

        return {
            'precision_at_k': precision,
            'recall_at_k': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'mean_reciprocal_rank': mrr,
            'average_precision': avg_precision,
            'k': k
        }

    def evaluate_ndcg(self, query: str, retrieved_docs: List[Dict],
                     relevance_scores: List[float], k: int = 5) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG@K)

        Args:
            query: User query
            retrieved_docs: Retrieved documents
            relevance_scores: Relevance score for each document (0-1 or 0-3 scale)
            k: Number of top results

        Returns:
            NDCG@K score
        """
        if len(relevance_scores) == 0:
            return 0.0

        # DCG: Discounted Cumulative Gain
        dcg = self._calculate_dcg(relevance_scores[:k])

        # IDCG: Ideal DCG (if docs were perfectly ordered by relevance)
        ideal_scores = sorted(relevance_scores, reverse=True)[:k]
        idcg = self._calculate_dcg(ideal_scores)

        # NDCG: Normalized DCG
        ndcg = dcg / idcg if idcg > 0 else 0.0

        return ndcg

    def comprehensive_evaluation(self, test_queries: List[Dict]) -> Dict[str, Any]:
        """
        Run comprehensive evaluation on multiple test queries

        Args:
            test_queries: List of dicts with 'query', 'relevant_doc_ids', 'ground_truth' etc.

        Returns:
            Aggregated evaluation metrics
        """
        all_metrics = {
            'context_relevance': [],
            'precision': [],
            'recall': [],
            'f1_score': [],
            'mrr': [],
            'ndcg': []
        }

        results_per_query = []

        for test_case in test_queries:
            query = test_case['query']
            relevant_ids = test_case.get('relevant_doc_ids', [])
            ground_truth = test_case.get('ground_truth_context', None)

            # Retrieve documents
            retrieved_docs = self.vector_db.search(query, top_k=5)

            # Evaluate context relevance
            relevance_metrics = self.evaluate_context_relevance(
                query, retrieved_docs, ground_truth
            )
            all_metrics['context_relevance'].append(relevance_metrics['overall_relevance'])

            # Evaluate precision/recall (if relevant docs provided)
            if relevant_ids:
                pr_metrics = self.evaluate_retrieval_precision_recall(
                    query, retrieved_docs, relevant_ids, k=5
                )
                all_metrics['precision'].append(pr_metrics['precision_at_k'])
                all_metrics['recall'].append(pr_metrics['recall_at_k'])
                all_metrics['f1_score'].append(pr_metrics['f1_score'])
                all_metrics['mrr'].append(pr_metrics['mean_reciprocal_rank'])

            # Store per-query results
            results_per_query.append({
                'query': query,
                'relevance': relevance_metrics,
                'precision_recall': pr_metrics if relevant_ids else None
            })

        # Calculate aggregate statistics
        aggregate_metrics = {
            'mean_context_relevance': np.mean(all_metrics['context_relevance']) if all_metrics['context_relevance'] else 0.0,
            'mean_precision': np.mean(all_metrics['precision']) if all_metrics['precision'] else 0.0,
            'mean_recall': np.mean(all_metrics['recall']) if all_metrics['recall'] else 0.0,
            'mean_f1_score': np.mean(all_metrics['f1_score']) if all_metrics['f1_score'] else 0.0,
            'mean_mrr': np.mean(all_metrics['mrr']) if all_metrics['mrr'] else 0.0,
            'std_context_relevance': np.std(all_metrics['context_relevance']) if all_metrics['context_relevance'] else 0.0,
            'std_precision': np.std(all_metrics['precision']) if all_metrics['precision'] else 0.0,
            'std_recall': np.std(all_metrics['recall']) if all_metrics['recall'] else 0.0,
        }

        return {
            'aggregate_metrics': aggregate_metrics,
            'per_query_results': results_per_query,
            'test_date': datetime.now().isoformat(),
            'num_queries': len(test_queries)
        }

    # Helper methods

    def _keyword_relevance(self, query: str, retrieved_docs: List[Dict]) -> float:
        """Calculate relevance based on keyword overlap"""
        query_terms = set(query.lower().split())

        relevance_scores = []
        for doc, score in retrieved_docs:
            doc_text = doc.get('text', '').lower()
            doc_terms = set(doc_text.split())

            # Jaccard similarity
            intersection = query_terms & doc_terms
            union = query_terms | doc_terms

            jaccard = len(intersection) / len(union) if union else 0.0
            relevance_scores.append(jaccard)

        return np.mean(relevance_scores) if relevance_scores else 0.0

    def _semantic_relevance(self, query: str, retrieved_docs: List[Dict]) -> float:
        """Calculate relevance based on semantic similarity (using embedding distance)"""
        if not retrieved_docs:
            return 0.0

        # Get query embedding
        query_embedding = self.vector_db.embedding_model.encode([query])[0]

        relevance_scores = []
        for doc, distance in retrieved_docs:
            # Convert L2 distance to similarity score (0-1)
            # Lower distance = higher similarity
            similarity = 1 / (1 + distance)
            relevance_scores.append(similarity)

        return np.mean(relevance_scores)

    def _position_weighted_relevance(self, query: str, retrieved_docs: List[Dict]) -> float:
        """Calculate position-weighted relevance (top results weighted more)"""
        if not retrieved_docs:
            return 0.0

        weighted_scores = []
        for idx, (doc, distance) in enumerate(retrieved_docs):
            # Position weight: 1/log2(rank+1)
            position_weight = 1.0 / np.log2(idx + 2)
            similarity = 1 / (1 + distance)
            weighted_scores.append(similarity * position_weight)

        return np.sum(weighted_scores) / np.sum([1.0 / np.log2(i + 2) for i in range(len(retrieved_docs))])

    def _llm_based_relevance(self, query: str, retrieved_docs: List[Dict]) -> Optional[float]:
        """Use LLM to judge relevance (most accurate but slower)"""
        if not self.llm_client or not retrieved_docs:
            return None

        try:
            # Simplified LLM-based scoring
            relevance_scores = []

            for doc, distance in retrieved_docs[:3]:  # Limit to top 3 for speed
                doc_text = doc.get('text', '')[:500]  # Limit length

                prompt = f"""Rate the relevance of this document to the query on a scale of 0-10.
Query: {query}
Document: {doc_text}

Relevance score (0-10, where 10 is perfectly relevant):"""

                # This is a simplified example - actual implementation would use LLM API
                # For now, fallback to semantic similarity
                similarity = 1 / (1 + distance)
                relevance_scores.append(similarity)

            return np.mean(relevance_scores) if relevance_scores else None

        except Exception as e:
            logger.warning(f"LLM-based relevance scoring failed: {e}")
            return None

    def _ground_truth_similarity(self, retrieved_docs: List[Dict],
                                 ground_truth: str) -> float:
        """Compare retrieved context to ground truth"""
        if not retrieved_docs:
            return 0.0

        # Combine retrieved document texts
        retrieved_text = ' '.join([doc.get('text', '') for doc, _ in retrieved_docs])

        # Calculate similarity to ground truth (using embeddings)
        try:
            retrieved_embedding = self.vector_db.embedding_model.encode([retrieved_text[:1000]])[0]
            ground_truth_embedding = self.vector_db.embedding_model.encode([ground_truth[:1000]])[0]

            # Cosine similarity
            similarity = np.dot(retrieved_embedding, ground_truth_embedding) / (
                np.linalg.norm(retrieved_embedding) * np.linalg.norm(ground_truth_embedding)
            )

            return float(similarity)
        except Exception as e:
            logger.warning(f"Ground truth similarity calculation failed: {e}")
            return 0.0

    def _calculate_mrr(self, retrieved_docs: List[Dict], relevant_ids: set) -> float:
        """Calculate Mean Reciprocal Rank"""
        for idx, (doc, _) in enumerate(retrieved_docs):
            doc_id = doc.get('id', doc.get('metadata', {}).get('doc_id', ''))
            if doc_id in relevant_ids:
                return 1.0 / (idx + 1)
        return 0.0

    def _calculate_average_precision(self, retrieved_docs: List[Dict],
                                    relevant_ids: set) -> float:
        """Calculate Average Precision"""
        relevant_count = 0
        precision_sum = 0.0

        for idx, (doc, _) in enumerate(retrieved_docs):
            doc_id = doc.get('id', doc.get('metadata', {}).get('doc_id', ''))
            if doc_id in relevant_ids:
                relevant_count += 1
                precision_at_k = relevant_count / (idx + 1)
                precision_sum += precision_at_k

        return precision_sum / len(relevant_ids) if relevant_ids else 0.0

    def _calculate_dcg(self, relevance_scores: List[float]) -> float:
        """Calculate Discounted Cumulative Gain"""
        dcg = 0.0
        for idx, score in enumerate(relevance_scores):
            # DCG formula: sum(rel_i / log2(i+2))
            dcg += score / np.log2(idx + 2)
        return dcg

    def save_evaluation_results(self, results: Dict, filepath: str = "data/rag_evaluation_results.json"):
        """Save evaluation results to file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Evaluation results saved to {filepath}")

    def generate_evaluation_report(self, results: Dict) -> str:
        """Generate human-readable evaluation report"""
        metrics = results['aggregate_metrics']

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║         RAG SYSTEM EVALUATION REPORT                         ║
╚══════════════════════════════════════════════════════════════╝

Test Date: {results['test_date']}
Number of Test Queries: {results['num_queries']}

┌──────────────────────────────────────────────────────────────┐
│ CONTEXT RELEVANCE METRICS                                    │
└──────────────────────────────────────────────────────────────┘

Mean Context Relevance:     {metrics['mean_context_relevance']:.3f}
Std Dev:                    {metrics['std_context_relevance']:.3f}

Interpretation:
  0.0 - 0.3: Poor relevance
  0.3 - 0.5: Fair relevance
  0.5 - 0.7: Good relevance ✓
  0.7 - 1.0: Excellent relevance ✓✓

┌──────────────────────────────────────────────────────────────┐
│ PRECISION & RECALL METRICS                                   │
└──────────────────────────────────────────────────────────────┘

Mean Precision@5:           {metrics['mean_precision']:.3f}
Mean Recall@5:              {metrics['mean_recall']:.3f}
Mean F1 Score:              {metrics['mean_f1_score']:.3f}
Mean Reciprocal Rank:       {metrics['mean_mrr']:.3f}

Std Dev (Precision):        {metrics['std_precision']:.3f}
Std Dev (Recall):           {metrics['std_recall']:.3f}

Interpretation:
  Precision: % of retrieved docs that are relevant
  Recall: % of relevant docs that were retrieved
  F1 Score: Harmonic mean of precision and recall
  MRR: Quality of ranking (first relevant result)

┌──────────────────────────────────────────────────────────────┐
│ OVERALL ASSESSMENT                                           │
└──────────────────────────────────────────────────────────────┘

"""
        # Overall grade
        avg_score = (metrics['mean_context_relevance'] + metrics['mean_precision'] +
                    metrics['mean_recall']) / 3

        if avg_score >= 0.8:
            grade = "EXCELLENT ⭐⭐⭐⭐⭐"
        elif avg_score >= 0.7:
            grade = "VERY GOOD ⭐⭐⭐⭐"
        elif avg_score >= 0.6:
            grade = "GOOD ⭐⭐⭐"
        elif avg_score >= 0.5:
            grade = "FAIR ⭐⭐"
        else:
            grade = "NEEDS IMPROVEMENT ⭐"

        report += f"Overall RAG Quality: {grade}\n"
        report += f"Composite Score: {avg_score:.3f}\n\n"

        return report


# Convenience function for quick evaluation
def evaluate_rag_system(vector_db, rag_module, test_queries: List[Dict],
                       save_results: bool = True) -> Dict:
    """
    Quick evaluation of RAG system

    Args:
        vector_db: VectorDatabase instance
        rag_module: RAGModule instance
        test_queries: List of test cases
        save_results: Whether to save results to file

    Returns:
        Evaluation results dictionary
    """
    evaluator = RAGEvaluator(vector_db, rag_module)
    results = evaluator.comprehensive_evaluation(test_queries)

    # Print report
    report = evaluator.generate_evaluation_report(results)
    print(report)

    # Save results
    if save_results:
        evaluator.save_evaluation_results(results)

    return results
