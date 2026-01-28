"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import ingest, query
from backend.database.db import init_db
from backend.app.models import HealthResponse
from backend.services.vector_store import vector_store
from backend.database.db import db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Video Content Search API",
    description="Multi-Modal RAG system for searching YouTube video transcripts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up Video Content Search API...")
    await init_db()
    logger.info("Database initialized")
    logger.info("Services ready")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Video Content Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ingest": "/ingest",
            "query": "/query"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check system health"""
    chroma_connected = vector_store.check_health()
    database_connected = await db.check_health()
    
    status = "healthy" if (chroma_connected and database_connected) else "degraded"
    
    return HealthResponse(
        status=status,
        chroma_connected=chroma_connected,
        database_connected=database_connected
    )


# Include routers
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(query.router, tags=["Query"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
