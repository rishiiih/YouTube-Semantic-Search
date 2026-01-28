"""
YouTube metadata extraction service
"""
import yt_dlp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class YouTubeMetadataService:
    """Extracts metadata from YouTube videos"""
    
    @staticmethod
    async def get_metadata(video_id: str) -> Dict[str, any]:
        """
        Extract video metadata without downloading
        
        Returns:
            Dict with title, thumbnail_url, channel_name, upload_date, view_count, duration
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
                
                # Extract relevant metadata
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'thumbnail_url': info.get('thumbnail') or info.get('thumbnails', [{}])[-1].get('url'),
                    'channel_name': info.get('uploader') or info.get('channel'),
                    'upload_date': info.get('upload_date'),  # Format: YYYYMMDD
                    'view_count': info.get('view_count'),
                    'duration': float(info.get('duration', 0)),
                }
                
                # Format upload_date if available
                if metadata['upload_date']:
                    try:
                        date_str = metadata['upload_date']
                        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        metadata['upload_date'] = formatted_date
                    except:
                        pass
                
                logger.info(f"Retrieved metadata for {video_id}: {metadata['title']}")
                return metadata
                
        except Exception as e:
            logger.error(f"Failed to get metadata for {video_id}: {e}")
            return {
                'title': 'Unknown',
                'thumbnail_url': None,
                'channel_name': None,
                'upload_date': None,
                'view_count': None,
                'duration': 0.0,
            }


# Singleton instance
youtube_metadata_service = YouTubeMetadataService()
