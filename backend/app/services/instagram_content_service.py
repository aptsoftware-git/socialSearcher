"""
Instagram Content Service - Fetch full post details using Instagram Graph API.
NOTE: Requires Instagram Business Account connected to Facebook Page.
Supports third-party scraping via ScrapeCreators API (configurable via INSTAGRAM_SCRAPER env variable).
"""

from typing import Optional, Dict, Any
import re
import httpx
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


class InstagramContentService:
    """Service for fetching full Instagram post content."""
    
    def __init__(self):
        """Initialize Instagram service with Access Token."""
        self.access_token = settings.instagram_access_token
        self.base_url = "https://graph.instagram.com"
        
    def extract_media_id(self, url: str) -> Optional[str]:
        """
        Extract media ID from Instagram URL.
        
        Note: Instagram Graph API uses different IDs than public URLs.
        This extracts the shortcode which can be converted to media ID.
        
        Supports:
        - https://www.instagram.com/p/SHORTCODE/
        - https://www.instagram.com/reel/SHORTCODE/
        """
        patterns = [
            r'instagram\.com\/(?:p|reel)\/([A-Za-z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_post_content(self, url: str) -> Optional[SocialFullContent]:
        """
        Fetch full post details from Instagram Graph API or ScrapeCreators API.
        
        NOTE: Native Instagram Graph API requires:
        1. Instagram Business Account
        2. Connected to Facebook Page
        3. Access token with instagram_basic permission
        
        Args:
            url: Instagram post URL
            
        Returns:
            SocialFullContent with post details or None if error
        """
        # Check if we should use ScrapeCreators API instead
        if settings.instagram_scraper.upper() == "SCRAPECREATORS":
            logger.info("🔄 Using ScrapeCreators API for Instagram content")
            scrapecreators_data = await scrapecreators_service.get_instagram_content(url)
            if scrapecreators_data:
                return self._convert_scrapecreators_to_model(scrapecreators_data)
            else:
                logger.warning("⚠️ ScrapeCreators failed, falling back to native Instagram API")
                # Fall through to native API
        
        # Use native Instagram Graph API
        logger.info("🔄 Using native Instagram Graph API")
        
        if not self.access_token:
            logger.warning(
                "Instagram Access Token not configured. Instagram Graph API requires: "
                "1) Instagram Business/Creator Account, 2) Connected to Facebook Page, "
                "3) Access token with Instagram permissions. "
                "Wait for Facebook App Review approval, then configure Instagram Business Account. "
                "See doc/INSTAGRAM_SETUP.md for details."
            )
            return None
        
        # Extract shortcode
        shortcode = self.extract_media_id(url)
        if not shortcode:
            logger.error(f"Could not extract media shortcode from URL: {url}")
            return None
        
        logger.info(f"Fetching Instagram post: {shortcode}")
        
        try:
            # Note: Instagram Graph API requires media ID, not shortcode
            # For now, we'll return None and log the requirement
            logger.warning(
                f"Instagram API requires Business Account and media ID. "
                f"Shortcode {shortcode} cannot be directly queried without Business Account setup."
            )
            logger.info(
                "To enable Instagram content fetching:\n"
                "1. Convert Instagram account to Business Account\n"
                "2. Connect to Facebook Page\n"
                "3. Use Facebook Graph API to get Instagram Business Account ID\n"
                "4. Query media using business account endpoint"
            )
            
            # Placeholder for when properly configured
            # async with httpx.AsyncClient(timeout=30.0) as client:
            #     response = await client.get(
            #         f"{self.base_url}/{media_id}",
            #         params={
            #             'access_token': self.access_token,
            #             'fields': 'caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,like_count,comments_count'
            #         }
            #     )
            #     ...
            
            return None
                
        except Exception as e:
            logger.error(f"Error fetching Instagram post {shortcode}: {e}", exc_info=True)
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
            logger.info(f"📊 ScrapeCreators Instagram data keys: {list(data.keys())}")
            logger.info(f"🖼️ Instagram media count: {len(data.get('media', []))}")
            
            # Extract author info
            author_data = data.get("author", {})
            logger.info(f"👤 Instagram author_data: name={author_data.get('name')}, username={author_data.get('username')}, profile_image={'present ('+str(len(author_data.get('profile_image', '')))+' chars)' if author_data.get('profile_image') else 'EMPTY'}")
            
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
            for m in data.get("media", []):
                media_type = m.get("type", "image")
                media_url = m.get("url", "")
                logger.info(f"🖼️ Instagram media: type={media_type}, url={'present ('+str(len(media_url))+' chars)' if media_url else 'EMPTY'}")
                
                media_list.append(
                    SocialContentMedia(
                        type=media_type,
                        url=media_url,
                        thumbnail_url=m.get("thumbnail", ""),
                        width=None,
                        height=None,
                        duration_ms=int(m.get("duration", 0) * 1000) if m.get("duration") else None
                    )
                )
            
            # Extract metrics
            metrics = data.get("metrics", {})
            engagement = SocialContentEngagement(
                likes=metrics.get("likes", 0) or 0,
                comments=metrics.get("comments", 0) or 0,
                shares=0,  # Instagram doesn't have shares
                views=metrics.get("views", 0) or 0
            )
            
            # Create SocialFullContent
            content = SocialFullContent(
                platform="instagram",
                platform_id=data.get("shortcode", "unknown"),
                url=data.get("url", ""),
                content_type=data.get("content_type", "image"),
                text=data.get("text", ""),
                media=media_list,
                author=author,
                engagement=engagement,
                posted_at=data.get("timestamp") or datetime.utcnow(),
                platform_data={
                    'scraper': 'scrapecreators',
                    'shortcode': data.get("shortcode", ""),
                    'audio': data.get("audio"),
                    'raw_data': data.get("raw_data", {})
                }
            )
            
            logger.info("✅ Converted ScrapeCreators Instagram data to SocialFullContent model")
            return content
            
        except Exception as e:
            logger.error(f"❌ Error converting ScrapeCreators Instagram data to model: {e}")
            return None
