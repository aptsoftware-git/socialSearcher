"""
Google Custom Search Engine Service for Social Media Search.
"""

from typing import List, Dict, Any, Optional
import json
import httpx
from loguru import logger
from app.settings import settings


class SocialSearchService:
    """Service for searching social media platforms using Google Custom Search Engine."""
    
    def __init__(self):
        """Initialize the social search service."""
        self.api_key = settings.google_cse_api_key if hasattr(settings, 'google_cse_api_key') else None
        self.search_engine_id = settings.google_cse_id if hasattr(settings, 'google_cse_id') else None
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    async def search(
        self,
        query: str,
        sites: Optional[List[str]] = None,
        results_per_site: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search using Google Custom Search Engine.
        
        Args:
            query: Search query string
            sites: List of sites to search (e.g., ['facebook.com', 'x.com'])
            results_per_site: Number of results to fetch per site (default: 10)
            
        Returns:
            List of search results with title, link, snippet, etc.
        """
        if not self.api_key or not self.search_engine_id:
            logger.error("Google CSE API key or Search Engine ID not configured")
            return []
        
        # Default sites if not provided - includes all configured platforms
        if not sites:
            sites = ['facebook.com', 'x.com', 'youtube.com', 'instagram.com']
        
        all_results = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for site in sites:
                logger.info(f"Searching {site} for: {query}")
                
                # Construct site-specific query
                site_query = f"site:{site} {query}"
                
                try:
                    results = await self._fetch_results(
                        client=client,
                        query=site_query,
                        max_results=results_per_site
                    )
                    
                    # Add site information to each result
                    for result in results:
                        result['source_site'] = site
                    
                    all_results.extend(results)
                    logger.info(f"Found {len(results)} results from {site}")
                    
                except Exception as e:
                    logger.error(f"Error searching {site}: {e}")
                    continue
        
        logger.info(f"Total social search results: {len(all_results)}")
        return all_results
    
    async def _fetch_results(
        self,
        client: httpx.AsyncClient,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch results from Google Custom Search API.
        
        Args:
            client: httpx AsyncClient
            query: Search query
            max_results: Maximum number of results to fetch
            
        Returns:
            List of search results
        """
        results = []
        start_index = 1
        
        # Google CSE returns max 10 results per request
        # We need to paginate to get more
        while len(results) < max_results:
            try:
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': query,
                    'start': start_index,
                    'num': min(10, max_results - len(results))  # Max 10 per request
                }
                
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract search results
                items = data.get('items', [])
                if not items:
                    break  # No more results
                
                for item in items:
                    pagemap = item.get('pagemap', {})
                    
                    # Debug: Log full item for Facebook results
                    if 'facebook' in item.get('link', '').lower():
                        logger.info(f"=== FACEBOOK ITEM FROM GOOGLE CSE ===")
                        logger.info(f"Title: {item.get('title', '')}")
                        logger.info(f"Link: {item.get('link', '')}")
                        logger.info(f"Pagemap keys: {list(pagemap.keys())}")
                        logger.info(f"Full pagemap: {json.dumps(pagemap, indent=2)}")
                        
                        # Check for image fields
                        if 'cse_image' in pagemap:
                            logger.info(f"✓ Has cse_image: {pagemap['cse_image']}")
                        if 'cse_thumbnail' in pagemap:
                            logger.info(f"✓ Has cse_thumbnail: {pagemap['cse_thumbnail']}")
                        if 'metatags' in pagemap:
                            logger.info(f"✓ Has metatags")
                            if pagemap['metatags']:
                                meta = pagemap['metatags'][0] if isinstance(pagemap['metatags'], list) else pagemap['metatags']
                                if 'og:image' in meta:
                                    logger.info(f"  ✓ og:image: {meta['og:image']}")
                    
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'display_link': item.get('displayLink', ''),
                        'formatted_url': item.get('formattedUrl', ''),
                        'pagemap': pagemap,
                    }
                    results.append(result)
                
                # Check if there are more results
                if 'nextPage' not in data.get('queries', {}):
                    break
                
                start_index += 10
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during Google CSE search: {e.response.status_code} - {e.response.text}")
                break
            except Exception as e:
                logger.error(f"Error fetching results: {e}")
                break
        
        return results


# Global instance
social_search_service = SocialSearchService()
