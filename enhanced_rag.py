"""
Enhanced RAG Module with Advanced Retrieval Techniques
Implements re-ranking, contextual compression, and hybrid search
"""

import logging
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from sentence_transformers import CrossEncoder, util
from rank_bm25 import BM25Okapi
import re

from rag import VectorDatabase, RAGModule

logger = logging.getLogger(__name__)


class EnhancedVectorDatabase(VectorDatabase):
    """
    Enhanced Vector Database with Hybrid Search (Vector + BM25)
    """

    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 dimension: int = 384):
        super().__init__(embedding_model_name, dimension)
        self.bm25 = None
        self.tokenized_docs = None

    def build_index(self, documents: List[Dict]):
        """Build both FAISS and BM25 indices"""
        # Build FAISS index (existing)
        super().build_index(documents)

        # Build BM25 index for keyword search
        logger.info("Building BM25 index for hybrid search...")
        self.tokenized_docs = [
            self._tokenize(doc['text'])
            for doc in documents
        ]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        logger.info(f"✅ BM25 index built with {len(documents)} documents")

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        # Convert to lowercase and split on whitespace/punctuation
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens

    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.5) -> List[Tuple[Dict, float]]:
        """
        Hybrid search combining vector and keyword matching

        Args:
            query: Search query
            top_k: Number of results
            alpha: Weight for vector search (0.0 = pure BM25, 1.0 = pure vector, 0.5 = balanced)

        Returns:
            List of (document, score) tuples
        """
        if not self.bm25:
            logger.warning("BM25 index not built, falling back to vector search")
            return self.search(query, top_k)

        # 1. Vector search scores (wider pool to give BM25 more candidates to boost)
        vector_results = self.search(query, top_k=top_k * 4)
        vector_scores = {}
        for doc, distance in vector_results:
            doc_id = doc['id']
            # Convert distance to similarity (0-1 scale)
            similarity = 1 / (1 + distance)
            vector_scores[doc_id] = similarity

        # 2. BM25 keyword search scores
        query_tokens = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(query_tokens)

        # Normalize BM25 scores to 0-1 scale
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
        bm25_normalized = {}
        for i, score in enumerate(bm25_scores):
            if i < len(self.documents):
                doc_id = self.documents[i]['id']
                bm25_normalized[doc_id] = score / max_bm25

        # 3. Combine scores with weighted average
        all_doc_ids = set(vector_scores.keys()) | set(bm25_normalized.keys())
        hybrid_scores = {}

        for doc_id in all_doc_ids:
            vector_score = vector_scores.get(doc_id, 0)
            bm25_score = bm25_normalized.get(doc_id, 0)

            # Weighted combination
            hybrid_scores[doc_id] = (alpha * vector_score) + ((1 - alpha) * bm25_score)

        # 4. Sort by combined score and return top-k
        sorted_docs = sorted(
            hybrid_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        # Convert back to (doc, distance) format
        results = []
        for doc_id, score in sorted_docs:
            doc = next((d for d in self.documents if d['id'] == doc_id), None)
            if doc:
                # Convert similarity back to distance for consistency
                distance = (1 / score) - 1 if score > 0 else 999
                results.append((doc, distance))

        return results

    def add_documents(self, new_documents: List[Dict]):
        """Add new documents to existing index (incremental indexing with BM25 update)"""
        # Call parent method to add to FAISS index
        super().add_documents(new_documents)

        # Update BM25 index
        if self.bm25 and new_documents:
            logger.info("Updating BM25 index with new documents...")
            new_tokenized = [self._tokenize(doc['text']) for doc in new_documents]
            self.tokenized_docs.extend(new_tokenized)
            # Rebuild BM25 (it's fast enough to rebuild)
            self.bm25 = BM25Okapi(self.tokenized_docs)
            logger.info(f"✅ BM25 index updated")

    def load_index(self, path: str):
        """Load index and rebuild BM25"""
        super().load_index(path)

        # Rebuild BM25 index
        if self.documents:
            logger.info("Rebuilding BM25 index from loaded documents...")
            self.tokenized_docs = [
                self._tokenize(doc['text'])
                for doc in self.documents
            ]
            self.bm25 = BM25Okapi(self.tokenized_docs)
            logger.info(f"✅ BM25 index rebuilt with {len(self.documents)} documents")


class EnhancedRAGModule(RAGModule):
    """
    Enhanced RAG Module with Re-Ranking and Contextual Compression
    """

    def __init__(self, vector_db: VectorDatabase, top_k: int = 5,
                 similarity_threshold: float = 2.0,
                 enable_reranking: bool = True,
                 enable_compression: bool = True,
                 rerank_model: str = "cross-encoder/ms-marco-TinyBERT-L-2-v2"):
        """
        Initialize Enhanced RAG Module

        Args:
            vector_db: VectorDatabase instance
            top_k: Number of top results to retrieve
            similarity_threshold: Similarity threshold for filtering
            enable_reranking: Enable cross-encoder re-ranking
            enable_compression: Enable contextual compression
            rerank_model: Cross-encoder model for re-ranking
        """
        super().__init__(vector_db, top_k, similarity_threshold)

        self.enable_reranking = enable_reranking
        self.enable_compression = enable_compression

        # Initialize re-ranker
        if enable_reranking:
            try:
                logger.info(f"Loading re-ranker model: {rerank_model}...")
                self.reranker = CrossEncoder(rerank_model)
                logger.info("✅ Re-ranker loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load re-ranker: {e}")
                self.reranker = None
                self.enable_reranking = False
        else:
            self.reranker = None

    def retrieve_context(self, query: str, use_query_expansion: bool = True,
                        use_hybrid: bool = True, alpha: float = 0.5) -> str:
        """
        Enhanced context retrieval with re-ranking and compression

        Args:
            query: User query
            use_query_expansion: Enable query expansion
            use_hybrid: Use hybrid search if available
            alpha: Hybrid search alpha (0.0=BM25 only, 1.0=vector only)

        Returns:
            Retrieved context as formatted string
        """
        try:
            import time
            start_time = time.time()

            # Step 1: Expand query if enabled (only for complex queries)
            t1 = time.time()
            queries_to_search = [query]
            # Optimization: Only expand queries with 6+ words for better performance
            if use_query_expansion and len(query.split()) >= 6:
                expanded_queries = self._expand_query(query)
                queries_to_search.extend(expanded_queries)
                logger.info(f"Expanded query to {len(queries_to_search)} variations")
            logger.debug(f"⏱️  Query expansion: {time.time() - t1:.2f}s")

            # Step 2: Initial retrieval (get more candidates for re-ranking)
            # Optimized: Reduced from 4x to 2x for faster re-ranking
            t2 = time.time()
            initial_k = self.top_k * 2 if self.enable_reranking else self.top_k
            all_results = {}

            for q in queries_to_search:
                # Use hybrid search if available and enabled
                if use_hybrid and hasattr(self.vector_db, 'hybrid_search'):
                    results = self.vector_db.hybrid_search(q, top_k=initial_k, alpha=alpha)
                else:
                    results = self.vector_db.search(q, initial_k)

                for doc, score in results:
                    doc_id = doc.get('id', id(doc))
                    # Keep best score for each document
                    if doc_id not in all_results or score < all_results[doc_id][1]:
                        all_results[doc_id] = (doc, score)

            # Convert back to list and sort by score
            results = sorted(all_results.values(), key=lambda x: x[1])[:initial_k]
            logger.debug(f"⏱️  Hybrid search: {time.time() - t2:.2f}s")

            # Step 3: Re-rank if enabled
            t3 = time.time()
            if self.enable_reranking and self.reranker and len(results) > 1:
                results = self._rerank_results(query, results)
                logger.info(f"Re-ranked {len(results)} results")
            logger.debug(f"⏱️  Re-ranking: {time.time() - t3:.2f}s")

            # Take top-k after re-ranking
            results = results[:self.top_k]

            # Step 4: Filter by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score < self.similarity_threshold
            ]

            if not filtered_results:
                logger.warning(f"No results passed threshold {self.similarity_threshold}")
                return "No relevant context found."

            # Step 5: Apply contextual compression if enabled
            t4 = time.time()
            if self.enable_compression:
                context = self._compressed_context(query, filtered_results)
            else:
                context = self._format_context_standard(filtered_results)
            logger.debug(f"⏱️  Compression: {time.time() - t4:.2f}s")

            total_time = time.time() - start_time
            logger.info(f"Retrieved {len(filtered_results)} relevant documents in {total_time:.2f}s")
            return context

        except Exception as e:
            logger.error(f"Error in enhanced retrieval: {e}")
            return "Error retrieving context."

    def _rerank_results(self, query: str, results: List[Tuple[Dict, float]]) -> List[Tuple[Dict, float]]:
        """
        Re-rank results using cross-encoder

        Args:
            query: Original query
            results: Initial retrieval results

        Returns:
            Re-ranked results
        """
        try:
            # Prepare query-document pairs
            pairs = [(query, doc['text']) for doc, _ in results]

            # Get re-ranking scores from cross-encoder
            rerank_scores = self.reranker.predict(pairs)

            # Combine with original results and sort by re-ranking scores
            reranked = sorted(
                zip(results, rerank_scores),
                key=lambda x: x[1],
                reverse=True
            )

            # Return re-ranked documents with original distance scores
            # (we keep original scores but change order based on re-ranking)
            return [doc_score for (doc_score, _) in reranked]

        except Exception as e:
            logger.warning(f"Re-ranking failed: {e}, using original order")
            return results

    def _compressed_context(self, query: str, results: List[Tuple[Dict, float]],
                           sentences_per_doc: int = 2) -> str:
        """
        Extract only the most relevant sentences from each document

        Args:
            query: Original query
            results: Retrieved documents
            sentences_per_doc: Number of sentences to extract per document

        Returns:
            Compressed context string
        """
        try:
            compressed_parts = []

            for doc, score in results:
                # Extract relevant sentences
                compressed_text = self._extract_relevant_sentences(
                    query,
                    doc['text'],
                    top_k=sentences_per_doc
                )

                similarity = 1 / (1 + score)
                compressed_parts.append(
                    f"[Relevance: {similarity:.2f}]\n{compressed_text}\n"
                )

            return "\n---\n".join(compressed_parts)

        except Exception as e:
            logger.warning(f"Compression failed: {e}, using standard format")
            return self._format_context_standard(results)

    def _extract_relevant_sentences(self, query: str, text: str, top_k: int = 3) -> str:
        """
        Extract the most relevant sentences from text using sentence embeddings

        Args:
            query: Search query
            text: Document text
            top_k: Number of sentences to extract

        Returns:
            Concatenated relevant sentences
        """
        try:
            # Split into sentences (simple approach)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

            if len(sentences) <= top_k:
                return text  # Return full text if too few sentences

            # Embed query and sentences
            query_embedding = self.vector_db.embedding_model.encode(query, convert_to_tensor=True)
            sentence_embeddings = self.vector_db.embedding_model.encode(sentences, convert_to_tensor=True)

            # Calculate similarities
            similarities = util.cos_sim(query_embedding, sentence_embeddings)[0]

            # Get top-k most similar sentences
            top_indices = similarities.argsort(descending=True)[:top_k]

            # Sort by original order to maintain readability
            top_indices_sorted = sorted(top_indices.tolist())

            # Combine selected sentences
            relevant_sentences = [sentences[i] for i in top_indices_sorted]
            return ' '.join(relevant_sentences)

        except Exception as e:
            logger.warning(f"Sentence extraction failed: {e}")
            return text[:500]  # Fallback to first 500 chars

    def _format_context_standard(self, results: List[Tuple[Dict, float]]) -> str:
        """Standard context formatting (no compression)"""
        context_parts = []
        for doc, score in results:
            similarity = 1 / (1 + score)
            context_parts.append(f"[Relevance: {similarity:.2f}]\n{doc['text']}\n")

        return "\n---\n".join(context_parts)

    def _expand_query(self, query: str) -> List[str]:
        """
        Enhanced query expansion with better semantic coverage

        Args:
            query: Original query

        Returns:
            List of expanded queries
        """
        query_lower = query.lower()
        expansions = []

        # Pattern 1: Severity/Classification
        if 'severity' in query_lower or 'level' in query_lower:
            expansions.extend([
                query.replace('severity', 'classification'),
                query.replace('severity levels', 'delay categories'),
                query.replace('severity', 'priority')
            ])

        # Pattern 2: Delay/Late
        if 'delay' in query_lower:
            expansions.extend([
                query.replace('delay', 'late delivery'),
                query.replace('delay', 'lateness')
            ])

        # Pattern 3: Policy/Procedure
        if 'policy' in query_lower:
            expansions.extend([
                query.replace('policy', 'procedure'),
                query.replace('policy', 'guideline')
            ])

        # Pattern 4: Process/Steps
        if 'process' in query_lower:
            expansions.extend([
                query.replace('process', 'procedure'),
                query.replace('process', 'steps')
            ])

        # Remove duplicates and limit
        expansions = list(set(expansions))[:2]
        return expansions


# Convenience function to create enhanced RAG system
def create_enhanced_rag_system(
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    enable_reranking: bool = True,
    enable_compression: bool = True,
    enable_hybrid: bool = True
) -> Tuple[EnhancedVectorDatabase, EnhancedRAGModule]:
    """
    Create an enhanced RAG system with all improvements

    Args:
        embedding_model: Embedding model name
        enable_reranking: Enable cross-encoder re-ranking
        enable_compression: Enable contextual compression
        enable_hybrid: Enable hybrid search

    Returns:
        (vector_db, rag_module) tuple
    """
    # Create enhanced vector database
    if enable_hybrid:
        vector_db = EnhancedVectorDatabase(
            embedding_model_name=embedding_model,
            dimension=384
        )
    else:
        vector_db = VectorDatabase(
            embedding_model_name=embedding_model,
            dimension=384
        )

    # Initialize vector database
    vector_db.initialize()

    # Create enhanced RAG module
    rag_module = EnhancedRAGModule(
        vector_db=vector_db,
        top_k=5,
        similarity_threshold=2.0,
        enable_reranking=enable_reranking,
        enable_compression=enable_compression
    )

    return vector_db, rag_module
