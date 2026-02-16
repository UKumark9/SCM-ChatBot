"""
Retrieval-Augmented Generation (RAG) Module
Handles document embedding, vector storage, and retrieval
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import pickle

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    logging.warning("sentence-transformers or faiss not installed")

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk documents for RAG"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize Document Processor

        Args:
            chunk_size: Number of words per chunk
            chunk_overlap: Number of overlapping words between chunks
                          Increased default to preserve context better
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def create_documents_from_data(self, data_processor) -> List[Dict]:
        """Create searchable documents from supply chain data"""
        try:
            logger.info("Creating documents from supply chain data...")
            documents = []
            
            # Create documents from orders
            for _, order in data_processor.orders.iterrows():
                doc_text = f"""
                Order ID: {order['order_id']}
                Customer: {order['customer_id']}
                Status: {order['order_status']}
                Purchase Date: {order['order_purchase_timestamp']}
                Delivery Status: {'Delayed' if order.get('is_delayed') else 'On Time'}
                Delay Days: {order.get('delay_days', 0)}
                State: {order.get('customer_state', 'Unknown')}
                """
                
                documents.append({
                    'id': f"order_{order['order_id']}",
                    'text': doc_text.strip(),
                    'type': 'order',
                    'metadata': {
                        'order_id': order['order_id'],
                        'customer_id': order['customer_id'],
                        'status': order['order_status'],
                        'is_delayed': order.get('is_delayed', False)
                    }
                })
            
            # Create documents from products
            for _, product in data_processor.products.iterrows():
                doc_text = f"""
                Product ID: {product['product_id']}
                Category: {product.get('product_category_name', 'Unknown')}
                Weight: {product.get('product_weight_g', 0)}g
                Dimensions: L{product.get('product_length_cm', 0)} x 
                           W{product.get('product_width_cm', 0)} x 
                           H{product.get('product_height_cm', 0)} cm
                """
                
                documents.append({
                    'id': f"product_{product['product_id']}",
                    'text': doc_text.strip(),
                    'type': 'product',
                    'metadata': {
                        'product_id': product['product_id'],
                        'category': product.get('product_category_name', 'Unknown')
                    }
                })
            
            # Create summary documents
            summary_docs = [
                {
                    'id': 'summary_delays',
                    'text': f"""
                    Supply Chain Delay Analysis Summary:
                    Total Orders: {len(data_processor.orders)}
                    Delayed Orders: {data_processor.orders['is_delayed'].sum()}
                    Delay Rate: {data_processor.orders['is_delayed'].mean() * 100:.2f}%
                    Average Delay: {data_processor.orders[data_processor.orders['is_delayed']]['delay_days'].mean():.2f} days
                    This indicates the overall delivery performance of the supply chain.
                    """,
                    'type': 'summary',
                    'metadata': {'category': 'delays'}
                },
                {
                    'id': 'summary_revenue',
                    'text': f"""
                    Revenue and Sales Summary:
                    Total Revenue: ${data_processor.payments['payment_value'].sum():,.2f}
                    Total Orders: {len(data_processor.orders)}
                    Average Order Value: ${data_processor.payments.groupby('order_id')['payment_value'].sum().mean():,.2f}
                    This provides an overview of the financial performance.
                    """,
                    'type': 'summary',
                    'metadata': {'category': 'revenue'}
                }
            ]
            
            documents.extend(summary_docs)
            
            logger.info(f"Created {len(documents)} documents for RAG")
            return documents
            
        except Exception as e:
            logger.error(f"Error creating documents: {str(e)}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks with semantic boundaries

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        # Try to split by paragraphs first for better semantic preservation
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            words = para.split()
            para_size = len(words)

            # If paragraph fits in current chunk
            if current_size + para_size <= self.chunk_size:
                current_chunk.extend(words)
                current_size += para_size
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(' '.join(current_chunk))

                # If paragraph is larger than chunk_size, split it
                if para_size > self.chunk_size:
                    for i in range(0, para_size, self.chunk_size - self.chunk_overlap):
                        chunk = ' '.join(words[i:i + self.chunk_size])
                        chunks.append(chunk)
                    current_chunk = []
                    current_size = 0
                else:
                    # Start new chunk with overlap from previous
                    if chunks:
                        prev_words = chunks[-1].split()
                        overlap_words = prev_words[-self.chunk_overlap:]
                        current_chunk = overlap_words + words
                        current_size = len(current_chunk)
                    else:
                        current_chunk = words
                        current_size = para_size

        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks if chunks else [text]  # Return original if no chunks created


class VectorDatabase:
    """Vector database for semantic search"""
    
    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 dimension: int = 384):
        self.embedding_model_name = embedding_model_name
        self.dimension = dimension
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.doc_embeddings = None
    
    def initialize(self):
        """Initialize the embedding model and FAISS index"""
        try:
            logger.info("Initializing vector database...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info("Vector database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            raise
    
    def embed_documents(self, documents: List[Dict]) -> np.ndarray:
        """Generate embeddings for documents"""
        try:
            logger.info(f"Embedding {len(documents)} documents...")
            texts = [doc['text'] for doc in documents]
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            logger.info(f"Generated embeddings with shape {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    def build_index(self, documents: List[Dict]):
        """Build the vector index from documents"""
        try:
            logger.info("Building vector index...")
            self.documents = documents
            self.doc_embeddings = self.embed_documents(documents)
            self.index.add(self.doc_embeddings.astype('float32'))
            logger.info(f"Index built with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise
    
    def add_documents(self, new_documents: List[Dict]):
        """
        Add new documents to existing index (incremental indexing)

        Args:
            new_documents: List of document dictionaries to add
        """
        try:
            if not new_documents:
                logger.warning("No documents to add")
                return

            logger.info(f"Adding {len(new_documents)} new documents to index...")

            # Embed new documents
            new_embeddings = self.embed_documents(new_documents)

            # Add to FAISS index
            self.index.add(new_embeddings.astype('float32'))

            # Append to documents list
            self.documents.extend(new_documents)

            # Append to embeddings array
            if self.doc_embeddings is not None:
                self.doc_embeddings = np.vstack([self.doc_embeddings, new_embeddings])
            else:
                self.doc_embeddings = new_embeddings

            logger.info(f"✅ Added {len(new_documents)} documents. Total: {len(self.documents)}")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Search for relevant documents"""
        try:
            logger.info(f"Searching for: {query}")
            query_embedding = self.embedding_model.encode([query])
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)

            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(distance)))

            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise
    
    def save_index(self, path: str):
        """Save the index and documents to disk"""
        try:
            logger.info(f"Saving index to {path}...")
            index_path = Path(path)
            index_path.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(index_path / "index.faiss"))
            
            # Save documents and metadata
            with open(index_path / "documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(index_path / "embeddings.npy", 'wb') as f:
                np.save(f, self.doc_embeddings)
            
            logger.info("Index saved successfully")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, path: str):
        """Load the index and documents from disk"""
        try:
            logger.info(f"Loading index from {path}...")
            index_path = Path(path)
            
            # Load FAISS index
            self.index = faiss.read_index(str(index_path / "index.faiss"))
            
            # Load documents and metadata
            with open(index_path / "documents.pkl", 'rb') as f:
                self.documents = pickle.load(f)
            
            with open(index_path / "embeddings.npy", 'rb') as f:
                self.doc_embeddings = np.load(f)
            
            logger.info(f"Index loaded with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise


class RAGModule:
    """Retrieval-Augmented Generation Module"""

    def __init__(self, vector_db: VectorDatabase, top_k: int = 5,
                 similarity_threshold: float = 2.0):
        """
        Initialize RAG Module

        Args:
            vector_db: VectorDatabase instance
            top_k: Number of top results to retrieve
            similarity_threshold: Distance threshold (higher = more permissive)
                                 Recommended: 2.0-3.0 for good recall
                                 Lower values (< 1.0) = very strict, may miss relevant docs
        """
        self.vector_db = vector_db
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
    
    def retrieve_context(self, query: str, use_query_expansion: bool = True) -> str:
        """
        Retrieve relevant context for a query

        Args:
            query: User query
            use_query_expansion: If True, expand query with related terms

        Returns:
            Retrieved context as formatted string
        """
        try:
            # Expand query if enabled
            queries_to_search = [query]
            if use_query_expansion:
                expanded_queries = self._expand_query(query)
                queries_to_search.extend(expanded_queries)
                logger.info(f"Expanded query to {len(queries_to_search)} variations")

            # Search with all query variations
            all_results = {}
            for q in queries_to_search:
                results = self.vector_db.search(q, self.top_k)
                for doc, score in results:
                    doc_id = doc.get('id', id(doc))
                    # Keep best score for each document
                    if doc_id not in all_results or score < all_results[doc_id][1]:
                        all_results[doc_id] = (doc, score)

            # Convert back to list and sort by score
            results = sorted(all_results.values(), key=lambda x: x[1])[:self.top_k]

            # Filter by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score < self.similarity_threshold  # Lower distance = higher similarity
            ]

            if not filtered_results:
                logger.warning(f"No results passed threshold {self.similarity_threshold}")
                return "No relevant context found."

            # Combine retrieved documents
            context_parts = []
            for doc, score in filtered_results:
                similarity = 1/(1+score)
                doc_name = doc.get('metadata', {}).get('doc_name', '')
                source_line = f"[Source: {doc_name}]\n" if doc_name else ""
                context_parts.append(f"{source_line}[Relevance: {similarity:.2f}]\n{doc['text']}\n")

            context = "\n---\n".join(context_parts)
            logger.info(f"Retrieved {len(filtered_results)} relevant documents")
            return context

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return ""

    def _expand_query(self, query: str) -> List[str]:
        """
        Expand query with related terms for better retrieval

        Args:
            query: Original query

        Returns:
            List of expanded query variations
        """
        expanded = []
        query_lower = query.lower()

        # Severity-related expansions
        if 'severity' in query_lower or 'level' in query_lower:
            expanded.extend([
                "critical delay major delay minor delay classification",
                "delay severity levels product management",
                "critical major minor at-risk delay categories"
            ])

        # Delay-related expansions
        if 'delay' in query_lower:
            expanded.extend([
                "product delay management policy",
                "delivery delay classification"
            ])

        # Policy-related expansions
        if 'policy' in query_lower or 'procedure' in query_lower:
            expanded.extend([
                "supply chain management procedures",
                "operational policies guidelines"
            ])

        return expanded[:2]  # Limit to top 2 expansions
    
    def augment_query(self, query: str, context: str) -> str:
        """Augment the query with retrieved context"""
        augmented_query = f"""
Context from supply chain database:
{context}

User Question: {query}

Please answer the question based on the provided context. If the context doesn't contain relevant information, say so.
"""
        return augmented_query


def build_rag_system(data_processor, config: Dict) -> Tuple[VectorDatabase, RAGModule]:
    """Build and initialize the complete RAG system"""
    try:
        logger.info("Building RAG system...")
        
        # Create documents
        doc_processor = DocumentProcessor(
            chunk_size=config['chunk_size'],
            chunk_overlap=config['chunk_overlap']
        )
        documents = doc_processor.create_documents_from_data(data_processor)
        
        # Initialize vector database
        vector_db = VectorDatabase(
            embedding_model_name=config['embedding_model'],
            dimension=config['dimension']
        )
        vector_db.initialize()
        vector_db.build_index(documents)
        
        # Initialize RAG module
        rag = RAGModule(
            vector_db=vector_db,
            top_k=config.get('top_k', 5),
            similarity_threshold=config.get('similarity_threshold', 1.5)
        )
        
        logger.info("RAG system built successfully")
        return vector_db, rag
        
    except Exception as e:
        logger.error(f"Error building RAG system: {str(e)}")
        raise
