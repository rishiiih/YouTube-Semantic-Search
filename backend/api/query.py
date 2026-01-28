"""
Query endpoint for searching video content
"""
from fastapi import APIRouter, HTTPException
from backend.app.models import QueryRequest, QueryResponse, Timestamp, VideoInfo, VideoListResponse
from backend.database.db import db
from backend.services.embedding_service import embedding_service
from backend.services.vector_store import vector_store
from backend.services.llm_service import llm_service
import re
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def extract_timestamps_from_answer(answer: str) -> list[str]:
    """Extract [MM:SS] timestamps from answer text"""
    pattern = r'\[(\d{1,2}):(\d{2})\]'
    matches = re.findall(pattern, answer)
    
    timestamps = []
    for minutes, seconds in matches:
        time_str = f"{int(minutes):02d}:{int(seconds):02d}"
        if time_str not in timestamps:
            timestamps.append(time_str)
    
    return timestamps


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


@router.post("/query", response_model=QueryResponse)
async def query_video(request: QueryRequest):
    """
    Query a video with a natural language question
    
    Process:
    1. Verify video exists and is completed
    2. Generate query embedding
    3. Search ChromaDB for relevant chunks
    4. Generate answer with LLM
    5. Extract and format timestamps
    """
    try:
        video_id = request.video_id
        question = request.question
        
        # Check video exists and is completed
        conn = await db.get_connection()
        try:
            cursor = await conn.execute(
                "SELECT video_id, status, youtube_url FROM videos WHERE video_id = ?",
                (video_id,)
            )
            video = await cursor.fetchone()
        finally:
            await conn.close()
        
        if not video:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
        
        if video[1] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Video is not ready for querying. Status: {video[1]}"
            )
        
        youtube_url = video[2]
        
        # Generate query embedding
        logger.info(f"Processing query for video {video_id}: {question}")
        query_embedding = embedding_service.generate_embedding(question)
        
        # Search ChromaDB
        results = await vector_store.query_similar(
            query_embedding=query_embedding,
            video_id=video_id
        )
        
        if not results['ids'][0]:
            return QueryResponse(
                answer="No relevant content found in the video for your question.",
                timestamps=[],
                video_id=video_id,
                sources_used=0
            )
        
        # Get chunk metadata from database
        chunk_ids = results['ids'][0]
        conn = await db.get_connection()
        try:
            placeholders = ','.join('?' * len(chunk_ids))
            cursor = await conn.execute(
                f"SELECT chunk_id, text, start_time, end_time FROM chunks WHERE chunk_id IN ({placeholders})",
                chunk_ids
            )
            chunks = await cursor.fetchall()
        finally:
            await conn.close()
        
        # Format chunks for LLM
        context_chunks = [
            {
                "text": chunk[1],
                "start_time": chunk[2],
                "end_time": chunk[3]
            }
            for chunk in chunks
        ]
        
        # Generate answer with LLM
        answer = await llm_service.generate_answer(question, context_chunks)
        
        # Extract timestamps from answer
        timestamp_strings = extract_timestamps_from_answer(answer)
        
        # Create timestamp objects with URLs
        timestamps = []
        for ts_str in timestamp_strings:
            # Parse MM:SS to seconds
            parts = ts_str.split(':')
            seconds = int(parts[0]) * 60 + int(parts[1])
            
            # Find matching chunk for context
            matching_chunk = None
            for chunk in context_chunks:
                if chunk["start_time"] <= seconds <= chunk["end_time"]:
                    matching_chunk = chunk
                    break
            
            # Default to first chunk if no exact match
            if not matching_chunk and context_chunks:
                matching_chunk = context_chunks[0]
            
            context_text = matching_chunk["text"][:100] + "..." if matching_chunk else ""
            
            timestamps.append(Timestamp(
                time=ts_str,
                seconds=seconds,
                url=f"{youtube_url}&t={seconds}",
                text=context_text
            ))
        
        return QueryResponse(
            answer=answer,
            timestamps=timestamps,
            video_id=video_id,
            sources_used=len(context_chunks)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing failed")


@router.get("/videos/{video_id}", response_model=VideoInfo)
async def get_video(video_id: str):
    """Get video information by ID"""
    conn = await db.get_connection()
    try:
        cursor = await conn.execute(
            "SELECT video_id, youtube_url, title, duration, status, created_at FROM videos WHERE video_id = ?",
            (video_id,)
        )
        video = await cursor.fetchone()
    finally:
        await conn.close()
    
    if not video:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
    
    return VideoInfo(
        video_id=video[0],
        youtube_url=video[1],
        title=video[2] or "Unknown",
        duration=video[3] or 0.0,
        status=video[4],
        created_at=video[5]
    )


@router.get("/videos", response_model=VideoListResponse)
async def list_videos():
    """List all ingested videos"""
    conn = await db.get_connection()
    try:
        cursor = await conn.execute(
            "SELECT video_id, youtube_url, title, duration, status, created_at FROM videos ORDER BY created_at DESC"
        )
        videos = await cursor.fetchall()
    finally:
        await conn.close()
    
    video_list = [
        VideoInfo(
            video_id=v[0],
            youtube_url=v[1],
            title=v[2] or "Unknown",
            duration=v[3] or 0.0,
            status=v[4],
            created_at=v[5]
        )
        for v in videos
    ]
    
    return VideoListResponse(
        videos=video_list,
        total=len(video_list)
    )
