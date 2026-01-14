"""
Twitter/X Content Service - Fetch full tweet details using Twitter API v2.
Uses OAuth 2.0 Bearer Token authentication (simpler, same rate limits as OAuth 1.0a on FREE tier).
Supports third-party scraping via ScrapeCreators API (configurable via TWITTER_SCRAPER env variable).
"""

from typing import Optional, Dict, Any, List
import re
import httpx
import asyncio
from datetime import datetime
from loguru import logger

from app.settings import settings
from app.models import (
    SocialFullContent,
    SocialContentAuthor,
    SocialContentMedia,
    SocialContentEngagement
)
from app.services.scrapecreators_service import scrapecreators_service


class TwitterContentService:
    """Service for fetching full Twitter/X tweet content using OAuth 2.0 Bearer Token."""
    
    def __init__(self):
        """Initialize Twitter service with OAuth 2.0 Bearer Token."""
        self.bearer_token = settings.twitter_bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.max_retries = 3
        self.base_retry_delay = 15  # seconds
        
        logger.info("🔐 Twitter: Using OAuth 2.0 (Bearer Token)")
        
    def _log_rate_limit_info(self, headers: Dict[str, str]):
        """Log rate limit information from response headers."""
        try:
            self.rate_limit_remaining = headers.get('x-rate-limit-remaining')
            self.rate_limit_reset = headers.get('x-rate-limit-reset')
            
            if self.rate_limit_remaining:
                remaining = int(self.rate_limit_remaining)
                # Note: FREE tier has 1 request/15min, Basic has 15/15min, Pro has 450-900/15min
                logger.info(f"🐦 Twitter API remaining: {remaining} requests")
                
                if remaining <= 0:
                    logger.error(f"🚨 Twitter rate limit exhausted: {remaining} requests remaining!")
                elif remaining <= 5:
                    logger.warning(f"⚠️ Twitter rate limit low: {remaining} requests remaining")
                    
            if self.rate_limit_reset:
                reset_time = datetime.fromtimestamp(int(self.rate_limit_reset))
                logger.info(f"🔄 Twitter rate limit resets at: {reset_time.strftime('%H:%M:%S')}")
        except Exception as e:
            logger.debug(f"Could not parse rate limit headers: {e}")
        
    def extract_tweet_id(self, url: str) -> Optional[str]:
        """
        Extract tweet ID from various Twitter URL formats.
        
        Supports:
        - https://twitter.com/username/status/TWEET_ID
        - https://x.com/username/status/TWEET_ID
        - https://mobile.twitter.com/username/status/TWEET_ID
        """
        patterns = [
            r'(?:twitter\.com|x\.com)\/(?:\w+)\/status\/(\d+)',
            r'status\/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_tweet_content(self, url: str) -> Optional[SocialFullContent]:
        """
        Fetch full tweet details from Twitter API v2 with retry logic.
        Uses OAuth 2.0 Bearer Token authentication or ScrapeCreators API based on TWITTER_SCRAPER setting.
        
        Args:
            url: Twitter/X tweet URL
            
        Returns:
            SocialFullContent with tweet details or None if error
        """
        # Check if we should use ScrapeCreators API instead
        if settings.twitter_scraper.upper() == "SCRAPECREATORS":
            logger.info("🔄 Using ScrapeCreators API for Twitter content")
            scrapecreators_data = await scrapecreators_service.get_twitter_content(url)
            if scrapecreators_data:
                # Log raw_data to see what ScrapeCreators actually returned
                if "raw_data" in scrapecreators_data:
                    raw_data = scrapecreators_data["raw_data"]
                    logger.info(f"🔍 raw_data top-level keys: {list(raw_data.keys())[:20]}")
                    if "user" in raw_data:
                        logger.info(f"🔍 raw_data['user'] keys: {list(raw_data['user'].keys())[:15] if isinstance(raw_data['user'], dict) else 'not dict'}")
                    if "author" in raw_data:
                        logger.info(f"🔍 raw_data['author']: {raw_data['author']}")
                return self._convert_scrapecreators_to_model(scrapecreators_data)
            else:
                logger.warning("⚠️ ScrapeCreators failed, falling back to native Twitter API")
                # Fall through to native API
        
        # Use native Twitter API (OAuth 2.0)
        logger.info("🔄 Using native Twitter API (OAuth 2.0)")
        
        # Check authentication
        if not self.bearer_token:
            logger.error("Twitter API Bearer Token not configured")
            return None
        
        # Extract tweet ID
        tweet_id = self.extract_tweet_id(url)
        if not tweet_id:
            logger.error(f"Could not extract tweet ID from URL: {url}")
            return None
        
        logger.info(f"Fetching Twitter tweet: {tweet_id}")
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Build API request
                    endpoint = f"{self.base_url}/tweets/{tweet_id}"
                    params = {
                        'tweet.fields': 'created_at,public_metrics,author_id,text,attachments,entities',
                        'expansions': 'author_id,attachments.media_keys',
                        'user.fields': 'name,username,profile_image_url,verified',
                        'media.fields': 'url,preview_image_url,type,width,height,duration_ms'
                    }
                    
                    # OAuth 2.0 Bearer Token authentication
                    headers = {
                        'Authorization': f'Bearer {self.bearer_token}'
                    }
                    
                    # Make API request
                    response = await client.get(endpoint, params=params, headers=headers)
                    
                    # Log rate limit info
                    self._log_rate_limit_info(response.headers)
                    
                    # Check for rate limit before raising error
                    if response.status_code == 429:
                        # Calculate wait time until rate limit resets
                        if self.rate_limit_reset:
                            current_time = datetime.now().timestamp()
                            reset_timestamp = int(self.rate_limit_reset)
                            wait_until_reset = max(0, reset_timestamp - current_time)
                            reset_time = datetime.fromtimestamp(reset_timestamp)
                            
                            # If reset is within 1 minute, wait for it
                            if 0 < wait_until_reset <= 60:
                                logger.info(
                                    f"⏳ Rate limit resets in {int(wait_until_reset)}s at {reset_time.strftime('%H:%M:%S')}. "
                                    f"Waiting for reset..."
                                )
                                await asyncio.sleep(wait_until_reset + 2)  # +2s buffer
                                continue  # Retry after reset
                            
                            # If reset is far away (>1 min), log warning but still try retry with backoff
                            logger.warning(
                                f"⚠️ Twitter rate limit hit (429). "
                                f"Rate limit resets at: {reset_time.strftime('%H:%M:%S')} "
                                f"(in {int(wait_until_reset / 60)} minutes {int(wait_until_reset % 60)} seconds)"
                            )
                        
                        # Use exponential backoff for retries
                        if attempt < self.max_retries - 1:
                            # Get retry-after from header or use exponential backoff
                            retry_after = response.headers.get('retry-after')
                            if retry_after:
                                retry_delay = int(retry_after)
                            else:
                                # Exponential backoff: 15s, 30s, 60s
                                retry_delay = self.base_retry_delay * (2 ** attempt)
                            
                            logger.warning(
                                f"⏳ Retrying in {retry_delay}s... (attempt {attempt + 1}/{self.max_retries})"
                            )
                            await asyncio.sleep(retry_delay)
                            continue  # Retry
                        else:
                            # Max retries reached
                            if self.rate_limit_reset:
                                reset_time = datetime.fromtimestamp(int(self.rate_limit_reset))
                                logger.error(
                                    f"🚨 Twitter rate limit exceeded. Max retries ({self.max_retries}) reached. "
                                    f"Rate limit resets at: {reset_time.strftime('%H:%M:%S')}. "
                                    f"Content is cached and will be available for 24 hours."
                                )
                            else:
                                logger.error(f"🚨 Twitter rate limit exceeded. Max retries ({self.max_retries}) reached.")
                            return None
                    
                    response.raise_for_status()
                    data = response.json()
                
                    if 'data' not in data:
                        logger.warning(f"No tweet found for ID: {tweet_id}")
                        return None
                    
                    tweet_data = data['data']
                    includes = data.get('includes', {})
                    
                    # Parse created date
                    created_at_str = tweet_data.get('created_at', '')
                    try:
                        posted_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except:
                        posted_at = datetime.utcnow()
                    
                    # Get author info from includes
                    author_data = {}
                    if 'users' in includes and includes['users']:
                        author_data = includes['users'][0]
                    
                    author = SocialContentAuthor(
                        name=author_data.get('name', 'Unknown'),
                        username=author_data.get('username', ''),
                        profile_url=f"https://twitter.com/{author_data.get('username', '')}",
                        profile_picture=author_data.get('profile_image_url'),
                        verified=author_data.get('verified', False)
                    )
                    
                    # Build media list
                    media = []
                    if 'media' in includes:
                        for media_item in includes['media']:
                            media_type = media_item.get('type', 'photo')
                            
                            if media_type == 'photo':
                                media.append(SocialContentMedia(
                                    type='image',
                                    url=media_item.get('url', ''),
                                    width=media_item.get('width'),
                                    height=media_item.get('height')
                                ))
                            elif media_type == 'video' or media_type == 'animated_gif':
                                media.append(SocialContentMedia(
                                    type='video' if media_type == 'video' else 'gif',
                                    url=media_item.get('url', ''),
                                    thumbnail_url=media_item.get('preview_image_url'),
                                    width=media_item.get('width'),
                                    height=media_item.get('height'),
                                    duration=media_item.get('duration_ms', 0) // 1000 if media_item.get('duration_ms') else None
                                ))
                    
                    # Build engagement metrics
                    public_metrics = tweet_data.get('public_metrics', {})
                    engagement = SocialContentEngagement(
                        likes=public_metrics.get('like_count', 0),
                        comments=public_metrics.get('reply_count', 0),
                        shares=0,  # Not directly available
                        retweets=public_metrics.get('retweet_count', 0),
                        replies=public_metrics.get('reply_count', 0),
                        views=public_metrics.get('impression_count', 0)  # May not be available for all tweets
                    )
                    
                    # Extract hashtags and mentions
                    entities = tweet_data.get('entities', {})
                    hashtags = [tag['tag'] for tag in entities.get('hashtags', [])]
                    mentions = [mention['username'] for mention in entities.get('mentions', [])]
                    urls = [url['expanded_url'] for url in entities.get('urls', [])]
                    
                    # Build full content
                    content = SocialFullContent(
                        platform='twitter',
                        content_type='tweet',
                        url=url,
                        platform_id=tweet_id,
                        text=tweet_data.get('text', ''),
                        author=author,
                        posted_at=posted_at,
                        media=media,
                        engagement=engagement,
                        platform_data={
                            'tweet_id': tweet_id,
                            'author_id': tweet_data.get('author_id'),
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'urls': urls,
                            'quote_count': public_metrics.get('quote_count', 0),
                            'lang': tweet_data.get('lang', 'en'),
                        }
                    )
                    
                    logger.info(f"Successfully fetched Twitter tweet: {tweet_id}")
                    return content
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching Twitter tweet {tweet_id}: {e.response.status_code}")
                if e.response.status_code == 401:
                    logger.error("Twitter Bearer Token is invalid or expired")
                    return None
                elif e.response.status_code == 429:
                    # Already handled above, but just in case
                    if attempt < self.max_retries - 1:
                        retry_delay = self.base_retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"⏳ Rate limit 429. Retrying in {retry_delay}s... (attempt {attempt + 1}/{self.max_retries})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error("Twitter API rate limit exceeded - max retries reached")
                        return None
                return None
                
            except Exception as e:
                logger.error(f"Error fetching Twitter tweet {tweet_id}: {e}", exc_info=True)
                return None
        
        # If we exit the loop without returning
        logger.error(f"Failed to fetch tweet {tweet_id} after {self.max_retries} attempts")
        return None
    
    def _convert_scrapecreators_to_model(self, data: Dict[str, Any]) -> Optional[SocialFullContent]:
        """
        Convert ScrapeCreators formatted data to SocialFullContent model.
        
        Args:
            data: Formatted data from ScrapeCreators service
        
        Returns:
            SocialFullContent model instance
        """
        try:
            # Debug log to see data structure
            logger.info(f"📊 ScrapeCreators Twitter data keys: {list(data.keys())}")
            
            # Extract author info
            author_data = data.get("author", {})
            logger.info(f"👤 Author data: {author_data}")
            
            author = SocialContentAuthor(
                name=author_data.get("name", "Unknown"),
                username=author_data.get("username", "unknown"),
                profile_picture=author_data.get("profile_image", ""),
                verified=author_data.get("verified", False),
                additional_info={
                    'followers': author_data.get("followers", 0)
                }
            )
            
            # Extract media
            media_list = []
            logger.info(f"🖼️ Processing {len(data.get('media', []))} media items from ScrapeCreators")
            for m in data.get("media", []):
                media_type = m.get("type", "image")
                media_url = m.get("url", "")
                logger.info(f"  Media: type={media_type}, url={'present' if media_url else 'EMPTY'}")
                media_list.append(
                    SocialContentMedia(
                        type=media_type,
                        url=media_url,
                        thumbnail_url=m.get("thumbnail", ""),
                        width=None,
                        height=None,
                        duration_ms=None
                    )
                )
            
            # Extract metrics
            metrics = data.get("metrics", {})
            engagement = SocialContentEngagement(
                likes=metrics.get("likes", 0),
                comments=metrics.get("replies", 0),
                shares=metrics.get("retweets", 0),
                views=metrics.get("views", 0),
                additional_metrics={
                    'quotes': metrics.get("quotes", 0)
                }
            )
            
            # Create SocialFullContent
            content = SocialFullContent(
                platform="twitter",
                platform_id=data.get("tweet_id", "unknown"),
                url=data.get("url", ""),
                content_type=data.get("content_type", "text"),
                text=data.get("text", ""),
                media=media_list,
                author=author,
                engagement=engagement,
                posted_at=data.get("timestamp") or datetime.utcnow(),
                platform_data={
                    'scraper': 'scrapecreators',
                    'raw_data': data.get("raw_data", {})
                }
            )
            
            logger.info("✅ Converted ScrapeCreators data to SocialFullContent model")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error converting ScrapeCreators data to model: {e}")
            return None
