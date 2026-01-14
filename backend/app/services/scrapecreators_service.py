"""
ScrapeCreators Third-Party API Service
Documentation: https://docs.scrapecreators.com/
"""

import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class ScrapeCreatorsService:
    """Service for fetching social media content using ScrapeCreators API."""
    
    def __init__(self):
        """Initialize ScrapeCreators service."""
        self.api_key = settings.scrapecreators_api_key
        self.base_url = "https://api.scrapecreators.com"
        self.timeout = 30  # 30 seconds timeout
        
        if not self.api_key:
            logger.warning("⚠️ ScrapeCreators API key not configured. Set SCRAPECREATORS_API_KEY in .env")
    
    async def get_twitter_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Twitter/X tweet content using ScrapeCreators API.
        
        Args:
            url: Tweet URL (e.g., https://twitter.com/user/status/123456789)
        
        Returns:
            Formatted content dict or None on error
        """
        if not self.api_key:
            logger.error("❌ ScrapeCreators API key not configured")
            return None
        
        try:
            logger.info(f"Fetching Twitter content via ScrapeCreators: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/twitter/tweet",
                    params={"url": url},
                    headers={"x-api-key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if data has "data" key (nested) or direct keys
                    if "data" in data:
                        logger.debug(f"Nested 'data' found, keys: {list(data['data'].keys())[:15]}")
                        actual_data = data["data"]
                    else:
                        logger.debug(f"Direct keys found (no nesting)")
                        actual_data = data
                    
                    # Log author-related keys for debugging
                    if "user" in actual_data:
                        logger.debug(f"Has 'user' key with keys: {list(actual_data['user'].keys())[:10] if isinstance(actual_data['user'], dict) else 'not a dict'}")
                    if "author" in actual_data:
                        logger.debug(f"Has 'author' key: {actual_data['author']}")
                    if "core" in actual_data:
                        logger.debug(f"Has 'core' key")
                    if "legacy" in actual_data:
                        logger.debug(f"Has 'legacy' key")
                        
                    return self._format_twitter_content(actual_data, url)
                elif response.status_code == 401:
                    logger.error("❌ ScrapeCreators: Invalid API key")
                    return None
                elif response.status_code == 402:
                    logger.error("❌ ScrapeCreators: Insufficient credits")
                    return None
                else:
                    logger.error(f"❌ ScrapeCreators API error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout fetching Twitter content from ScrapeCreators")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching Twitter content from ScrapeCreators: {e}")
            return None
    
    async def get_facebook_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Facebook post content using ScrapeCreators API.
        
        Args:
            url: Facebook post URL
        
        Returns:
            Formatted content dict or None on error
        """
        if not self.api_key:
            logger.error("❌ ScrapeCreators API key not configured")
            return None
        
        try:
            logger.info(f"Fetching Facebook content via ScrapeCreators: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/facebook/post",
                    params={"url": url},
                    headers={"x-api-key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_facebook_content(data, url)
                elif response.status_code == 401:
                    logger.error("❌ ScrapeCreators: Invalid API key")
                    return None
                elif response.status_code == 402:
                    logger.error("❌ ScrapeCreators: Insufficient credits")
                    return None
                else:
                    logger.error(f"❌ ScrapeCreators API error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout fetching Facebook content from ScrapeCreators")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching Facebook content from ScrapeCreators: {e}")
            return None
    
    async def get_instagram_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Instagram post/reel content using ScrapeCreators API.
        
        Args:
            url: Instagram post URL
        
        Returns:
            Formatted content dict or None on error
        """
        if not self.api_key:
            logger.error("❌ ScrapeCreators API key not configured")
            return None
        
        try:
            logger.info(f"Fetching Instagram content via ScrapeCreators: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/instagram/post",
                    params={"url": url},
                    headers={"x-api-key": self.api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_instagram_content(data, url)
                elif response.status_code == 401:
                    logger.error("❌ ScrapeCreators: Invalid API key")
                    return None
                elif response.status_code == 402:
                    logger.error("❌ ScrapeCreators: Insufficient credits")
                    return None
                else:
                    logger.error(f"❌ ScrapeCreators API error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout fetching Instagram content from ScrapeCreators")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching Instagram content from ScrapeCreators: {e}")
            return None
    
    def _format_twitter_content(self, data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Format ScrapeCreators Twitter response to match our standard format.
        
        Args:
            data: Raw ScrapeCreators API response
            url: Original tweet URL
        
        Returns:
            Formatted content dict
        """
        try:
            # Log the raw data structure for debugging
            logger.debug(f"Raw ScrapeCreators Twitter data keys: {list(data.keys())}")
            if "core" in data:
                logger.debug(f"core keys: {list(data['core'].keys())}")
            if "legacy" in data:
                logger.debug(f"legacy keys: {list(data['legacy'].keys())[:10]}...")  # First 10 keys
            
            legacy = data.get("legacy", {})
            user_result = data.get("core", {}).get("user_results", {}).get("result", {})
            user_legacy = user_result.get("legacy", {})
            user_core = user_result.get("core", {})  # Name and screen_name are here!
            
            logger.debug(f"user_legacy keys: {list(user_legacy.keys()) if user_legacy else 'EMPTY'}")
            logger.debug(f"user_core keys: {list(user_core.keys()) if user_core else 'EMPTY'}")
            
            # Extract tweet text
            text = legacy.get("full_text", "")
            
            # Extract media (images/videos)
            media = []
            entities = legacy.get("entities", {})
            extended_entities = legacy.get("extended_entities", {})
            
            media_list = extended_entities.get("media", entities.get("media", []))
            for m in media_list:
                media_type = m.get("type")
                if media_type == "photo":
                    media.append({
                        "type": "image",
                        "url": m.get("media_url_https", m.get("media_url", ""))
                    })
                elif media_type == "video" or media_type == "animated_gif":
                    # Get highest quality video
                    video_variants = m.get("video_info", {}).get("variants", [])
                    best_video = max(
                        (v for v in video_variants if v.get("content_type") == "video/mp4"),
                        key=lambda v: v.get("bitrate", 0),
                        default=None
                    )
                    if best_video:
                        media.append({
                            "type": "video",
                            "url": best_video.get("url", ""),
                            "thumbnail": m.get("media_url_https", "")
                        })
            
            # Log media extraction for debugging
            logger.debug(f"Twitter media extracted: {len(media)} items")
            for idx, m in enumerate(media):
                logger.debug(f"  Media {idx+1}: type={m.get('type')}, url={'present' if m.get('url') else 'empty'}")
            
            # Extract metrics
            metrics = {
                "likes": legacy.get("favorite_count", 0),
                "retweets": legacy.get("retweet_count", 0),
                "replies": legacy.get("reply_count", 0),
                "quotes": legacy.get("quote_count", 0),
                "views": data.get("views", {}).get("count", "0")
            }
            
            # Try to convert views to int
            try:
                metrics["views"] = int(metrics["views"])
            except (ValueError, TypeError):
                metrics["views"] = 0
            
            # Extract author info
            # Name and screen_name are in user_result.core (not legacy!)
            # Profile image is in user_result.avatar.image_url
            # But followers_count and other stats are in user_result.legacy
            author = {
                "name": user_core.get("name", "Unknown"),
                "username": user_core.get("screen_name", "unknown"),
                "profile_image": user_result.get("avatar", {}).get("image_url", "") or user_legacy.get("profile_image_url_https", ""),
                "verified": user_legacy.get("verified", False) or user_result.get("is_blue_verified", False),
                "followers": user_legacy.get("followers_count", 0)
            }
            
            # Log author data for debugging
            logger.debug(f"Twitter author extracted: name={author['name']}, username={author['username']}, followers={author['followers']}")
            
            # Extract timestamp
            created_at = legacy.get("created_at", "")
            timestamp = self._parse_twitter_timestamp(created_at) if created_at else None
            
            # Extract tweet ID from the API response
            tweet_id = data.get("rest_id") or legacy.get("id_str") or "unknown"
            
            formatted = {
                "platform": "twitter",
                "tweet_id": tweet_id,
                "url": url,
                "content_type": "video" if any(m["type"] == "video" for m in media) else "text",
                "text": text,
                "media": media,
                "author": author,
                "metrics": metrics,
                "timestamp": timestamp,
                "raw_data": data,
                "scraper": "scrapecreators"
            }
            
            logger.debug(f"Successfully formatted Twitter content from ScrapeCreators")
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting Twitter content: {e}")
            # Return minimal format on error
            return {
                "platform": "twitter",
                "url": url,
                "content_type": "text",
                "text": data.get("legacy", {}).get("full_text", "Content unavailable"),
                "scraper": "scrapecreators",
                "error": str(e)
            }
    
    def _format_facebook_content(self, data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Format ScrapeCreators Facebook response to match our standard format.
        
        Args:
            data: Raw ScrapeCreators API response
            url: Original post URL
        
        Returns:
            Formatted content dict
        """
        try:
            logger.debug(f"Formatting Facebook content from ScrapeCreators")
            logger.debug(f"Has image_url: {bool(data.get('image_url'))}")
            logger.debug(f"Has video: {bool(data.get('video', {}).get('hd_url') or data.get('video', {}).get('sd_url'))}")
            logger.debug(f"Author data: {data.get('author', {})}")
            
            # Extract text content
            text = data.get("description", "")
            
            # Extract media
            media = []
            video_data = data.get("video", {})
            image_url = data.get("image_url")
            
            # Check if video has actual content (not just empty object with null values)
            has_video = video_data and (video_data.get("hd_url") or video_data.get("sd_url"))
            
            if has_video:
                media.append({
                    "type": "video",
                    "url": video_data.get("hd_url") or video_data.get("sd_url", ""),
                    "thumbnail": video_data.get("thumbnail", ""),
                    "duration": video_data.get("length_in_second", 0)
                })
            elif image_url:
                media.append({
                    "type": "image",
                    "url": image_url
                })
            
            # Extract metrics
            metrics = {
                "likes": data.get("like_count", 0),
                "comments": data.get("comment_count", 0),
                "shares": data.get("share_count", 0),
                "views": data.get("view_count", 0)
            }
            
            # Extract author info
            author_data = data.get("author", {})
            author_id = author_data.get("id", "")
            author_url = author_data.get("url") or (f"https://www.facebook.com/{author_id}" if author_id else None)
            
            # Try to extract username from URL or use name as fallback
            if author_url:
                # Extract username from URL (last part after /)
                username = author_url.rstrip('/').split('/')[-1]
            else:
                # Use name as username if no URL available
                username = author_data.get("name", "unknown").replace(" ", "").lower()
            
            author = {
                "name": author_data.get("name", "Unknown"),
                "username": username,
                "profile_image": author_data.get("image", ""),
                "verified": bool(author_data.get("is_verified", False))
            }
            
            # Extract music/audio info
            music_data = data.get("music", {})
            audio_info = None
            if music_data:
                audio_info = {
                    "title": music_data.get("track_title", ""),
                    "artist": music_data.get("track_title", "").split("·")[0].strip() if "·" in music_data.get("track_title", "") else ""
                }
            
            formatted = {
                "platform": "facebook",
                "url": url,
                "content_type": "video" if has_video else "image" if image_url else "text",
                "text": text,
                "media": media,
                "author": author,
                "metrics": metrics,
                "audio": audio_info,
                "post_id": data.get("post_id", ""),
                "raw_data": data,
                "scraper": "scrapecreators"
            }
            
            logger.debug(f"Facebook author: name={author['name']}, username={author['username']}, profile_image={'present' if author['profile_image'] else 'EMPTY'}")
            logger.debug(f"Facebook media: {len(media)} items, content_type={formatted['content_type']}")
            logger.debug(f"Successfully formatted Facebook content from ScrapeCreators")
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting Facebook content: {e}")
            return {
                "platform": "facebook",
                "url": url,
                "content_type": "text",
                "text": data.get("description", "Content unavailable"),
                "scraper": "scrapecreators",
                "error": str(e)
            }
    
    def _format_instagram_content(self, data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Format ScrapeCreators Instagram response to match our standard format.
        
        Args:
            data: Raw ScrapeCreators API response
            url: Original post URL
        
        Returns:
            Formatted content dict
        """
        try:
            logger.debug(f"Formatting Instagram content from ScrapeCreators")
            media_data = data.get("data", {}).get("xdt_shortcode_media", {})
            logger.debug(f"Has media_data: {bool(media_data)}")
            
            # Extract text content
            caption_edges = media_data.get("edge_media_to_caption", {}).get("edges", [])
            text = caption_edges[0]["node"]["text"] if caption_edges else ""
            
            # Determine content type
            typename = media_data.get("__typename", "")
            is_video = typename == "XDTGraphVideo" or media_data.get("is_video", False)
            logger.debug(f"Content type: {typename}, is_video: {is_video}")
            
            # Extract media
            media = []
            if is_video:
                video_url = media_data.get("video_url", "")
                thumbnail = media_data.get("display_url", "")
                duration = media_data.get("video_duration", 0)
                
                media.append({
                    "type": "video",
                    "url": video_url,
                    "thumbnail": thumbnail,
                    "duration": duration
                })
            else:
                # Check for carousel (multiple images)
                carousel = media_data.get("edge_sidecar_to_children", {}).get("edges", [])
                if carousel:
                    for item in carousel:
                        node = item.get("node", {})
                        media.append({
                            "type": "image",
                            "url": node.get("display_url", "")
                        })
                else:
                    # Single image
                    display_url = media_data.get("display_url", "")
                    if display_url:
                        media.append({
                            "type": "image",
                            "url": display_url
                        })
                        logger.debug(f"Added single image: {len(display_url)} chars")
            
            # Extract metrics
            metrics = {
                "likes": media_data.get("edge_media_preview_like", {}).get("count", 0),
                "comments": media_data.get("edge_media_to_parent_comment", {}).get("count", 0),
                "views": media_data.get("video_play_count", 0) if is_video else 0
            }
            
            # Extract author info
            owner = media_data.get("owner", {})
            logger.debug(f"Owner data: username={owner.get('username')}, full_name={owner.get('full_name')}, has_profile_pic={bool(owner.get('profile_pic_url'))}")
            
            # For Instagram: Display username as name, and full_name as username (swapped for UI display)
            author = {
                "name": owner.get("username", "Unknown"),  # Show username as the main name
                "username": owner.get("full_name", "unknown"),  # Show full_name as the handle
                "profile_image": owner.get("profile_pic_url", ""),
                "verified": owner.get("is_verified", False),
                "followers": owner.get("edge_followed_by", {}).get("count", 0)
            }
            
            logger.debug(f"Instagram author: name={author['name']}, username={author['username']}, profile_image={'present ('+str(len(author['profile_image']))+' chars)' if author['profile_image'] else 'EMPTY'}")
            logger.debug(f"Instagram media: {len(media)} items, content_type={'video' if is_video else 'image'}")
            
            # Extract timestamp
            timestamp_unix = media_data.get("taken_at_timestamp")
            timestamp = datetime.fromtimestamp(timestamp_unix).isoformat() if timestamp_unix else None
            
            # Extract audio/music info
            clips_music = media_data.get("clips_music_attribution_info", {})
            audio_info = None
            if clips_music:
                audio_info = {
                    "title": clips_music.get("song_name", ""),
                    "artist": clips_music.get("artist_name", "")
                }
            
            formatted = {
                "platform": "instagram",
                "url": url,
                "content_type": "video" if is_video else "image",
                "text": text,
                "media": media,
                "author": author,
                "metrics": metrics,
                "audio": audio_info,
                "timestamp": timestamp,
                "shortcode": media_data.get("shortcode", ""),
                "raw_data": data,
                "scraper": "scrapecreators"
            }
            
            logger.debug(f"Successfully formatted Instagram content from ScrapeCreators")
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting Instagram content: {e}")
            return {
                "platform": "instagram",
                "url": url,
                "content_type": "text",
                "text": "Content unavailable",
                "scraper": "scrapecreators",
                "error": str(e)
            }
    
    def _parse_twitter_timestamp(self, created_at: str) -> Optional[str]:
        """
        Parse Twitter timestamp format to ISO 8601.
        
        Args:
            created_at: Twitter timestamp (e.g., "Thu Feb 23 14:52:10 +0000 2023")
        
        Returns:
            ISO 8601 formatted timestamp or None
        """
        try:
            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            return dt.isoformat()
        except Exception as e:
            logger.warning(f"Failed to parse Twitter timestamp '{created_at}': {e}")
            return None


# Global instance
scrapecreators_service = ScrapeCreatorsService()
