"""Service for generating suggested questions from video transcripts using Groq LLM."""
import os
from typing import List, Optional
from groq import Groq
import logging

logger = logging.getLogger(__name__)


class QuestionGeneratorService:
    """Generates contextually relevant questions from video transcripts."""

    def __init__(self):
        """Initialize (lazy-load the Groq client)."""
        self._client = None
        self.model = "llama-3.3-70b-versatile"

    @property
    def client(self):
        """Lazy-load the Groq client."""
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self._client = Groq(api_key=api_key)
        return self._client

    def generate_questions(
        self, 
        transcript: str, 
        video_title: str,
        num_questions: int = 5
    ) -> List[str]:
        """
        Generate contextually relevant questions from a video transcript.
        
        Args:
            transcript: The full or partial transcript text
            video_title: Title of the video for context
            num_questions: Number of questions to generate (default: 5)
            
        Returns:
            List of suggested questions
        """
        # Truncate transcript if too long (keep first ~3000 chars for context)
        truncated_transcript = transcript[:3000] if len(transcript) > 3000 else transcript

        prompt = f"""You are analyzing a video titled "{video_title}".

Based on the following transcript excerpt, generate {num_questions} interesting and diverse questions that viewers might want to ask about this video content.

Transcript:
{truncated_transcript}

Generate {num_questions} specific, answerable questions that:
1. Cover different topics/aspects of the video
2. Are natural questions a viewer would ask
3. Can be answered from the video content
4. Range from specific details to broader concepts
5. Are clear and concise (one sentence each)

Return ONLY the questions, one per line, without numbering or extra formatting."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates relevant questions about video content. Output only the questions, one per line."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content.strip()
            
            # Parse questions (split by newlines, filter empty)
            questions = [
                q.strip().lstrip('0123456789.-) ') 
                for q in content.split('\n') 
                if q.strip()
            ]
            
            # Ensure we have the requested number (or close to it)
            return questions[:num_questions] if questions else []

        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []


# Singleton instance
question_generator_service = QuestionGeneratorService()
