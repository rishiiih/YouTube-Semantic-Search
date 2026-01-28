"""
Clean up a failed video ingestion
Run: python cleanup_video.py UISjk-adxSo
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.database.db import db
from backend.services.vector_store import vector_store


async def cleanup_video(video_id: str):
    """Delete all data for a video"""
    print(f"Cleaning up video: {video_id}")
    
    # Delete from database
    conn = await db.get_connection()
    try:
        await conn.execute("DELETE FROM chunks WHERE video_id = ?", (video_id,))
        await conn.execute("DELETE FROM transcripts WHERE video_id = ?", (video_id,))
        await conn.execute("DELETE FROM videos WHERE video_id = ?", (video_id,))
        await conn.commit()
        print(f"✓ Deleted from database")
    finally:
        await conn.close()
    
    # Delete from ChromaDB
    try:
        await vector_store.delete_video_chunks(video_id)
        print(f"✓ Deleted from ChromaDB")
    except Exception as e:
        print(f"⚠ ChromaDB cleanup: {e}")
    
    print(f"✓ Cleanup complete for {video_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleanup_video.py <video_id>")
        sys.exit(1)
    
    video_id = sys.argv[1]
    asyncio.run(cleanup_video(video_id))
