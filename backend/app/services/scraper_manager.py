"""
Scraper manager for async web scraping with retry logic and rate limiting.
"""

import httpx
import asyncio
import random
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime
from loguru import logger

from app.models import SourceConfig, ArticleContent
from app.utils.rate_limiter import rate_limiter
from app.utils.robots_checker import robots_checker
from app.services.content_extractor import ContentExtractor
from app.settings import settings


class ScraperManager:
    """
    Manages web scraping operations with async support, retries, and rate limiting.
    """
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        follow_redirects: bool = True
    ):
        """
        Initialize the scraper manager.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            follow_redirects: Whether to follow HTTP redirects
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.follow_redirects = follow_redirects
        self.content_extractor = ContentExtractor()
        
        # Multiple User-Agents for rotation (avoid detection)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        ]
        self._user_agent_index = 0
        
        # Enhanced headers to mimic real browser more closely
        self.default_headers = {
            'User-Agent': self.user_agents[0],  # Will rotate on each request
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _get_rotated_user_agent(self) -> str:
        """Get next User-Agent in rotation to avoid detection."""
        user_agent = self.user_agents[self._user_agent_index]
        self._user_agent_index = (self._user_agent_index + 1) % len(self.user_agents)
        return user_agent
    
    def _merge_headers(self, custom_headers: Optional[Dict[str, str]] = None, skip_referer: bool = False, minimal: bool = False) -> Dict[str, str]:
        """Merge custom headers with defaults and rotate User-Agent.
        
        Args:
            custom_headers: Custom headers to override defaults
            skip_referer: Skip adding Google Referer header
            minimal: Use minimal headers only (for POST form submissions to avoid bot detection)
        """
        if minimal:
            # DuckDuckGo POST search detects bots by checking header combinations
            # Use ONLY User-Agent for search POST - multiple headers trigger bot detection
            # Test showed: User-Agent only = 31,116 chars (success)
            # Test showed: User-Agent + Accept + others = 4,536 chars (bot detected)
            headers = {
                'User-Agent': self._get_rotated_user_agent()
            }
        else:
            headers = self.default_headers.copy()
            # Rotate User-Agent for each request
            headers['User-Agent'] = self._get_rotated_user_agent()
            # Add Referer header to appear more legitimate (skip for certain requests like POST to DuckDuckGo)
            if not skip_referer:
                headers['Referer'] = 'https://www.google.com/'
        if custom_headers:
            headers.update(custom_headers)
        return headers
    
    async def fetch_url(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        rate_limit: float = 1.0,
        respect_robots: Optional[bool] = None,
        method: str = "GET",
        data: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Fetch content from a URL with retry logic, rate limiting, and robots.txt compliance.
        
        Args:
            url: URL to fetch
            headers: Optional custom headers
            rate_limit: Minimum delay between requests to this domain
            respect_robots: Whether to respect robots.txt (default: use settings.scraper_respect_robots)
            method: HTTP method to use ("GET" or "POST")
            data: Optional form data for POST requests
        
        Returns:
            HTML content or None if failed
        """
        # Use setting if not explicitly specified
        if respect_robots is None:
            respect_robots = settings.scraper_respect_robots
        
        # Check robots.txt compliance
        if respect_robots and not robots_checker.can_fetch(url):
            logger.warning(f"Skipping {url} - disallowed by robots.txt")
            return None
        
        # Get crawl delay from robots.txt if specified
        if respect_robots:
            robots_delay = robots_checker.get_crawl_delay(url)
            if robots_delay and robots_delay > rate_limit:
                logger.debug(f"Using robots.txt crawl delay of {robots_delay}s instead of {rate_limit}s")
                rate_limit = robots_delay
        
        domain = self._get_domain(url)
        # Use minimal headers for POST requests to avoid bot detection
        is_post = (method.upper() == "POST")
        merged_headers = self._merge_headers(headers, skip_referer=is_post, minimal=is_post)
        
        # Apply rate limiting with small random jitter (more human-like)
        await rate_limiter.wait_if_needed(domain, rate_limit)
        jitter = random.uniform(0.1, 0.5)  # Add 100-500ms random delay
        await asyncio.sleep(jitter)
        
        # Single attempt only - no retries to avoid wasting time
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=self.follow_redirects
            ) as client:
                logger.debug(f"Fetching {url} via {method}")
                
                # Choose GET or POST based on method parameter
                if method.upper() == "POST" and data:
                    logger.info(f"[POST-DEBUG] Making POST to {url} with data={data}, headers={merged_headers}")
                    response = await client.post(url, data=data, headers=merged_headers)
                    logger.info(f"[POST-DEBUG] Response status={response.status_code}, length={len(response.content)}, url={response.url}")
                else:
                    response = await client.get(url, headers=merged_headers)
                
                response.raise_for_status()
                
                # Handle encoding properly - detect from Content-Type header or response
                content_type = response.headers.get('content-type', '').lower()
                
                # Check if response is actually HTML/text
                if not any(t in content_type for t in ['html', 'text', 'xml', 'json']):
                    logger.warning(f"Non-text content type '{content_type}' for {url}")
                    return None
                
                # Try to decode with proper charset detection
                try:
                    # First try httpx's auto-detection
                    text = response.text
                    
                    # Validate it's actually readable text (not binary garbage)
                    if len(text) > 100:
                        printable_count = sum(c.isprintable() or c.isspace() for c in text[:1000])
                        printable_ratio = printable_count / min(1000, len(text))
                        
                        # If less than 85% printable, try alternative decoding
                        if printable_ratio < 0.85:
                            logger.warning(f"Initial decode quality low ({printable_ratio:.1%}) for {url}, trying alternative encodings")
                            
                            best_text = text
                            best_ratio = printable_ratio
                            best_encoding = 'httpx-auto'
                            
                            # First, try charset-normalizer for intelligent detection
                            try:
                                from charset_normalizer import from_bytes
                                
                                # Let charset-normalizer analyze the raw bytes
                                results = from_bytes(response.content)
                                if results:
                                    best_match = results.best()
                                    if best_match and best_match.encoding:
                                        detected_text = str(best_match)
                                        detected_printable = sum(c.isprintable() or c.isspace() for c in detected_text[:1000])
                                        detected_ratio = detected_printable / min(1000, len(detected_text))
                                        
                                        logger.info(f"charset-normalizer detected: {best_match.encoding} ({detected_ratio:.1%} readable, confidence: {best_match.encoding_confidence:.0%})")
                                        
                                        if detected_ratio > best_ratio:
                                            best_text = detected_text
                                            best_ratio = detected_ratio
                                            best_encoding = f'charset-normalizer:{best_match.encoding}'
                            except ImportError:
                                logger.debug("charset-normalizer not available, using fallback encoding detection")
                            except Exception as e:
                                logger.debug(f"charset-normalizer failed: {e}, using fallback")
                            
                            # Fallback: Try common encodings manually
                            if best_ratio < 0.70:  # Only if charset-normalizer didn't help enough
                                for encoding in ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1', 'cp1252']:
                                    try:
                                        alt_text = response.content.decode(encoding, errors='replace')
                                        alt_text = alt_text.replace('�', '')
                                        
                                        alt_printable = sum(c.isprintable() or c.isspace() for c in alt_text[:1000])
                                        alt_ratio = alt_printable / min(1000, len(alt_text))
                                        
                                        logger.debug(f"  Tried {encoding}: {alt_ratio:.1%} readable")
                                        
                                        if alt_ratio > best_ratio:
                                            best_text = alt_text
                                            best_ratio = alt_ratio
                                            best_encoding = encoding
                                        
                                        if alt_ratio > 0.95:
                                            logger.info(f"Excellent decode with {encoding} ({alt_ratio:.1%} readable)")
                                            text = alt_text
                                            break
                                    except (UnicodeDecodeError, AttributeError) as e:
                                        logger.debug(f"  {encoding} failed: {e}")
                                        continue
                            
                            # Use best encoding found
                            if best_ratio > 0.30:  # Accept content above 30% readable
                                if best_ratio < printable_ratio:
                                    # Don't downgrade if original was better
                                    logger.info(f"Keeping original httpx decode ({printable_ratio:.1%}) - better than alternatives")
                                else:
                                    logger.info(f"Using {best_encoding} encoding ({best_ratio:.1%} readable)")
                                    text = best_text
                                    
                                    # Additional aggressive cleaning for low-quality content
                                    if best_ratio < 0.60:
                                        text = text.replace('\x00', '')  # NULL bytes
                                        text = text.replace('\ufffd', '')  # Replacement character
                                        text = ''.join(c for c in text if ord(c) < 0x10000)  # Remove high Unicode
                                        logger.debug(f"Applied aggressive cleaning for low-quality content")
                            else:
                                # Content is truly unrecoverable (<30% readable)
                                logger.error(f"All encodings failed for {url} (best: {best_encoding} at {best_ratio:.1%}) - likely binary content")
                                return None
                    
                    logger.info(f"Successfully fetched {url} ({len(text)} chars)")
                    return text
                except UnicodeDecodeError as e:
                    logger.error(f"Encoding error for {url}: {e}")
                    return None
                
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.warning(f"HTTP error {status_code} for {url}")
            return None
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching {url} - skipping")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def scrape_article(
        self,
        url: str,
        source_config: SourceConfig
    ) -> Optional[ArticleContent]:
        """
        Scrape a single article using source configuration.
        
        Args:
            url: Article URL
            source_config: Source configuration with selectors
        
        Returns:
            ArticleContent object or None if failed
        """
        try:
            # Make URL absolute if relative
            if url.startswith('/'):
                url = urljoin(source_config.base_url, url)
            
            # Fetch HTML
            html = await self.fetch_url(
                url,
                headers=source_config.headers,
                rate_limit=source_config.rate_limit
            )
            
            if not html:
                return None
            
            # Log HTML quality (but don't reject - we'll try to extract what we can)
            if len(html) > 100:
                sample = html[:1000]
                printable = sum(c.isprintable() or c.isspace() for c in sample)
                ratio = printable / len(sample)
                if ratio < 0.70:
                    logger.warning(f"HTML quality low for {url} (readable: {ratio:.1%}) - will try to extract usable content")
            
            # Extract content using selectors
            if source_config.selectors:
                extracted = self.content_extractor.extract_with_selectors(
                    html,
                    source_config.selectors
                )
            else:
                # Fallback to generic extraction
                extracted = self.content_extractor.extract_generic(html)
            
            # Clean the content
            title = self.content_extractor.clean_text(extracted.get('title', ''))
            content = self.content_extractor.clean_text(extracted.get('content', ''))
            
            # Log content quality before validation
            if content:
                sample = content[:500]
                readable = sum(c.isalnum() or c.isspace() or c in '.,!?;:()-"\'' for c in sample)
                ratio = readable / len(sample) if len(sample) > 0 else 0
                logger.info(f"Content quality after cleaning: {ratio:.1%} readable (sample: {sample[:100]!r})")
            
            # Validate content
            if not self.content_extractor.is_valid_content(content):
                # logger.warning(
                #     f"Invalid or insufficient content from {url} "
                #     f"(title_len={len(title) if title else 0}, "
                #     f"content_len={len(content) if content else 0}, "
                #     f"extracted_fields={list(extracted.keys())})"
                # )
                return None
            
            # Create ArticleContent object
            article = ArticleContent(
                url=url,
                title=title or "Untitled",
                content=content,
                author=extracted.get('author'),
                source_name=source_config.name
            )
            
            logger.info(f"Successfully scraped article from {url}")
            return article
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None
    
    async def fetch_google_search_api(
        self,
        query: str,
        max_results: int = 10
    ) -> List[str]:
        """
        Fetch search results from Google Custom Search API with automatic pagination.
        
        Google API Limits:
        - Max 10 results per request (Google's hard limit)
        - Automatically paginates for requests > 10
        - Filters out social media/video platforms
        
        Args:
            query: Search query string
            max_results: Maximum number of article URLs to return (will make multiple API calls if > 10)
        
        Returns:
            List of article URLs (deduplicated, social/video filtered)
        """
        if not settings.google_cse_api_key or not settings.google_cse_id:
            logger.error("Google Custom Search API credentials not configured")
            return []
        
        # Social/video platforms to filter out (can't scrape as articles)
        EXCLUDED_DOMAINS = {
            'youtube.com', 'youtu.be', 
            'facebook.com', 'fb.com',
            'twitter.com', 'x.com',
            'instagram.com',
            'tiktok.com', 
            'vimeo.com',
            'linkedin.com/posts',
            'reddit.com/r/'
        }
        
        try:
            all_urls = []
            seen_urls = set()  # Deduplication
            filtered_count = 0
            total_fetched = 0
            
            # Calculate API requests needed (Google max: 10 results/request)
            num_requests = min((max_results + 9) // 10, 10)  # Cap at 100 results (10 requests)
            
            logger.info(f"Fetching Google Custom Search: '{query}' (target: {max_results} results, {num_requests} API calls)")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for page in range(num_requests):
                    # Check if we have enough results
                    if len(all_urls) >= max_results:
                        break
                    
                    start_index = page * 10 + 1
                    results_per_request = min(10, max_results - len(all_urls) + filtered_count)  # Request extra to account for filtering
                    
                    params = {
                        'key': settings.google_cse_api_key,
                        'cx': settings.google_cse_id,
                        'q': query,
                        'num': min(results_per_request, 10),  # Google's hard limit
                        'start': start_index
                    }
                    
                    try:
                        response = await client.get(
                            "https://www.googleapis.com/customsearch/v1",
                            params=params,
                            timeout=10.0
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                    except httpx.TimeoutException:
                        logger.warning(f"Google API timeout on page {page + 1}, continuing with {len(all_urls)} results")
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 429:
                            logger.error("Google API rate limit exceeded")
                        else:
                            logger.error(f"Google API HTTP {e.response.status_code}: {e.response.text[:200]}")
                        break
                    
                    # Check if results exist
                    if 'items' not in data or not data['items']:
                        logger.debug(f"No more results after {total_fetched} fetched")
                        break
                    
                    items = data['items']
                    total_fetched += len(items)
                    
                    # Extract and filter URLs
                    for item in items:
                        if 'link' not in item:
                            continue
                        
                        url = item['link']
                        
                        # Skip duplicates
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        # Filter out social/video platforms
                        url_lower = url.lower()
                        if any(domain in url_lower for domain in EXCLUDED_DOMAINS):
                            filtered_count += 1
                            logger.debug(f"Filtered social/video: {url[:60]}...")
                            continue
                        
                        all_urls.append(url)
                        
                        # Stop if we have enough
                        if len(all_urls) >= max_results:
                            break
                    
                    # Stop if Google returned fewer results than requested
                    if len(items) < params['num']:
                        logger.debug(f"Google returned {len(items)} < {params['num']} requested, stopping pagination")
                        break
                
                # Summary logging
                logger.info(
                    f"Google API: Fetched {total_fetched} results, "
                    f"filtered {filtered_count} social/video, "
                    f"returning {len(all_urls)} article URLs"
                )
                
                return all_urls
                
        except Exception as e:
            logger.error(f"Unexpected error in Google API fetch: {type(e).__name__}: {e}")
            return []
    
    async def scrape_search_results(
        self,
        source_config: SourceConfig,
        query: str,
        max_search_results: Optional[int] = None,
        max_articles_to_process: Optional[int] = None,
        cancellation_check: Optional[callable] = None
    ) -> List[ArticleContent]:
        """
        Scrape articles from search results with cancellation support.
        Supports both HTML scraping and API-based sources (Google Custom Search).
        
        Args:
            source_config: Source configuration
            query: Search query
            max_search_results: Maximum URL results to extract (overrides source config and global)
            max_articles_to_process: Maximum articles to scrape (overrides source config and global)
            cancellation_check: Optional function that returns True if operation should be cancelled
        
        Returns:
            List of ArticleContent objects
        """
        articles = []
        
        # Determine effective limits with priority: param > source config > global settings
        # 1. Get global defaults
        effective_max_search_results = settings.max_search_results
        effective_max_articles = settings.max_articles_to_process
        
        # 2. Override with source config if provided
        if source_config.max_search_results is not None:
            effective_max_search_results = source_config.max_search_results
        if source_config.max_articles_to_process is not None:
            effective_max_articles = source_config.max_articles_to_process
        
        # 3. Override with function parameters if provided
        if max_search_results is not None:
            effective_max_search_results = max_search_results
        if max_articles_to_process is not None:
            effective_max_articles = max_articles_to_process
        
        # Validation: max_search_results > 0
        if effective_max_search_results <= 0:
            logger.warning(f"Invalid max_search_results ({effective_max_search_results}), using default 10")
            effective_max_search_results = 10
        
        # Validation: if max_search_results < max_articles_to_process, make them equal
        if effective_max_search_results < effective_max_articles:
            logger.info(
                f"max_search_results ({effective_max_search_results}) < max_articles_to_process ({effective_max_articles}), "
                f"setting max_search_results = max_articles_to_process"
            )
            effective_max_search_results = effective_max_articles
        
        logger.info(
            f"[SCRAPING] Source {source_config.name}: max_search_results={effective_max_search_results}, "
            f"max_articles_to_process={effective_max_articles}"
        )
        
        try:
            # Check cancellation before starting
            if cancellation_check and cancellation_check():
                logger.info(f"[CANCELLED] Scraping cancelled before fetching search results from {source_config.name}")
                return articles
            
            # Check if this is an API-based source (Google Custom Search)
            is_api_based = source_config.name == "Google" or (
                hasattr(source_config, 'api_based') and 
                getattr(source_config, 'api_based', False)
            )
            
            article_links = []
            
            if is_api_based and source_config.name == "Google":
                # Use Google Custom Search API
                logger.info(f"[GOOGLE-API] Using Google Custom Search API for: {query}")
                article_links = await self.fetch_google_search_api(
                    query=query,
                    max_results=effective_max_search_results
                )
                
                if not article_links:
                    logger.warning("[GOOGLE-API] No results from Google API, falling back to DuckDuckGo")
                    return articles
                
                logger.info(f"[GOOGLE-API] Got {len(article_links)} results from Google API")
            else:
                # Use HTML scraping (DuckDuckGo and others)
                # Build search URL
                if not source_config.search_url_template:
                    logger.warning(f"No search URL template for {source_config.name}")
                    return articles
                
                search_url = source_config.search_url_template.format(query=query)
                
                # Prepare request data if POST method is configured
                request_method = getattr(source_config, 'request_method', 'GET')
                request_data = None
                
                if request_method.upper() == "POST" and hasattr(source_config, 'request_data') and source_config.request_data:
                    # Replace {query} placeholder in form data values
                    request_data = {
                        key: value.format(query=query) if isinstance(value, str) else value
                        for key, value in source_config.request_data.items()
                    }
                    logger.info(f"[SCRAPING] Using POST request with form data for {source_config.name}: {request_data}")
                
                logger.info(f"[SCRAPING] Fetching search results from {source_config.name}: {search_url} via {request_method}")
                # Fetch search results page with POST support
                html = await self.fetch_url(
                    search_url,
                    headers=source_config.headers,
                    rate_limit=source_config.rate_limit,
                    method=request_method,
                    data=request_data
                )
                
                if not html:
                    return articles
                
                # Check cancellation after fetching search page
                if cancellation_check and cancellation_check():
                    logger.info(f"[CANCELLED] Scraping cancelled after fetching search results from {source_config.name}")
                    return articles
                
                # Extract article links
                link_selector = source_config.selectors.get('article_links', 'a')
                logger.debug(f"Using link selector: {link_selector}")
                
                article_links = self.content_extractor.extract_links(html, link_selector)
                
                # Limit links to max_search_results
                article_links = article_links[:effective_max_search_results]
                
                logger.info(f"Found {len(article_links)} article links from {source_config.name} (limited to {effective_max_search_results})")
                if len(article_links) > 0:
                    logger.debug(f"First 5 links: {article_links[:5]}")
                else:
                    logger.warning(f"No links found with selector: {link_selector}")
            
            # Scrape articles (up to max_articles_to_process)
            # Note: We continue trying articles until we get max_articles_to_process successful scrapes
            scraped_count = 0
            failed_count = 0
            attempted_count = 0
            
            for idx, link in enumerate(article_links, 1):
                attempted_count = idx  # Track last attempted index
                
                # Check cancellation before each article
                if cancellation_check and cancellation_check():
                    logger.info(f"[CANCELLED] Scraping cancelled at article {idx}/{len(article_links)} (scraped: {scraped_count}, failed: {failed_count})")
                    return articles
                
                # Stop if we have enough successful scrapes
                if scraped_count >= effective_max_articles:
                    logger.info(f"[SCRAPING] Reached target of {effective_max_articles} articles, stopping")
                    break
                
                logger.info(f"[SCRAPING] Fetching article {idx}/{len(article_links)} from {source_config.name}: {link[:80]}...")
                
                article = await self.scrape_article(link, source_config)
                
                if article:
                    articles.append(article)
                    scraped_count += 1
                    logger.info(f"[SCRAPING] Successfully scraped article {idx} from {source_config.name} ({scraped_count}/{effective_max_articles})")
                else:
                    failed_count += 1
                    # logger.warning(f"[SCRAPING] Failed to scrape article {idx} from {source_config.name} (failures: {failed_count})")
            
            if attempted_count > 0:
                logger.info(
                    f"Scraped {scraped_count} articles from {source_config.name} "
                    f"(attempted: {attempted_count}, failed: {failed_count})"
                )
            else:
                logger.warning(f"No articles to scrape from {source_config.name}")
            
        except Exception as e:
            logger.error(f"Error scraping search results from {source_config.name}: {e}")
        
        return articles
    
    async def scrape_sources(
        self,
        sources: List[SourceConfig],
        query: str,
        max_search_results: Optional[int] = None,
        max_articles_to_process: Optional[int] = None
    ) -> List[ArticleContent]:
        """
        Scrape articles from multiple sources.
        
        Args:
            sources: List of source configurations
            query: Search query
            max_search_results: Global override for max search results (optional)
            max_articles_to_process: Global override for max articles to process (optional)
        
        Returns:
            Combined list of ArticleContent objects
        """
        all_articles = []
        
        logger.info(f"Starting scraping from {len(sources)} sources for query: '{query}'")
        
        for source in sources:
            if not source.enabled:
                logger.debug(f"Skipping disabled source: {source.name}")
                continue
            
            try:
                articles = await self.scrape_search_results(
                    source,
                    query,
                    max_search_results,
                    max_articles_to_process
                )
                all_articles.extend(articles)
                logger.info(f"Got {len(articles)} articles from {source.name}")
                
            except Exception as e:
                logger.error(f"Error scraping {source.name}: {e}")
                continue
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles


# Global scraper manager instance
scraper_manager = ScraperManager()
