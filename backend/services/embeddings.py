"""Text embedding generation and similarity search."""
import numpy as np
from typing import Optional, List
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Generates embeddings and performs similarity search."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding model.
        
        Args:
            model_name: Sentence-transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dimension = 384  # Dimension for this model

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            raise ValueError(f"Failed to generate embeddings: {str(e)}")

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            arr1 = np.array(embedding1)
            arr2 = np.array(embedding2)

            # Cosine similarity
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            raise ValueError(f"Failed to calculate similarity: {str(e)}")

    def batch_similarities(
        self, query_embedding: List[float], document_embeddings: List[List[float]]
    ) -> List[float]:
        """Calculate similarities between query and multiple documents."""
        try:
            query = np.array(query_embedding)
            documents = np.array(document_embeddings)

            # Batch cosine similarity
            dot_products = np.dot(documents, query)
            query_norm = np.linalg.norm(query)
            doc_norms = np.linalg.norm(documents, axis=1)

            similarities = dot_products / (doc_norms * query_norm)
            return similarities.tolist()
        except Exception as e:
            raise ValueError(f"Failed to calculate batch similarities: {str(e)}")

    def search_similar(
        self,
        query_text: str,
        documents: List[str],
        top_k: int = 5,
    ) -> List[tuple[int, str, float]]:
        """Find most similar documents to query text.
        
        Returns:
            List of (index, document, similarity_score) tuples
        """
        try:
            query_embedding = self.embed_text(query_text)
            doc_embeddings = self.embed_texts(documents)

            similarities = self.batch_similarities(query_embedding, doc_embeddings)

            # Get top-k with indices
            indexed_similarities = [
                (idx, doc, score)
                for idx, (doc, score) in enumerate(zip(documents, similarities))
            ]
            indexed_similarities.sort(key=lambda x: x[2], reverse=True)

            return indexed_similarities[:top_k]
        except Exception as e:
            raise ValueError(f"Failed to search similar documents: {str(e)}")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.embedding_dimension


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
