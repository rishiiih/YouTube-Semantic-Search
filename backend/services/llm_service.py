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
            # Format context with timestamps
            context_parts = []
            for i, chunk in enumerate(context_chunks, 1):
                start_min = int(chunk["start_time"] // 60)
                start_sec = int(chunk["start_time"] % 60)
                timestamp = f"[{start_min:02d}:{start_sec:02d}]"
                
                context_parts.append(
                    f"Context {i} {timestamp}:\n{chunk['text']}\n"
                )
            
            context_text = "\n".join(context_parts)
            
            # System prompt with strict instructions
            system_prompt = """You are a helpful assistant that answers questions based ONLY on the provided video transcript context.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. Include timestamps in [MM:SS] format when referencing specific information
3. If the answer is not in the context, say "I cannot find this information in the video"
4. Be concise and direct
5. Cite the timestamp [MM:SS] for each key point you mention

Format your answer naturally while including timestamps where relevant."""
            
            # User prompt
            user_prompt = f"""Context from video transcript:

{context_text}

Question: {question}

Answer the question using ONLY the context above. Include timestamps [MM:SS] for key points."""
            
            logger.info(f"Generating answer for: {question}")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistency
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer: {answer[:100]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise


# Singleton instance
llm_service = LLMService()
