"""
Embedding generation service using sentence-transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates embeddings for text using local sentence-transformers model"""
    
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Generate embeddings in batch
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert to list of lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(f"Generated {len(embeddings_list)} embeddings")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return self.generate_embeddings([text])[0]


# Singleton instance
embedding_service = EmbeddingService()
