"""
Facebook Content Service - Fetch full post details using Facebook Graph API.
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


class FacebookContentService:
    """Service for fetching full Facebook post content."""
    
    def __init__(self):
        """Initialize Facebook service with Access Token."""
        self.access_token = settings.facebook_access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def extract_post_id(self, url: str) -> Optional[str]:
        """
        Extract post ID from various Facebook URL formats.
        
        For Graph API v2.4+, we need the full object ID (page_id_post_id format).
        
        Supports:
        - https://www.facebook.com/USERNAME/posts/POST_ID
        - https://www.facebook.com/USERNAME/posts/SLUG/POST_ID (with descriptive slug)
        - https://www.facebook.com/permalink.php?story_fbid=POST_ID&id=PAGE_ID
        - https://www.facebook.com/photo.php?fbid=PHOTO_ID
        - https://www.facebook.com/groups/GROUP_ID/posts/POST_ID
        - https://www.facebook.com/PAGE_ID/posts/POST_ID (numeric page ID)
        """
        # Pattern 1: Numeric page ID with post ID (with optional slug)
        # Matches: facebook.com/12345/posts/67890 or facebook.com/12345/posts/slug/67890
        numeric_pattern = r'facebook\.com\/(\d+)\/posts\/(?:[\w\-]+\/)?(\d+)'
        match = re.search(numeric_pattern, url)
        if match:
            page_id = match.group(1)
            post_id = match.group(2)
            logger.info(f"Extracted numeric page post: {page_id}_{post_id}")
            return f"{page_id}_{post_id}"
        
        # Pattern 2: permalink.php format with story_fbid and id parameters
        if 'permalink.php' in url or 'story_fbid' in url:
            story_fbid_match = re.search(r'story_fbid=(\d+)', url)
            page_id_match = re.search(r'[?&]id=(\d+)', url)
            if story_fbid_match and page_id_match:
                story_fbid = story_fbid_match.group(1)
                page_id = page_id_match.group(1)
                logger.info(f"Extracted permalink post: {page_id}_{story_fbid}")
                return f"{page_id}_{story_fbid}"
        
        # Pattern 3: Username format with OPTIONAL descriptive slug
        # Matches: facebook.com/USERNAME/posts/12345 OR facebook.com/USERNAME/posts/slug-text/12345
        # The slug can contain hyphens, underscores, and multiple words
        username_pattern = r'facebook\.com\/([\w\.]+)\/posts\/(?:[\w\-]+\/)?([\d]+)'
        match = re.search(username_pattern, url)
        if match:
            username = match.group(1)
            post_id = match.group(2)
            logger.info(f"Extracted username post: {username}_{post_id}")
            # Return format that we'll need to resolve
            return f"{username}_{post_id}"
        
        # Pattern 4: Photo posts
        if 'photo.php' in url:
            fbid_match = re.search(r'fbid=(\d+)', url)
            if fbid_match:
                photo_id = fbid_match.group(1)
                logger.info(f"Extracted photo ID: {photo_id}")
                return photo_id
        
        # Pattern 5: Try to extract from URL path by finding any numeric ID after /posts/
        # This is a fallback that looks for the LAST numeric segment in the path
        parts = url.rstrip('/').split('/')
        
        # Look for 'posts' in the path
        try:
            posts_index = parts.index('posts')
            # Get all parts after 'posts'
            parts_after_posts = parts[posts_index + 1:]
            
            # Find the first numeric part (could be after slug)
            for part in parts_after_posts:
                if part.isdigit() and len(part) >= 10:  # Post IDs are typically long
                    # Try to find username/page_id before 'posts'
                    if posts_index > 0:
                        username_or_page = parts[posts_index - 1]
                        logger.info(f"Extracted from path: {username_or_page}_{part}")
                        return f"{username_or_page}_{part}"
                    else:
                        logger.info(f"Extracted from path: {part}")
                        return part
        except (ValueError, IndexError):
            pass
        
        # Pattern 6: Last resort - find any long numeric sequence in URL
        numeric_sequences = re.findall(r'\d{10,}', url)
        if numeric_sequences:
            post_id = numeric_sequences[-1]  # Take the last long number
            logger.warning(f"Using last resort extraction: {post_id}")
            return post_id
        
        logger.error(f"Could not extract post ID from URL: {url}")
        return None
    
    async def get_post_content(self, url: str) -> Optional[SocialFullContent]:
        """
        Fetch full post details from Facebook Graph API.
        
        Args:
            url: Facebook post URL
            
        Returns:
            SocialFullContent with post details or None if error
        """
        if not self.access_token:
            logger.error("Facebook Access Token not configured")
            return None
        
        # Extract post ID
        post_id = self.extract_post_id(url)
        if not post_id:
            logger.error(f"Could not extract post ID from URL: {url}")
            return None
        
        logger.info(f"Fetching Facebook post: {post_id}")
        
        # Store original post_id for fallback attempts
        original_post_id = post_id
        username_format_id = None
        numeric_only_id = None
        page_id_format_id = None
        
        # If post_id contains username (not numeric), prepare multiple formats to try
        if '_' in post_id and not post_id.split('_')[0].isdigit():
            username, numeric_post_id = post_id.split('_', 1)
            username_format_id = post_id  # Try username_postid format first
            numeric_only_id = numeric_post_id  # Fallback to just numeric
            
            logger.info(f"Attempting to resolve username '{username}' to page ID")
            
            # MUST resolve username to page ID for Graph API v2.4+
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    page_response = await client.get(
                        f"{self.base_url}/{username}",
                        params={
                            'access_token': self.access_token,
                            'fields': 'id,name'
                        }
                    )
                    if page_response.status_code == 200:
                        page_data = page_response.json()
                        page_id = page_data.get('id')
                        page_name = page_data.get('name', username)
                        if page_id:
                            page_id_format_id = f"{page_id}_{numeric_post_id}"
                            logger.info(f"Resolved username '{username}' ('{page_name}') to page ID: {page_id}")
                            logger.info(f"Will use format: {page_id_format_id}")
                        else:
                            logger.warning(f"Username '{username}' returned empty page ID")
                    else:
                        logger.warning(f"Failed to resolve username '{username}': status {page_response.status_code}")
                        logger.debug(f"Response: {page_response.text}")
            except Exception as e:
                logger.error(f"Error resolving username '{username}' to page ID: {e}")
        
        # Try multiple post ID formats in order of preference
        # IMPORTANT: For Graph API v2.4+, pageid_postid format is REQUIRED
        formats_to_try = []
        if page_id_format_id:
            formats_to_try.append(('pageid_postid', page_id_format_id))
        if username_format_id:
            formats_to_try.append(('username_postid', username_format_id))
        if numeric_only_id:
            formats_to_try.append(('numeric_only', numeric_only_id))
        if not formats_to_try:
            formats_to_try.append(('original', original_post_id))
        
        # Log the issue if username resolution failed
        if '_' in original_post_id and not post_id.split('_')[0].isdigit() and not page_id_format_id:
            logger.warning(f"Username resolution failed. Facebook Graph API requires numeric page IDs.")
            logger.warning(f"Your token may need 'pages_read_engagement' or 'Page Public Content Access' permissions.")
            logger.warning(f"Trying fallback formats, but they may not work for public pages like news organizations.")
        
        post_data = None
        successful_format = None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try each format until one works
                for format_name, format_id in formats_to_try:
                    try:
                        logger.info(f"Trying {format_name} format: {format_id}")
                        response = await client.get(
                            f"{self.base_url}/{format_id}",
                            params={
                                'access_token': self.access_token,
                                'fields': 'message,created_time,from,full_picture,attachments,shares,reactions.summary(true),comments.summary(true)'
                            }
                        )
                        
                        if response.status_code == 200:
                            post_data = response.json()
                            successful_format = format_name
                            logger.info(f"Successfully fetched with {format_name} format")
                            break
                        else:
                            error_detail = response.text
                            logger.warning(f"{format_name} format failed with status {response.status_code}: {error_detail}")
                    except httpx.HTTPStatusError as e:
                        logger.warning(f"{format_name} format failed: {e}")
                        continue
                
                if not post_data:
                    logger.error("All post ID formats failed")
                    return None
                
                # Parse created date
                created_time_str = post_data.get('created_time', '')
                try:
                    posted_at = datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
                except:
                    posted_at = datetime.utcnow()
                
                # Get author info
                from_data = post_data.get('from', {})
                author = SocialContentAuthor(
                    name=from_data.get('name', 'Unknown'),
                    username=from_data.get('id', ''),
                    profile_url=f"https://www.facebook.com/{from_data.get('id', '')}",
                    verified=False  # Facebook Graph API doesn't easily provide verified status
                )
                
                # Build media list
                media = []
                full_picture = post_data.get('full_picture')
                if full_picture:
                    media.append(SocialContentMedia(
                        type='image',
                        url=full_picture
                    ))
                
                # Check attachments for additional media
                attachments = post_data.get('attachments', {}).get('data', [])
                for attachment in attachments:
                    media_data = attachment.get('media', {})
                    media_type = attachment.get('type', 'photo')
                    
                    if media_type == 'photo':
                        media.append(SocialContentMedia(
                            type='image',
                            url=media_data.get('image', {}).get('src', '')
                        ))
                    elif media_type == 'video':
                        media.append(SocialContentMedia(
                            type='video',
                            url=media_data.get('source', ''),
                            thumbnail_url=media_data.get('image', {}).get('src', '')
                        ))
                
                # Build engagement metrics
                reactions_summary = post_data.get('reactions', {}).get('summary', {})
                comments_summary = post_data.get('comments', {}).get('summary', {})
                shares_data = post_data.get('shares', {})
                
                engagement = SocialContentEngagement(
                    likes=reactions_summary.get('total_count', 0),
                    comments=comments_summary.get('total_count', 0),
                    shares=shares_data.get('count', 0)
                )
                
                # Build full content
                content = SocialFullContent(
                    platform='facebook',
                    content_type='post',
                    url=url,
                    platform_id=successful_format or original_post_id,
                    text=post_data.get('message', ''),
                    author=author,
                    posted_at=posted_at,
                    media=media,
                    engagement=engagement,
                    platform_data={
                        'post_id': successful_format or original_post_id,
                        'format_used': successful_format,
                        'from_id': from_data.get('id'),
                        'story': post_data.get('story', ''),
                        'type': post_data.get('type', 'status'),
                    }
                )
                
                logger.info(f"Successfully fetched Facebook post with {successful_format} format")
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Facebook post {original_post_id}: {e.response.status_code}")
            logger.error(f"Response: {e.response.text[:500]}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Facebook post {original_post_id}: {e}", exc_info=True)
            return None
