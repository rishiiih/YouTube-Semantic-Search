"""
LLM service for generating answers using Groq
"""
from groq import Groq
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Handles LLM-based answer generation using Groq"""
    
    def __init__(self):
        self._client = None
        self.model = settings.llm_model
    
    @property
    def client(self):
        """Lazy initialization of Groq client"""
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=settings.groq_api_key)
        return self._client
    
    async def generate_answer(self, question: str, context_chunks: list[dict]) -> str:
        """
        Generate answer from question and retrieved chunks
        
        Args:
            question: User's question
            context_chunks: List of chunks with text, start_time, end_time
            
        Returns:
            Answer string with embedded timestamps in [MM:SS] format
        """
        try:
            # Sort chunks by start_time to provide chronological context
            sorted_chunks = sorted(context_chunks, key=lambda x: x["start_time"])
            
            # Format context with timestamps
            context_parts = []
            unique_timestamps = set()
            
            for i, chunk in enumerate(sorted_chunks, 1):
                start_min = int(chunk["start_time"] // 60)
                start_sec = int(chunk["start_time"] % 60)
                timestamp = f"[{start_min:02d}:{start_sec:02d}]"
                
                # Track unique timestamps
                unique_timestamps.add(timestamp)
                
                context_parts.append(
                    f"Context {i} {timestamp}:\n{chunk['text']}\n"
                )
            
            context_text = "\n".join(context_parts)
            
            # System prompt with strict instructions
            system_prompt = """You are a helpful assistant that answers questions based ONLY on the provided video transcript context.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. Use DIFFERENT timestamps from DIFFERENT parts of the video - DO NOT repeat the same timestamp multiple times
3. Reference timestamps in CHRONOLOGICAL ORDER as they appear in the video timeline
4. Use the timestamp [MM:SS] that corresponds to each specific piece of information
5. If multiple contexts have useful information, cite timestamps from DIFFERENT contexts to show the full video coverage
6. Be comprehensive and reference information from throughout the video

Format: Write naturally and embed timestamps [MM:SS] inline when mentioning specific points."""
            
            # User prompt
            user_prompt = f"""Context from video transcript (in chronological order):

{context_text}

Question: {question}

Answer comprehensively using information from MULTIPLE contexts above. Include the specific timestamp [MM:SS] for EACH key point. Use DIFFERENT timestamps to show coverage across the video timeline."""
            
            logger.info(f"Generating answer for: {question}")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistency
                max_tokens=1500
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer with {len(unique_timestamps)} unique timestamps available")
            
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise


# Singleton instance
llm_service = LLMService()
