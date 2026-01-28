from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum


class IngestionStatus(str, Enum):
    """Video ingestion status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Ingestion Models
class IngestRequest(BaseModel):
    """Request to ingest a YouTube video"""
    youtube_url: str = Field(..., description="YouTube video URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }


class IngestResponse(BaseModel):
    """Response after initiating video ingestion"""
    video_id: str = Field(..., description="Unique video identifier")
    youtube_url: str
    title: Optional[str] = None
    duration: Optional[float] = None
    thumbnail_url: Optional[str] = None
    channel_name: Optional[str] = None
    status: IngestionStatus
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Tutorial: Building REST APIs",
                "duration": 1234.5,
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "channel_name": "Tech Channel",
                "status": "completed",
                "message": "Video ingested successfully"
            }
        }


# Query Models
class QueryRequest(BaseModel):
    """Request to query a video"""
    video_id: str = Field(..., description="Video ID to query")
    question: str = Field(..., min_length=3, description="Natural language question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "question": "How do I fix the CORS error?"
            }
        }


class Timestamp(BaseModel):
    """Video timestamp with clickable link"""
    time: str = Field(..., description="Formatted time (MM:SS)")
    seconds: int = Field(..., description="Time in seconds")
    url: str = Field(..., description="YouTube URL with timestamp parameter")
    text: str = Field(..., description="Context text at this timestamp")


class QueryResponse(BaseModel):
    """Response to a query with answer and timestamps"""
    answer: str = Field(..., description="Natural language answer from LLM")
    timestamps: List[Timestamp] = Field(default_factory=list, description="Relevant video timestamps")
    video_id: str
    sources_used: int = Field(..., description="Number of chunks retrieved")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To fix CORS errors, you need to configure your backend...",
                "timestamps": [
                    {
                        "time": "05:23",
                        "seconds": 323,
                        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=323",
                        "text": "Now let's add CORS middleware..."
                    }
                ],
                "video_id": "dQw4w9WgXcQ",
                "sources_used": 3
            }
        }


# Video Info Models
class VideoInfo(BaseModel):
    """Video metadata"""
    video_id: str
    youtube_url: str
    title: str
    duration: float
    thumbnail_url: Optional[str] = None
    channel_name: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    status: IngestionStatus
    progress_step: Optional[str] = None
    progress_percent: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """List of ingested videos"""
    videos: List[VideoInfo]
    total: int


class QuestionSuggestion(BaseModel):
    """AI-generated question suggestion"""
    question: str
    display_order: int = 0


class VideoWithSuggestions(VideoInfo):
    """Video info with suggested questions"""
    suggestions: List[QuestionSuggestion] = Field(default_factory=list)


# Error Models
class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Video not found",
                "detail": "No video with ID 'abc123' exists in the database"
            }
        }


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    chroma_connected: bool
    database_connected: bool
