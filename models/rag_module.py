"""
RAG Module - Retrieval-Augmented Generation
Handles document embedding, storage, and semantic search
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import pickle
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS or SentenceTransformers not available. Install with: pip install faiss-cpu sentence-transformers")


class DocumentChunker:
    """Chunks documents for embedding"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunk = {
                "text": chunk_text,
                "metadata": metadata or {},
                "start_pos": start,
                "end_pos": end
            }
            chunks.append(chunk)
            
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def chunk_dataframe(self, df: pd.DataFrame, text_column: str, 
                       metadata_columns: List[str] = None) -> List[Dict]:
        """Chunk text from dataframe rows"""
        all_chunks = []
        
        for idx, row in df.iterrows():
            text = str(row[text_column])
            metadata = {col: row[col] for col in (metadata_columns or [])}
            metadata['row_index'] = idx
            
            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks


class VectorDatabase:
    """FAISS-based vector database for semantic search"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 dimension: int = 384):
        """
        Initialize vector database
        
        Args:
            embedding_model: HuggingFace model for embeddings
            dimension: Embedding dimension
        """
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.embeddings = None
        
        if FAISS_AVAILABLE:
            self.model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        else:
            self.model = None
            logger.error("SentenceTransformers not available")
    
    def create_index(self):
        """Create FAISS index"""
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available")
        
        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info(f"Created FAISS index with dimension {self.dimension}")
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector database"""
        if not self.model:
            logger.error("No embedding model loaded")
            return
        
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Add to index
        if self.index is None:
            self.create_index()
        
        self.index.add(embeddings.astype('float32'))
        self.documents.extend(documents)
        
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
        
        logger.info(f"Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        if not self.model or self.index is None:
            logger.error("Model or index not initialized")
            return []
        
        # Encode query
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                result = {
                    "document": self.documents[idx],
                    "score": float(dist),
                    "similarity": 1 / (1 + float(dist))  # Convert distance to similarity
                }
                results.append(result)
        
        return results
    
    def save(self, path: str):
        """Save index and documents to disk"""
        if not FAISS_AVAILABLE:
            return
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        if self.index:
            faiss.write_index(self.index, str(path / "faiss.index"))
        
        # Save documents and embeddings
        with open(path / "documents.pkl", 'wb') as f:
            pickle.dump(self.documents, f)
        
        if self.embeddings is not None:
            np.save(path / "embeddings.npy", self.embeddings)
        
        logger.info(f"Saved vector database to {path}")
    
    def load(self, path: str):
        """Load index and documents from disk"""
        if not FAISS_AVAILABLE:
            return
        
        path = Path(path)
        
        # Load FAISS index
        index_path = path / "faiss.index"
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
        
        # Load documents
        docs_path = path / "documents.pkl"
        if docs_path.exists():
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
        
        # Load embeddings
        emb_path = path / "embeddings.npy"
        if emb_path.exists():
            self.embeddings = np.load(emb_path)
        
        logger.info(f"Loaded vector database from {path}")


class RAGModule:
    """Complete RAG system for SCM chatbot"""
    
    def __init__(self, config: Dict):
        """
        Initialize RAG module
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.chunker = DocumentChunker(
            chunk_size=config.get('chunk_size', 500),
            chunk_overlap=config.get('chunk_overlap', 50)
        )
        self.vector_db = VectorDatabase(
            embedding_model=config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        )
        self.knowledge_base = []
    
    def build_knowledge_base(self, orders_df: pd.DataFrame, products_df: pd.DataFrame,
                            customers_df: pd.DataFrame):
        """Build knowledge base from supply chain data"""
        logger.info("Building knowledge base...")
        
        # Create knowledge base documents
        kb_docs = []
        
        # Add order information
        for idx, order in orders_df.head(1000).iterrows():  # Limit for demo
            text = f"""
            Order ID: {order['order_id']}
            Customer ID: {order['customer_id']}
            Status: {order['order_status']}
            Purchase Date: {order['order_purchase_timestamp']}
            Delivery Date: {order.get('order_delivered_timestamp', 'Not delivered')}
            Delayed: {order.get('is_delayed', False)}
            """
            
            doc = {
                'text': text.strip(),
                'metadata': {
                    'type': 'order',
                    'order_id': order['order_id'],
                    'status': order['order_status']
                }
            }
            kb_docs.append(doc)
        
        # Add product information
        for idx, product in products_df.head(500).iterrows():  # Limit for demo
            text = f"""
            Product ID: {product['product_id']}
            Category: {product.get('product_category_name', 'Unknown')}
            Weight: {product.get('product_weight_g', 'N/A')}g
            Dimensions: {product.get('product_length_cm', 'N/A')}x{product.get('product_width_cm', 'N/A')}x{product.get('product_height_cm', 'N/A')} cm
            """
            
            doc = {
                'text': text.strip(),
                'metadata': {
                    'type': 'product',
                    'product_id': product['product_id'],
                    'category': product.get('product_category_name', 'Unknown')
                }
            }
            kb_docs.append(doc)
        
        self.knowledge_base = kb_docs
        self.vector_db.add_documents(kb_docs)
        
        logger.info(f"Built knowledge base with {len(kb_docs)} documents")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        return self.vector_db.search(query, top_k=top_k)
    
    def save(self, path: str):
        """Save RAG module"""
        self.vector_db.save(path)
    
    def load(self, path: str):
        """Load RAG module"""
        self.vector_db.load(path)
