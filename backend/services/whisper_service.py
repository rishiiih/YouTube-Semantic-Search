"""
Whisper transcription service using Groq API
"""
from typing import List, Dict
from groq import AsyncGroq
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class WhisperService:
    """Handles audio transcription using Groq Whisper Large V3"""
    
    def __init__(self):
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of Groq client"""
        if self._client is None:
            from groq import AsyncGroq
            self._client = AsyncGroq(api_key=settings.groq_api_key)
        return self._client
    
    async def transcribe_audio(self, audio_file_path: str) -> List[Dict]:
        """
        Transcribe audio file using Groq Whisper Large V3 with timestamps
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            List of segments with text, start_time, end_time
            [
                {"text": "...", "start": 0.0, "end": 5.2},
                {"text": "...", "start": 5.2, "end": 10.8},
                ...
            ]
        """
        try:
            import os
            
            # Check file size (Whisper API limit is 25MB)
            file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
            if file_size_mb > 25:
                raise ValueError(f"File size ({file_size_mb:.1f}MB) exceeds Whisper API limit of 25MB. Please use a shorter video or extract audio-only format.")
            
            logger.info(f"Transcribing audio file: {audio_file_path} ({file_size_mb:.1f}MB)")
            
            client = self._get_client()
            
            with open(audio_file_path, "rb") as audio_file:
                # Groq Whisper Large V3 - fast and free
                response = await client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            # Handle both dict and object responses
            if isinstance(response, dict):
                response_dict = response
            else:
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else vars(response)
            
            # Extract segments with timestamps
            segments = []
            if 'segments' in response_dict and response_dict['segments']:
                for segment in response_dict['segments']:
                    segments.append({
                        "text": segment['text'].strip(),
                        "start": segment['start'],
                        "end": segment['end']
                    })
            else:
                # Fallback: if no segments, create single segment from full text
                text = response_dict.get('text', '')
                segments.append({
                    "text": text,
                    "start": 0.0,
                    "end": 0.0  # Unknown duration
                })
            
            logger.info(f"Transcription complete: {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise


# Singleton instance
whisper_service = WhisperService()
