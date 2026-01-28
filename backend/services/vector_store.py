"""
ChromaDB vector store wrapper
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
from backend.app.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages ChromaDB collections for video embeddings"""
    
    def __init__(self):
        logger.info(f"Initializing ChromaDB at: {settings.chroma_path}")
        self.client = chromadb.PersistentClient(
            path=str(settings.get_chroma_dir())
        )
        self.collection_name = "video_chunks"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create or get the main collection"""
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Video transcript chunks with timestamps"}
        )
        logger.info(f"Collection ready: {self.collection_name}")
    
    async def add_chunks(
        self,
        video_id: str,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        Add chunks with embeddings to ChromaDB
        
        Args:
            video_id: Unique video identifier
            chunks: List of chunk dicts with text, start_time, end_time, chunk_index
            embeddings: Corresponding embedding vectors
            
        Returns:
            List of generated chunk_ids
        """
        try:
            chunk_ids = [str(uuid.uuid4()) for _ in chunks]
            
            # Prepare metadata for each chunk
            metadatas = [
                {
                    "video_id": video_id,
                    "start_time": chunk["start_time"],
                    "end_time": chunk["end_time"],
                    "chunk_index": chunk["chunk_index"]
                }
                for chunk in chunks
            ]
            
            # Prepare documents (text content)
            documents = [chunk["text"] for chunk in chunks]
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunk_ids)} chunks to ChromaDB for video {video_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {e}")
            raise
    
    async def query_similar(
        self,
        query_embedding: List[float],
        video_id: str,
        top_k: int = None
    ) -> Dict:
        """
        Query similar chunks for a given video
        
        Args:
            query_embedding: Query embedding vector
            video_id: Filter by video_id
            top_k: Number of results (default from settings)
            
        Returns:
            Dict with ids, documents, metadatas, distances
        """
        try:
            if top_k is None:
                top_k = settings.top_k_results
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"video_id": video_id}
            )
            
            logger.info(f"Retrieved {len(results['ids'][0])} results for video {video_id}")
            return results
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    async def delete_video_chunks(self, video_id: str):
        """Delete all chunks for a video"""
        try:
            self.collection.delete(where={"video_id": video_id})
            logger.info(f"Deleted chunks for video {video_id}")
        except Exception as e:
            logger.error(f"Failed to delete chunks: {e}")
            raise
    
    def check_health(self) -> bool:
        """Check if ChromaDB is accessible"""
        try:
            self.collection.count()
            return True
        except Exception:
            return False


# Singleton instance
vector_store = VectorStore()
