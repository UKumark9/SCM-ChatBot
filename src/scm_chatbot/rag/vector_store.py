"""
Vector store abstraction (Dependency Inversion).

VectorDatabase (rag.py) depends on these interfaces rather than importing
sentence-transformers and FAISS directly, so the embedding model and index
backend can be swapped or mocked in tests without touching RAG business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import numpy as np


class EmbeddingModel(ABC):
    """Abstract interface for turning text into vectors."""

    @abstractmethod
    def encode(
        self,
        texts: Union[str, List[str]],
        show_progress: bool = False,
        convert_to_tensor: bool = False,
    ):
        """Embed one text or a list of texts."""
        raise NotImplementedError


class VectorIndex(ABC):
    """Abstract interface for a nearest-neighbor vector index."""

    @abstractmethod
    def add(self, vectors: np.ndarray) -> None:
        """Add vectors to the index."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self, query_vector: np.ndarray, top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Return (distances, indices) for the top_k nearest neighbors."""
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist the index to disk at path."""
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> None:
        """Load the index from disk at path, replacing current contents."""
        raise NotImplementedError


class SentenceTransformerEmbedding(EmbeddingModel):
    """sentence-transformers-backed implementation of EmbeddingModel."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def encode(
        self,
        texts: Union[str, List[str]],
        show_progress: bool = False,
        convert_to_tensor: bool = False,
    ):
        return self._model.encode(
            texts, show_progress_bar=show_progress, convert_to_tensor=convert_to_tensor
        )


class FaissFlatIndex(VectorIndex):
    """FAISS IndexFlatL2-backed implementation of VectorIndex."""

    def __init__(self, dimension: int):
        import faiss

        self._faiss = faiss
        self.dimension = dimension
        self._index = faiss.IndexFlatL2(dimension)

    def add(self, vectors: np.ndarray) -> None:
        self._index.add(vectors.astype("float32"))

    def search(
        self, query_vector: np.ndarray, top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        return self._index.search(query_vector.astype("float32"), top_k)

    def save(self, path: str) -> None:
        self._faiss.write_index(self._index, path)

    def load(self, path: str) -> None:
        self._index = self._faiss.read_index(path)
