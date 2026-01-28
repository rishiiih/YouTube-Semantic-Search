"""
Text chunking service with timestamp preservation
"""
from typing import List, Dict
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """Handles intelligent text chunking while preserving timestamps"""
    
    def __init__(self):
        self.target_chunk_size = settings.chunk_size  # Target tokens per chunk
        self.overlap_size = settings.chunk_overlap
    
    def chunk_transcript(self, segments: List[Dict]) -> List[Dict]:
        """
        Chunk transcript segments into logical blocks
        
        Strategy:
        - Group segments until reaching ~target_chunk_size tokens
        - Preserve start_time of first segment and end_time of last segment
        - Add overlap between chunks for context continuity
        
        Args:
            segments: List of {"text": str, "start": float, "end": float}
            
        Returns:
            List of chunks with preserved timestamps:
            [
                {
                    "text": "combined text...",
                    "start_time": 0.0,
                    "end_time": 15.5,
                    "chunk_index": 0
                },
                ...
            ]
        """
        if not segments:
            return []
        
        chunks = []
        current_chunk_texts = []
        current_chunk_start = segments[0]["start"]
        current_token_count = 0
        chunk_index = 0
        
        for segment in segments:
            # Rough token estimation: ~4 chars per token
            segment_tokens = len(segment["text"]) // 4
            
            # Check if adding this segment exceeds target
            if current_token_count > 0 and (current_token_count + segment_tokens) > self.target_chunk_size:
                # Save current chunk
                chunk_text = " ".join(current_chunk_texts)
                chunks.append({
                    "text": chunk_text,
                    "start_time": current_chunk_start,
                    "end_time": segments[segments.index(segment) - 1]["end"],
                    "chunk_index": chunk_index
                })
                
                # Start new chunk with overlap
                # Keep last few segments for context
                overlap_texts = current_chunk_texts[-2:] if len(current_chunk_texts) >= 2 else current_chunk_texts
                current_chunk_texts = overlap_texts + [segment["text"]]
                current_chunk_start = segment["start"]
                current_token_count = sum(len(t) // 4 for t in current_chunk_texts)
                chunk_index += 1
            else:
                # Add to current chunk
                current_chunk_texts.append(segment["text"])
                current_token_count += segment_tokens
        
        # Add final chunk
        if current_chunk_texts:
            chunk_text = " ".join(current_chunk_texts)
            chunks.append({
                "text": chunk_text,
                "start_time": current_chunk_start,
                "end_time": segments[-1]["end"],
                "chunk_index": chunk_index
            })
        
        logger.info(f"Created {len(chunks)} chunks from {len(segments)} segments")
        return chunks


# Singleton instance
chunking_service = ChunkingService()
