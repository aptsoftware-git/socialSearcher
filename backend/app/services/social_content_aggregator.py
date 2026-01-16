"""
Social Content Aggregator - Routes requests to appropriate services and handles caching.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import hashlib
from loguru import logger

from app.settings import settings
from app.models import SocialFullContent, EventData
from app.services.youtube_content_service import YouTubeContentService
from app.services.twitter_content_service import TwitterContentService
from app.services.facebook_content_service import FacebookContentService
from app.services.instagram_content_service import InstagramContentService
from app.services.google_content_service import GoogleContentService


class SocialContentAggregator:
    """Aggregates and caches social media content from various platforms."""
    
    def __init__(self):
        """Initialize aggregator with platform services."""
        self.youtube_service = YouTubeContentService()
        self.twitter_service = TwitterContentService()
        self.facebook_service = FacebookContentService()
        self.instagram_service = InstagramContentService()
        self.google_service = GoogleContentService()
        
        # In-memory cache (in production, use Redis)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._analysis_cache: Dict[str, Dict[str, Any]] = {}  # Cache for AI analysis results
        self.cache_duration_hours = settings.cache_social_content_hours if hasattr(settings, 'cache_social_content_hours') else 24
        
    def _get_cache_key(self, url: str, platform: str) -> str:
        """Generate cache key from URL and platform."""
        return hashlib.md5(f"{platform}:{url}".encode()).hexdigest()
    
    def _get_analysis_cache_key(self, url: str, llm_model: Optional[str] = None) -> str:
        """Generate cache key for AI analysis (includes model to allow different analyses)."""
        model_suffix = f":{llm_model}" if llm_model else ""
        return hashlib.md5(f"analysis:{url}{model_suffix}".encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[SocialFullContent]:
        """Retrieve content from cache if not expired."""
        # logger.info(f"_get_from_cache called with key: {cache_key}")
        # logger.info(f"Total cache entries: {len(self._cache)}")
        
        if cache_key not in self._cache:
            # logger.warning(f"Cache key not in cache. Available keys: {list(self._cache.keys())[:3]}")
            return None
        
        cached_data = self._cache[cache_key]
        expires_at = cached_data.get('expires_at')
        
        if expires_at and datetime.utcnow() > expires_at:
            # Cache expired, remove it
            del self._cache[cache_key]
            # logger.info(f"Cache expired for key: {cache_key}")
            return None
        
        logger.info(f"Cache hit for key: {cache_key}")
        content = SocialFullContent(**cached_data['content'])
        content.cached = True
        content.cache_expires_at = expires_at
        return content
    
    def _save_to_cache(self, cache_key: str, content: SocialFullContent):
        """Save content to cache with expiration."""
        expires_at = datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
        
        self._cache[cache_key] = {
            'content': content.model_dump(mode='json'),
            'expires_at': expires_at,
            'cached_at': datetime.utcnow()
        }
        
        logger.info(f"Saved content to cache - Key: {cache_key}, URL: {content.url[:60]}..., Platform: {content.platform}, Expires: {expires_at}")
    
    def get_cached_analysis(self, url: str, llm_model: Optional[str] = None) -> Optional[EventData]:
        """Retrieve cached AI analysis result."""
        cache_key = self._get_analysis_cache_key(url, llm_model)
        logger.info(f"Looking for analysis with cache_key: {cache_key} (url: {url[:60]}..., model: {llm_model})")
        
        if cache_key not in self._analysis_cache:
            logger.info(f"Cache key not found. Available keys: {list(self._analysis_cache.keys())[:5]}...")
            return None
        
        cached_data = self._analysis_cache[cache_key]
        expires_at = cached_data.get('expires_at')
        
        if expires_at and datetime.utcnow() > expires_at:
            # Cache expired, remove it
            del self._analysis_cache[cache_key]
            logger.debug(f"Analysis cache expired for key: {cache_key}")
            return None
        
        logger.info(f"Analysis cache hit for URL: {url[:60]}...")
        return EventData(**cached_data['event'])
    
    def save_analysis_to_cache(self, url: str, event: EventData, llm_model: Optional[str] = None):
        """Save AI analysis result to cache."""
        cache_key = self._get_analysis_cache_key(url, llm_model)
        expires_at = datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
        
        self._analysis_cache[cache_key] = {
            'event': event.model_dump(mode='json'),
            'expires_at': expires_at,
            'cached_at': datetime.utcnow()
        }
        
        logger.info(f"Saved analysis to cache - Key: {cache_key}, URL: {url[:60]}..., Model: {llm_model}, Title: {event.title[:50] if event.title else 'N/A'}...")
    
    def check_cache_status(self, url: str, platform: str, llm_model: Optional[str] = None) -> Dict[str, bool]:
        """
        Check if content and AI analysis are cached for a URL.
        
        Args:
            url: Social media URL
            platform: Platform name
            llm_model: LLM model used for analysis
            
        Returns:
            Dict with 'content_cached' and 'analysis_cached' booleans
        """
        content_cache_key = self._get_cache_key(url, platform)
        analysis_cache_key = self._get_analysis_cache_key(url, llm_model)
        
        # Check content cache
        content_cached = False
        if content_cache_key in self._cache:
            cached_data = self._cache[content_cache_key]
            expires_at = cached_data.get('expires_at')
            if not expires_at or datetime.utcnow() <= expires_at:
                content_cached = True
        
        # Check analysis cache
        analysis_cached = False
        if analysis_cache_key in self._analysis_cache:
            cached_data = self._analysis_cache[analysis_cache_key]
            expires_at = cached_data.get('expires_at')
            if not expires_at or datetime.utcnow() <= expires_at:
                analysis_cached = True
        
        return {
            'content_cached': content_cached,
            'analysis_cached': analysis_cached
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """
        Detect social media platform from URL.
        
        Returns:
            Platform name: 'facebook', 'twitter', 'youtube', 'instagram', or None
        """
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'facebook.com' in url_lower or 'fb.com' in url_lower:
            return 'facebook'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        
        return None
    
    async def fetch_content(
        self,
        url: str,
        platform: Optional[str] = None,
        force_refresh: bool = False,
        llm_model: Optional[str] = None
    ) -> Optional[SocialFullContent]:
        """
        Fetch full content from social media URL.
        
        Args:
            url: Social media post/tweet/video URL
            platform: Platform name (auto-detected if None)
            force_refresh: Skip cache and fetch fresh content
            llm_model: LLM model name to check for cached analysis
            
        Returns:
            SocialFullContent or None if error
        """
        # Auto-detect platform if not provided
        if not platform:
            platform = self.detect_platform(url)
            if not platform:
                logger.error(f"Could not detect platform from URL: {url}")
                return None
        
        platform = platform.lower()
        logger.info(f"Fetching {platform} content from: {url[:80]}...")
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cache_key = self._get_cache_key(url, platform)
            logger.info(f"🔑 Looking for content with cache_key: {cache_key}")
            cached_content = self._get_from_cache(cache_key)
            if cached_content:
                logger.info(f"CACHE HIT - Returning cached {platform} content for URL: {url[:60]}...")
                logger.info(f"Looking for analysis with llm_model: {llm_model}")
                
                # Check if we have cached analysis and attach it to content
                cached_analysis = self.get_cached_analysis(url, llm_model)
                if cached_analysis:
                    # logger.info(f"Attaching cached analysis to content: {cached_analysis.title[:50] if cached_analysis.title else 'N/A'}...")
                    cached_content.extracted_event = cached_analysis
                else:
                    pass  # logger.warning(f"No cached analysis found for URL with model: {llm_model}")
                    # Try without model (for backward compatibility)
                    cached_analysis_no_model = self.get_cached_analysis(url, None)
                    if cached_analysis_no_model:
                        # logger.info(f"Found analysis without model: {cached_analysis_no_model.title[:50] if cached_analysis_no_model.title else 'N/A'}...")
                        cached_content.extracted_event = cached_analysis_no_model
                
                return cached_content
            else:
                pass  # logger.warning(f"CACHE MISS - No cached content found. Available cache keys (first 5): {list(self._cache.keys())[:5]}")
        else:
            pass  # logger.info(f"Force refresh enabled - skipping cache lookup")
        
        # Fetch from appropriate service
        content = None
        
        try:
            if platform == 'youtube':
                content = await self.youtube_service.get_video_content(url)
            elif platform == 'twitter':
                content = await self.twitter_service.get_tweet_content(url)
            elif platform == 'facebook':
                # Note: Facebook Graph API requires "Page Public Content Access" permission
                # which needs Facebook App Review. Without it, you can only access:
                # - Your own posts
                # - Pages you manage
                # - Posts you're tagged in
                # For public posts from pages you don't own, App Review is required.
                # See doc/FACEBOOK_ACCESS_LIMITATIONS.md for details.
                content = await self.facebook_service.get_post_content(url)
                if not content:
                    logger.warning(
                        "Facebook content fetch failed. This is expected without 'Page Public Content Access' permission. "
                        "Submit your app for Facebook App Review to access public posts. "
                        "See doc/FACEBOOK_ACCESS_LIMITATIONS.md for details."
                    )
            elif platform == 'instagram':
                content = await self.instagram_service.get_post_content(url)
            elif platform == 'google':
                content = await self.google_service.get_content(url)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return None
            
            # Cache successful fetch
            if content:
                cache_key = self._get_cache_key(url, platform)
                self._save_to_cache(cache_key, content)
                logger.debug(f"Successfully fetched and cached {platform} content")
            else:
                logger.warning(f"No content retrieved for {platform} URL: {url}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching {platform} content: {e}", exc_info=True)
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_cached = len(self._cache)
        total_analysis_cached = len(self._analysis_cache)
        expired = 0
        analysis_expired = 0
        
        now = datetime.utcnow()
        for cached_data in self._cache.values():
            if cached_data.get('expires_at') and now > cached_data['expires_at']:
                expired += 1
        
        for cached_data in self._analysis_cache.values():
            if cached_data.get('expires_at') and now > cached_data['expires_at']:
                analysis_expired += 1
        
        return {
            'total_cached': total_cached,
            'active_cached': total_cached - expired,
            'expired': expired,
            'total_analysis_cached': total_analysis_cached,
            'active_analysis_cached': total_analysis_cached - analysis_expired,
            'analysis_expired': analysis_expired,
            'cache_duration_hours': self.cache_duration_hours
        }
    
    def clear_cache(self, platform: Optional[str] = None, clear_analysis: bool = False):
        """Clear cache for specific platform or all."""
        if platform:
            # Remove cache entries for specific platform
            keys_to_remove = [
                key for key, data in self._cache.items()
                if platform in data.get('content', {}).get('platform', '')
            ]
            for key in keys_to_remove:
                del self._cache[key]
            logger.info(f"Cleared {len(keys_to_remove)} cached entries for {platform}")
        else:
            # Clear all cache
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared all {count} cached entries")
        
        if clear_analysis:
            # Clear analysis cache
            analysis_count = len(self._analysis_cache)
            self._analysis_cache.clear()
            logger.info(f"Cleared all {analysis_count} cached analysis entries")


# Global instance
social_content_aggregator = SocialContentAggregator()
