"""
YouTube Content Service - Fetch full video details using YouTube Data API v3.
"""

from typing import Optional, Dict, Any
import re
import httpx
from datetime import datetime, timedelta
from loguru import logger

from app.settings import settings
from app.models import (
    SocialFullContent,
    SocialContentAuthor,
    SocialContentMedia,
    SocialContentEngagement
)


class YouTubeContentService:
    """Service for fetching full YouTube video content."""
    
    def __init__(self):
        """Initialize YouTube service with API key."""
        self.api_key = settings.youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def parse_duration(self, duration: str) -> int:
        """
        Parse ISO 8601 duration to seconds.
        
        Example: PT1H2M10S -> 3730 seconds
        """
        if not duration:
            return 0
            
        # Remove PT prefix
        duration = duration.replace('PT', '')
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        if 'H' in duration:
            hours_match = re.search(r'(\d+)H', duration)
            if hours_match:
                hours = int(hours_match.group(1))
        
        # Extract minutes
        if 'M' in duration:
            minutes_match = re.search(r'(\d+)M', duration)
            if minutes_match:
                minutes = int(minutes_match.group(1))
        
        # Extract seconds
        if 'S' in duration:
            seconds_match = re.search(r'(\d+)S', duration)
            if seconds_match:
                seconds = int(seconds_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def get_first_video_from_playlist(self, playlist_id: str) -> Optional[str]:
        """
        Get the first video ID from a YouTube playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            First video ID from playlist or None if error
        """
        if not self.api_key:
            logger.error("YouTube API key not configured")
            return None
        
        logger.info(f"Fetching first video from playlist: {playlist_id}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/playlistItems",
                    params={
                        'key': self.api_key,
                        'playlistId': playlist_id,
                        'part': 'contentDetails',
                        'maxResults': 1
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('items') and len(data['items']) > 0:
                    video_id = data['items'][0]['contentDetails']['videoId']
                    logger.info(f"Found first video in playlist: {video_id}")
                    return video_id
                else:
                    logger.warning(f"No videos found in playlist: {playlist_id}")
                    return None
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching playlist {playlist_id}: {e.response.status_code}")
            if e.response.status_code == 403:
                logger.error("YouTube API quota exceeded or invalid API key")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching playlist {playlist_id}: {e}", exc_info=True)
            return None
    
    async def get_video_content(self, url: str) -> Optional[SocialFullContent]:
        """
        Fetch full video details from YouTube Data API.
        
        Args:
            url: YouTube video URL
            
        Returns:
            SocialFullContent with video details or None if error
        """
        if not self.api_key:
            logger.error("YouTube API key not configured")
            return None
        
        # Track if this is from a playlist
        is_from_playlist = False
        playlist_id = None
        
        # Check if this is a playlist URL
        if 'playlist?' in url or ('list=' in url and 'watch?' not in url):
            # Pure playlist URL - extract playlist ID and get first video
            playlist_match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
            if playlist_match:
                playlist_id = playlist_match.group(1)
                is_from_playlist = True
                logger.info(f"Detected playlist URL, fetching first video from playlist: {playlist_id}")
                
                # Get first video from playlist
                video_id = await self.get_first_video_from_playlist(playlist_id)
                if not video_id:
                    logger.error(f"Could not get first video from playlist: {playlist_id}")
                    return None
            else:
                logger.error(f"Could not extract playlist ID from URL: {url}")
                return None
        elif 'watch?' in url and 'list=' in url:
            # Video URL with playlist parameter (e.g., watch?v=VIDEO_ID&list=PLAYLIST_ID)
            # Extract video ID from playlist URL
            match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
            if match:
                video_id = match.group(1)
                logger.info(f"Extracting video {video_id} from playlist URL")
                # Also extract playlist ID
                playlist_match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
                if playlist_match:
                    playlist_id = playlist_match.group(1)
                    is_from_playlist = True
            else:
                logger.error(f"Could not extract video ID from playlist URL: {url}")
                return None
        else:
            # Extract video ID from regular video URL
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error(f"Could not extract video ID from URL: {url}")
                return None
        
        logger.info(f"Fetching YouTube video: {video_id}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch video details
                response = await client.get(
                    f"{self.base_url}/videos",
                    params={
                        'key': self.api_key,
                        'id': video_id,
                        'part': 'snippet,contentDetails,statistics'
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get('items'):
                    logger.warning(f"No video found for ID: {video_id}")
                    return None
                
                video_data = data['items'][0]
                snippet = video_data.get('snippet', {})
                content_details = video_data.get('contentDetails', {})
                statistics = video_data.get('statistics', {})
                
                # Parse published date
                published_at_str = snippet.get('publishedAt', '')
                try:
                    posted_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                except:
                    posted_at = datetime.utcnow()
                
                # Parse duration
                duration_iso = content_details.get('duration', 'PT0S')
                duration_seconds = self.parse_duration(duration_iso)
                
                # Build author info
                author = SocialContentAuthor(
                    name=snippet.get('channelTitle', 'Unknown'),
                    username=snippet.get('channelId', ''),
                    profile_url=f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
                    verified=False  # YouTube doesn't provide verified status in basic API
                )
                
                # Build media (thumbnail)
                thumbnails = snippet.get('thumbnails', {})
                media = []
                
                # Get best quality thumbnail
                for quality in ['maxres', 'high', 'medium', 'default']:
                    if quality in thumbnails:
                        thumb = thumbnails[quality]
                        media.append(SocialContentMedia(
                            type='video',
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            thumbnail_url=thumb.get('url'),
                            width=thumb.get('width'),
                            height=thumb.get('height'),
                            duration=duration_seconds
                        ))
                        break
                
                # Build engagement metrics
                engagement = SocialContentEngagement(
                    likes=int(statistics.get('likeCount', 0)),
                    comments=int(statistics.get('commentCount', 0)),
                    shares=0,  # YouTube doesn't provide share count
                    views=int(statistics.get('viewCount', 0))
                )
                
                # Build full content
                content = SocialFullContent(
                    platform='youtube',
                    content_type='video',
                    url=f"https://www.youtube.com/watch?v={video_id}",  # Use clean video URL
                    platform_id=video_id,
                    text=snippet.get('description', ''),
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    author=author,
                    posted_at=posted_at,
                    media=media,
                    engagement=engagement,
                    platform_data={
                        'video_id': video_id,
                        'channel_id': snippet.get('channelId'),
                        'category_id': snippet.get('categoryId'),
                        'tags': snippet.get('tags', []),
                        'duration_seconds': duration_seconds,
                        'definition': content_details.get('definition', 'sd'),
                        'caption': content_details.get('caption', 'false'),
                        'licensed_content': content_details.get('licensedContent', False),
                        'is_from_playlist': is_from_playlist,
                        'playlist_id': playlist_id,
                        'original_url': url,  # Keep original URL for reference
                    }
                )
                
                logger.info(f"Successfully fetched YouTube video: {video_id}")
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching YouTube video {video_id}: {e.response.status_code}")
            if e.response.status_code == 403:
                logger.error("YouTube API quota exceeded or invalid API key")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching YouTube video {video_id}: {e}", exc_info=True)
            return None
