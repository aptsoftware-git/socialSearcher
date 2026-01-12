"""
Instagram Content Service - Fetch full post details using Instagram Graph API.
NOTE: Requires Instagram Business Account connected to Facebook Page.
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
        Fetch full post details from Instagram Graph API.
        
        NOTE: This requires:
        1. Instagram Business Account
        2. Connected to Facebook Page
        3. Access token with instagram_basic permission
        
        Args:
            url: Instagram post URL
            
        Returns:
            SocialFullContent with post details or None if error
        """
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
