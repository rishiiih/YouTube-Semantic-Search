"""
Video ingestion endpoint
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.app.models import IngestRequest, IngestResponse, IngestionStatus
from backend.database.db import db
from backend.services.whisper_service import whisper_service
from backend.services.chunking import chunking_service
from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.services.youtube_metadata import youtube_metadata_service
from backend.services.question_generator import question_generator_service
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import yt_dlp
import os
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter()


def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid YouTube URL")


async def get_youtube_transcript(video_id: str) -> tuple[list[dict], str, float]:
    """
    Get transcript from YouTube's official API (preferred method)
    
    Returns:
        (segments, title, duration) where segments = [{"text": str, "start": float, "end": float}, ...]
    """
    try:
        # Get transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English transcript, or the first available one
        try:
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        except:
            transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
        
        entries = transcript.fetch()
        
        # Convert to our format
        segments = []
        for entry in entries:
            segments.append({
                "text": entry['text'],
                "start": entry['start'],
                "end": entry['start'] + entry['duration']
            })
        
        # Get video metadata using yt-dlp (no download)
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
        
        logger.info(f"Retrieved YouTube transcript for {video_id} ({len(segments)} segments)")
        return segments, title, float(duration)
        
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.warning(f"No transcript available for {video_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to get transcript for {video_id}: {e}")
        raise


async def download_audio(youtube_url: str, video_id: str) -> tuple[str, str, float]:
    """
    Download audio-only from YouTube with smart segmentation for large files
    
    Returns:
        (audio_file_path, video_title, duration_seconds)
    """
    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)
    
    output_template = str(output_dir / f"{video_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'worstaudio[ext=m4a]/worstaudio/worst',  # Audio-only, smallest file
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['dash', 'hls'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            ext = info.get('ext', 'm4a')
            
        audio_path = str(output_dir / f"{video_id}.{ext}")
        
        # Check file size
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        logger.info(f"Downloaded audio: {file_size_mb:.1f}MB")
        
        return audio_path, title, float(duration)
        
    except Exception as e:
        logger.error(f"Audio download failed: {e}")
        raise


async def download_audio_segment(youtube_url: str, video_id: str, start_time: int, end_time: int, segment_num: int) -> str:
    """
    Download a specific time segment from YouTube
    
    Args:
        youtube_url: YouTube URL
        video_id: Video ID
        start_time: Start time in seconds
        end_time: End time in seconds
        segment_num: Segment number for filename
        
    Returns:
        Path to downloaded segment
    """
    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)
    
    output_path = str(output_dir / f"{video_id}_seg{segment_num}.m4a")
    
    ydl_opts = {
        'format': 'worstaudio[ext=m4a]/worstaudio/worst',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'download_ranges': lambda info_dict, ydl: [{'start_time': start_time, 'end_time': end_time}],
        'force_keyframes_at_cuts': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['dash', 'hls'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        logger.error(f"Segment download failed: {e}")
        raise


async def split_audio_with_ffmpeg(audio_path: str, video_id: str, duration: float) -> list[str]:
    """
    Split audio file into smaller segments using FFmpeg
    
    Args:
        audio_path: Path to audio file
        video_id: Video ID
        duration: Total duration in seconds
        
    Returns:
        List of paths to audio segments
    """
    import subprocess
    
    chunk_duration_minutes = 5  # 5-minute chunks to ensure under 25MB
    chunk_duration_seconds = chunk_duration_minutes * 60
    num_chunks = int(duration / chunk_duration_seconds) + (1 if duration % chunk_duration_seconds > 0 else 0)
    
    logger.info(f"Splitting {duration/60:.1f} minute file into {num_chunks} segments of {chunk_duration_minutes} minutes each")
    
    segment_paths = []
    output_dir = Path("downloads")
    
    for i in range(num_chunks):
        start_time = i * chunk_duration_seconds
        segment_duration = min(chunk_duration_seconds, duration - start_time)
        
        segment_path = str(output_dir / f"{video_id}_seg{i}.m4a")
        
        # Use FFmpeg to extract segment (audio-only, no re-encoding)
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(segment_duration),
            '-vn',  # No video
            '-acodec', 'copy',  # Copy audio codec (no re-encoding, fast)
            segment_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            segment_paths.append(segment_path)
            segment_size_mb = os.path.getsize(segment_path) / (1024 * 1024)
            logger.info(f"Created segment {i+1}/{num_chunks}: {segment_size_mb:.1f}MB")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed for segment {i}: {e.stderr}")
            raise
    
    return segment_paths


async def transcribe_with_chunking(youtube_url: str, video_id: str, duration: float, audio_path: str = None) -> list[dict]:
    """
    Transcribe video by splitting audio file into segments
    
    Args:
        youtube_url: YouTube URL
        video_id: Video ID
        duration: Video duration in seconds
        audio_path: Optional already-downloaded audio file
        
    Returns:
        List of segments with text, start, end
    """
    if audio_path:
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        
        # If file is under 25MB, transcribe directly
        if file_size_mb <= 25:
            return await whisper_service.transcribe_audio(audio_path)
        
        # File too large - split using FFmpeg
        logger.info(f"File size ({file_size_mb:.1f}MB) exceeds 25MB. Splitting with FFmpeg...")
        
        segment_paths = await split_audio_with_ffmpeg(audio_path, video_id, duration)
        os.remove(audio_path)  # Remove large file
        
        all_segments = []
        chunk_duration_seconds = 5 * 60  # 5 minutes per chunk
        
        for i, segment_path in enumerate(segment_paths):
            segment_size_mb = os.path.getsize(segment_path) / (1024 * 1024)
            logger.info(f"Transcribing segment {i+1}/{len(segment_paths)} ({segment_size_mb:.1f}MB)...")
            
            try:
                chunk_segments = await whisper_service.transcribe_audio(segment_path)
                
                # Adjust timestamps by adding offset
                offset_seconds = i * chunk_duration_seconds
                for segment in chunk_segments:
                    segment['start'] += offset_seconds
                    segment['end'] += offset_seconds
                    all_segments.append(segment)
                
                # Clean up segment file
                os.remove(segment_path)
                
            except Exception as e:
                logger.error(f"Failed to transcribe segment {i+1}: {e}")
                os.remove(segment_path)
                continue
        
        logger.info(f"Completed transcription: {len(all_segments)} total segments from {len(segment_paths)} chunks")
        return all_segments
    
    # Should not reach here
    raise ValueError("No audio path provided for chunking")


async def update_progress(video_id: str, step: str, percent: float):
    """Update ingestion progress"""
    conn = await db.get_connection()
    try:
        await conn.execute(
            """UPDATE videos SET progress_step = ?, progress_percent = ?, 
               updated_at = CURRENT_TIMESTAMP WHERE video_id = ?""",
            (step, percent, video_id)
        )
        await conn.commit()
    finally:
        await conn.close()


async def process_video_ingestion(video_id: str, youtube_url: str):
    """Background task to process video ingestion"""
    try:
        # Update status to processing
        conn = await db.get_connection()
        try:
            await conn.execute(
                "UPDATE videos SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE video_id = ?",
                (IngestionStatus.PROCESSING.value, video_id)
            )
            await conn.commit()
        finally:
            await conn.close()
        
        await update_progress(video_id, "Fetching metadata", 5)
        
        # Get metadata first
        metadata = await youtube_metadata_service.get_metadata(video_id)
        
        # Update database with metadata
        conn = await db.get_connection()
        try:
            await conn.execute(
                """UPDATE videos SET title = ?, duration = ?, thumbnail_url = ?, 
                   channel_name = ?, upload_date = ?, view_count = ? WHERE video_id = ?""",
                (metadata['title'], metadata['duration'], metadata['thumbnail_url'],
                 metadata['channel_name'], metadata['upload_date'], metadata['view_count'], video_id)
            )
            await conn.commit()
        finally:
            await conn.close()
        
        await update_progress(video_id, "Getting transcript", 15)
        
        # Step 1: Try to get YouTube transcript (fast, no download)
        logger.info(f"Attempting to get YouTube transcript for {video_id}")
        try:
            segments, title, duration = await get_youtube_transcript(video_id)
            logger.info(f"Successfully retrieved YouTube transcript for {video_id}")
        except Exception as transcript_error:
            # Fallback: Download audio and transcribe with Whisper
            logger.warning(f"Transcript unavailable, falling back to audio download: {transcript_error}")
            await update_progress(video_id, "Downloading audio", 20)
            logger.info(f"Downloading audio for {video_id}")
            audio_path, title, duration = await download_audio(youtube_url, video_id)
            
            await update_progress(video_id, "Transcribing", 40)
            logger.info(f"Transcribing audio for {video_id} (duration: {duration/60:.1f} minutes)")
            segments = await transcribe_with_chunking(youtube_url, video_id, duration, audio_path)
            
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
        
        await update_progress(video_id, "Saving transcript", 60)
        
        # Step 2: Save segments to database
        conn = await db.get_connection()
        try:
            for idx, segment in enumerate(segments):
                await conn.execute(
                    """INSERT INTO transcripts (video_id, segment_index, text, start_time, end_time)
                       VALUES (?, ?, ?, ?, ?)""",
                    (video_id, idx, segment["text"], segment["start"], segment["end"])
                )
            await conn.commit()
        finally:
            await conn.close()
        
        await update_progress(video_id, "Creating chunks", 70)
        
        # Step 3: Chunk transcript
        logger.info(f"Chunking transcript for {video_id}")
        chunks = chunking_service.chunk_transcript(segments)
        
        await update_progress(video_id, "Generating embeddings", 80)
        
        # Step 4: Generate embeddings
        logger.info(f"Generating embeddings for {video_id}")
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(texts)
        
        await update_progress(video_id, "Indexing", 90)
        
        # Step 5: Store in ChromaDB
        logger.info(f"Storing in ChromaDB for {video_id}")
        chunk_ids = await vector_store.add_chunks(video_id, chunks, embeddings)
        
        # Step 6: Store chunk metadata in database
        conn = await db.get_connection()
        try:
            for chunk, chunk_id in zip(chunks, chunk_ids):
                await conn.execute(
                    """INSERT INTO chunks (chunk_id, video_id, text, start_time, end_time, chunk_index)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (chunk_id, video_id, chunk["text"], chunk["start_time"],
                     chunk["end_time"], chunk["chunk_index"])
                )
            await conn.commit()
        finally:
            await conn.close()
        
        await update_progress(video_id, "Completed", 100)
        
        # Step 7: Generate suggested questions
        logger.info(f"Generating suggested questions for {video_id}")
        try:
            # Get first few transcript segments for context
            full_transcript = " ".join([seg["text"] for seg in segments[:50]])  # First 50 segments
            questions = question_generator_service.generate_questions(
                transcript=full_transcript,
                video_title=title,
                num_questions=5
            )
            
            # Store questions in database
            if questions:
                conn = await db.get_connection()
                try:
                    for question in questions:
                        await conn.execute(
                            """INSERT INTO question_suggestions (video_id, question)
                               VALUES (?, ?)""",
                            (video_id, question)
                        )
                    await conn.commit()
                finally:
                    await conn.close()
                logger.info(f"Stored {len(questions)} suggested questions for {video_id}")
        except Exception as e:
            logger.warning(f"Failed to generate questions for {video_id}: {e}")
        
        # Step 8: Update status to completed
        conn = await db.get_connection()
        try:
            await conn.execute(
                "UPDATE videos SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE video_id = ?",
                (IngestionStatus.COMPLETED.value, video_id)
            )
            await conn.commit()
        finally:
            await conn.close()
        
        logger.info(f"Ingestion completed for {video_id}")
        
    except Exception as e:
        logger.error(f"Ingestion failed for {video_id}: {e}")
        
        await update_progress(video_id, "Failed", 0)
        
        # Update status to failed
        conn = await db.get_connection()
        try:
            await conn.execute(
                """UPDATE videos SET status = ?, error_message = ?, 
                   updated_at = CURRENT_TIMESTAMP WHERE video_id = ?""",
                (IngestionStatus.FAILED.value, str(e), video_id)
            )
            await conn.commit()
        finally:
            await conn.close()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest a YouTube video for search
    
    Process:
    1. Extract video_id from URL
    2. Check if already ingested
    3. Create database entry
    4. Launch background ingestion task
    """
    try:
        # Extract video ID
        video_id = extract_video_id(request.youtube_url)
        
        # Check if already exists
        conn = await db.get_connection()
        try:
            cursor = await conn.execute(
                "SELECT video_id, status FROM videos WHERE video_id = ?",
                (video_id,)
            )
            existing = await cursor.fetchone()
        finally:
            await conn.close()
        
        if existing:
            return IngestResponse(
                video_id=video_id,
                youtube_url=request.youtube_url,
                status=IngestionStatus(existing[1]),
                message=f"Video already exists with status: {existing[1]}"
            )
        
        # Create new video entry
        conn = await db.get_connection()
        try:
            await conn.execute(
                """INSERT INTO videos (video_id, youtube_url, status)
                   VALUES (?, ?, ?)""",
                (video_id, request.youtube_url, IngestionStatus.PENDING.value)
            )
            await conn.commit()
        finally:
            await conn.close()
        
        # Launch background processing
        background_tasks.add_task(process_video_ingestion, video_id, request.youtube_url)
        
        return IngestResponse(
            video_id=video_id,
            youtube_url=request.youtube_url,
            status=IngestionStatus.PENDING,
            message="Video ingestion started. Check status with GET /videos/{video_id}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Ingestion failed")