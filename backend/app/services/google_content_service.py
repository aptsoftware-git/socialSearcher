"""
Google content service for fetching full content from Google search results.
"""

import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.models import SocialFullContent
from app.services.scraper_manager import ScraperManager
from app.services.content_extractor import ContentExtractor


class GoogleContentService:
    """Service for fetching content from Google search result URLs."""
    
    def __init__(self):
        """Initialize the Google content service."""
        self.scraper = ScraperManager(timeout=30.0)
        self.content_extractor = ContentExtractor()
    
    async def get_content(self, url: str) -> Optional[SocialFullContent]:
        """
        Fetch full content from a Google search result URL.
        
        Args:
            url: The URL to fetch content from (any website from Google results)
        
        Returns:
            SocialFullContent object with extracted data, or None if fetch fails
        """
        try:
            logger.info(f"Fetching Google search result content from: {url}")
            
            # Custom headers to appear more like a real browser and avoid 403 errors
            custom_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # Fetch HTML content using scraper with custom headers and less strict robots.txt
            html = await self.scraper.fetch_url(
                url,
                headers=custom_headers,
                rate_limit=1.0,  # 1 second between requests
                respect_robots=False  # Don't respect robots.txt to avoid blocks
            )
            
            if not html:
                logger.warning(f"Failed to fetch HTML from: {url}")
                # Return a partial result with error message instead of None
                return self._create_fallback_content(url, "Unable to fetch content. The website may be blocking automated requests (403 Forbidden).")
            
            # Extract content using generic extractor
            extracted = self.content_extractor.extract_generic(html)
            
            # Clean the extracted data
            title = self.content_extractor.clean_text(extracted.get('title', ''))
            content = self.content_extractor.clean_text(extracted.get('content', ''))
            author_name = self.content_extractor.clean_text(extracted.get('author', ''))
            publish_date_str = extracted.get('published_date', '')
            
            # Validate content
            if not self.content_extractor.is_valid_content(content):
                logger.warning(
                    f"Invalid or insufficient content from {url} "
                    f"(title_len={len(title)}, content_len={len(content)})"
                )
                # Return partial content with error message
                if not content:
                    return self._create_fallback_content(
                        url, 
                        "Content could not be extracted from this page. The page may have limited text or complex JavaScript rendering.",
                        title=title
                    )
            
            # Parse publish date if available
            published_at = None
            if publish_date_str:
                try:
                    published_at = datetime.fromisoformat(publish_date_str)
                except (ValueError, TypeError):
                    logger.debug(f"Could not parse publish date: {publish_date_str}")
            
            # Use current time if no publish date found
            if not published_at:
                published_at = datetime.utcnow()
            
            # Build author object
            from app.models import SocialContentAuthor, SocialContentEngagement
            
            if author_name:
                author = SocialContentAuthor(
                    name=author_name,
                    username='',
                    profile_url=None,
                    verified=False
                )
            else:
                author = SocialContentAuthor(
                    name='Unknown',
                    username='',
                    profile_url=None,
                    verified=False
                )
            
            # Create engagement object
            engagement = SocialContentEngagement(
                likes=0,
                comments=0,
                shares=0,
                views=0
            )
            
            # Construct SocialFullContent object
            full_content = SocialFullContent(
                platform='google',
                content_type='web_page',
                url=url,
                platform_id=url,  # Use URL as platform ID for web pages
                title=title or "Untitled",
                text=content,
                description=content[:500] if len(content) > 500 else content,  # First 500 chars as description
                author=author,
                posted_at=published_at,
                media=[],
                engagement=engagement,
                platform_data={}
            )
            
            logger.info(
                f"Successfully extracted Google content: "
                f"title={title[:50]}..., content_length={len(content)}"
            )
            
            return full_content
            
        except httpx.HTTPStatusError as e:
            # Specific handling for HTTP errors like 403, 404, 503
            status_code = e.response.status_code
            error_messages = {
                403: "Access Forbidden (403). The website is blocking automated requests. Try accessing the URL directly in your browser.",
                404: "Page Not Found (404). The content may have been removed or the URL is incorrect.",
                503: "Service Unavailable (503). The website may be temporarily down or overloaded.",
                500: "Internal Server Error (500). The website encountered an error.",
                401: "Unauthorized (401). Authentication required to access this content.",
                429: "Too Many Requests (429). Rate limit exceeded. Please try again later."
            }
            error_msg = error_messages.get(status_code, f"HTTP Error {status_code}. Unable to fetch content from this website.")
            logger.warning(f"HTTP {status_code} error fetching Google content from {url}: {e}")
            return self._create_fallback_content(url, error_msg)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching Google content from {url}: {e}")
            return self._create_fallback_content(url, f"Network error occurred while fetching content: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error fetching Google content from {url}: {e}", exc_info=True)
            return self._create_fallback_content(url, f"Unexpected error occurred: {str(e)}")
    
    def _create_fallback_content(self, url: str, error_message: str, title: str = None) -> SocialFullContent:
        """
        Create a fallback SocialFullContent object when fetching fails.
        
        Args:
            url: The URL that failed to fetch
            error_message: User-friendly error message
            title: Optional title extracted before failure
        
        Returns:
            SocialFullContent with error message
        """
        from app.models import SocialContentAuthor, SocialContentEngagement
        
        # Create fallback author
        fallback_author = SocialContentAuthor(
            name="Unknown",
            username="",
            profile_url=None,
            verified=False
        )
        
        # Create fallback engagement
        fallback_engagement = SocialContentEngagement(
            likes=0,
            comments=0,
            shares=0,
            views=0
        )
        
        return SocialFullContent(
            platform='google',
            content_type='web_page',
            url=url,
            platform_id=url,  # Use URL as ID for web pages
            title=title or "Content Unavailable",
            text=f"⚠️ {error_message}\n\nURL: {url}\n\nYou can try:\n1. Opening the URL directly in your browser\n2. Checking if the website is accessible\n3. Trying again later if the site is temporarily down",
            description=error_message,
            author=fallback_author,
            posted_at=datetime.utcnow(),
            media=[],
            engagement=fallback_engagement,
            platform_data={'error': error_message, 'fetch_failed': True}
        )
