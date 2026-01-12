"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from datetime import datetime, timedelta
from typing import List
from loguru import logger
import json
import asyncio
import httpx

from app.settings import settings
from app.utils.logger import setup_logging
from app.services.ollama_service import OllamaClient
from app.services.llm_router import llm_router
from app.services.config_manager import config_manager
from app.services.event_extractor import event_extractor
from app.services.search_service import search_service
from app.services.excel_exporter import excel_exporter
from app.services.social_search_service import social_search_service
from app.services.social_content_aggregator import social_content_aggregator
from app.models import (
    SourcesListResponse,
    ArticleContent,
    EventData,
    ExtractedEntities,
    SearchQuery,
    SearchResponse,
    SearchStatus,
    SocialSearchRequest,
    SocialSearchResponse,
    FetchContentRequest,
    FetchContentResponse,
    AnalyseContentRequest,
    AnalyseContentResponse
)

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Event Scraper API",
    version="1.0.0",
    description="Web scraping tool for event extraction and summarization"
)

# CORS Configuration
cors_origins = [origin.strip() for origin in settings.cors_origins.split(',')] if settings.cors_origins else ["http://localhost:5173"]
logger.info(f"CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ollama client
ollama_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global ollama_client
    
    logger.info("Starting Event Scraper API...")
    logger.info(f"Ollama URL: {settings.ollama_url}")
    logger.info(f"Ollama Model: {settings.ollama_model}")
    
    # Log social media API configuration status
    logger.info("=== Social Media API Configuration ===")
    logger.info(f"YouTube API: {'✓ Configured' if settings.youtube_api_key else '✗ Not configured'}")
    logger.info(f"Facebook API: {'✓ Configured' if settings.facebook_access_token else '✗ Not configured'}")
    if settings.facebook_access_token:
        logger.info(f"  Token: {settings.facebook_access_token[:20]}...")
    logger.info(f"Twitter API: {'✓ Configured' if settings.twitter_bearer_token else '✗ Not configured'}")
    logger.info(f"Instagram API: {'✓ Configured' if settings.instagram_access_token else '✗ Not configured'}")
    logger.info("=======================================")
    
    # Initialize Ollama client
    try:
        ollama_client = OllamaClient(
            base_url=settings.ollama_url,
            default_model=settings.ollama_model
        )
        logger.info("Ollama client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama client: {e}")
        logger.warning("API will start but Ollama features may not work")
    
    # Load source configurations
    try:
        sources = config_manager.load_sources()
        logger.info(f"Loaded {len(sources)} sources ({config_manager.get_enabled_count()} enabled)")
    except FileNotFoundError:
        logger.warning("sources.yaml not found - create it in config/ directory")
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Event Scraper API...")


# Health Check Endpoints

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dictionary with health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/v1/ollama/status")
async def ollama_status():
    """
    Check Ollama connection status.
    
    Returns:
        Dictionary with Ollama connection status and configuration
    """
    if ollama_client is None:
        return {
            "status": "not_initialized",
            "error": "Ollama client not initialized"
        }
    
    try:
        # Test connection
        is_connected = ollama_client.test_connection()
        
        return {
            "status": "connected" if is_connected else "disconnected",
            "model": ollama_client.default_model,
            "base_url": ollama_client.base_url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ollama status check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "model": settings.ollama_model,
            "base_url": settings.ollama_url,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/v1/llm/status")
async def llm_status():
    """
    Get status of all LLM providers (Ollama and Claude).
    
    Returns:
        Dictionary with provider status and availability
    """
    try:
        status = llm_router.get_provider_status()
        return {
            **status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM status check failed: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/v1/llm/models")
async def llm_models():
    """
    List all available LLM models from all providers.
    
    Returns:
        Dictionary with models by provider
    """
    try:
        models = llm_router.list_available_models()
        return {
            "models": models,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM models listing failed: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/v1/llm/usage")
async def llm_usage():
    """
    Get Claude API usage statistics.
    
    Returns:
        Dictionary with usage stats including costs
    """
    try:
        usage = llm_router.get_claude_usage()
        return {
            "usage": usage,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM usage stats failed: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/v1/llm/reset-stats")
async def llm_reset_stats():
    """
    Reset Claude API usage statistics.
    
    Returns:
        Success message
    """
    try:
        llm_router.reset_claude_stats()
        return {
            "status": "success",
            "message": "Claude usage stats reset",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM stats reset failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Dictionary with API information and available endpoints
    """
    return {
        "name": "Event Scraper API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "ollama_status": "/api/v1/ollama/status",
            "llm_status": "/api/v1/llm/status",
            "llm_models": "/api/v1/llm/models",
            "llm_usage": "/api/v1/llm/usage",
            "llm_reset_stats": "/api/v1/llm/reset-stats",
            "sources": "/api/v1/sources",
            "search": "/api/v1/search",
            "export_excel": "/api/v1/export/excel",
            "extract_event": "/api/v1/extract/event",
            "extract_event_simple": "/api/v1/extract/event/simple",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Configuration Endpoints

@app.get("/api/v1/sources", response_model=SourcesListResponse)
async def get_sources(enabled_only: bool = True):
    """
    Get list of configured news sources.
    
    Args:
        enabled_only: If True, return only enabled sources (default: True)
    
    Returns:
        SourcesListResponse with list of sources and counts
    """
    try:
        sources = config_manager.get_sources(enabled_only=enabled_only)
        
        return SourcesListResponse(
            sources=sources,
            total_count=config_manager.get_total_count(),
            enabled_count=config_manager.get_enabled_count()
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="sources.yaml configuration file not found. Please create config/sources.yaml"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Error retrieving sources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sources: {str(e)}")


# Social Search Endpoint

@app.post("/api/v1/social-search", response_model=SocialSearchResponse)
async def social_search(request: SocialSearchRequest):
    """
    Search social media platforms using Google Custom Search Engine.
    
    This endpoint uses Google's Custom Search API to search across
    configured social media platforms like YouTube, Twitter/X, Facebook, Instagram, etc.
    
    Args:
        request: SocialSearchRequest with query, sites, and results_per_site
    
    Returns:
        SocialSearchResponse with search results
    
    Example:
        ```
        POST /api/v1/social-search
        {
            "query": "cybersecurity breach 2025",
            "sites": ["youtube.com", "x.com"],
            "results_per_site": 10
        }
        ```
    """
    try:
        logger.info(f"Social search request: '{request.query}' from sites: {request.sites or ['youtube.com', 'x.com', 'facebook.com', 'instagram.com']}")
        
        # Execute social search
        results = await social_search_service.search(
            query=request.query,
            sites=request.sites,
            results_per_site=request.results_per_site
        )
        
        return SocialSearchResponse(
            status="success",
            query=request.query,
            sites=request.sites or ['youtube.com', 'x.com', 'facebook.com', 'instagram.com'],
            total_results=len(results),
            results=results
        )
        
    except Exception as e:
        logger.error(f"Social search endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Social search failed: {str(e)}"
        )


# Social Content Fetch Endpoint

@app.post("/api/v1/social-content/fetch", response_model=FetchContentResponse)
async def fetch_social_content(request: FetchContentRequest):
    """
    Fetch full content from a social media post/tweet/video URL.
    
    Uses platform-specific APIs (YouTube, Twitter, Facebook, Instagram)
    to retrieve complete content including text, media, and engagement metrics.
    
    Results are cached for 24 hours (configurable) to reduce API calls.
    
    Args:
        request: FetchContentRequest with URL, platform, and force_refresh flag
    
    Returns:
        FetchContentResponse with full social content
    
    Example:
        ```
        POST /api/v1/social-content/fetch
        {
            "url": "https://youtube.com/watch?v=VIDEO_ID",
            "platform": "youtube",
            "force_refresh": false
        }
        ```
    """
    try:
        logger.info(f"Fetch content request: {request.platform} - {request.url}")
        
        # Fetch content using aggregator (with caching)
        content = await social_content_aggregator.fetch_content(
            url=request.url,
            platform=request.platform,
            force_refresh=request.force_refresh
        )
        
        if not content:
            return FetchContentResponse(
                status="error",
                error="Could not fetch content from the provided URL. Please check the URL and API credentials.",
                from_cache=False
            )
        
        return FetchContentResponse(
            status="success",
            content=content,
            from_cache=content.cached if hasattr(content, 'cached') else False,
            rate_limit_remaining=None,  # TODO: Track rate limits
            rate_limit_reset=None
        )
        
    except Exception as e:
        logger.error(f"Fetch content endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch content: {str(e)}"
        )


# Social Content Analysis Endpoint

@app.post("/api/v1/social-content/analyse", response_model=AnalyseContentResponse)
async def analyse_social_content(request: AnalyseContentRequest):
    """
    Analyse social media content and extract event information using LLM.
    
    Uses the existing LLM service (Claude/Ollama with fallback) to analyse
    the full social media content and extract structured event information.
    
    Args:
        request: AnalyseContentRequest with content and optional LLM model
    
    Returns:
        AnalyseContentResponse with extracted event data
    
    Example:
        ```
        POST /api/v1/social-content/analyse
        {
            "content": {...full social content object...},
            "llm_model": "claude-3-5-haiku-20241022"
        }
        ```
    """
    try:
        start_time = datetime.utcnow()
        logger.info(f"Analysing {request.content.platform} content: {request.content.url}")
        
        # Check cache first for existing analysis
        cached_event = social_content_aggregator.get_cached_analysis(
            request.content.url,
            request.llm_model
        )
        
        if cached_event:
            # Return cached analysis
            logger.info(f"✅ Returning cached analysis for: {request.content.url}")
            return AnalyseContentResponse(
                status="success",
                event=cached_event,
                llm_model_used="cached",
                processing_time_seconds=0.0
            )
        
        # Prepare content for LLM
        # Combine title (if YouTube), text, and description into analysis text
        analysis_text = ""
        if request.content.title:
            analysis_text += f"Title: {request.content.title}\n\n"
        if request.content.text:
            analysis_text += f"{request.content.text}\n\n"
        if request.content.description and request.content.description != request.content.text:
            analysis_text += f"Description: {request.content.description}\n\n"
        
        # Add context about the post
        analysis_text += f"\nPosted by: {request.content.author.name}\n"
        analysis_text += f"Platform: {request.content.platform}\n"
        analysis_text += f"Posted at: {request.content.posted_at.isoformat()}\n"
        analysis_text += f"URL: {request.content.url}\n"
        
        if not analysis_text.strip():
            return AnalyseContentResponse(
                status="error",
                error="No text content available to analyse"
            )
        
        # Extract event using existing LLM service
        # Use specified model or default from settings
        model_to_use = request.llm_model if request.llm_model else None
        
        # Auto-detect provider from model name
        # Claude models start with "claude-", everything else is Ollama
        provider_to_use = None
        if model_to_use:
            if model_to_use.startswith("claude-"):
                provider_to_use = "claude"
            else:
                provider_to_use = "ollama"
        
        logger.info(f"Extracting event using LLM provider: {provider_to_use or 'default'}, model: {model_to_use or 'default'}")
        
        # Call event_extractor with proper parameters
        event_tuple = await event_extractor.extract_event(
            title=request.content.title or f"{request.content.platform.title()} Post",
            content=analysis_text,
            url=request.content.url,
            source_name=request.content.platform.title(),
            article_published_date=request.content.posted_at,
            llm_provider=provider_to_use,
            llm_model=model_to_use
        )
        
        # Extract event and metadata from tuple (returns tuple[EventData, Dict])
        event = event_tuple[0] if event_tuple else None
        metadata = event_tuple[1] if event_tuple and len(event_tuple) > 1 else {}
        
        if not event:
            error_msg = metadata.get("error", "Failed to extract event from content")
            return AnalyseContentResponse(
                status="error",
                error=error_msg
            )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Get the model that was actually used from metadata
        # Format: "provider:model" (e.g., "ollama:qwen2.5:latest" or "claude:claude-3-5-haiku-20241022")
        llm_model_used = metadata.get("model", model_to_use or "default")
        provider = metadata.get("provider", "unknown")
        if provider != "unknown":
            llm_model_used = f"{provider}:{llm_model_used}"
        
        # Cache the successful analysis result
        social_content_aggregator.save_analysis_to_cache(
            request.content.url,
            event,
            request.llm_model
        )
        
        return AnalyseContentResponse(
            status="success",
            event=event,
            llm_model_used=llm_model_used,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"Analyse content endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyse content: {str(e)}"
        )


# Cache Management Endpoints

@app.get("/api/v1/social-content/cache/stats")
async def get_cache_stats():
    """Get cache statistics for social media content."""
    try:
        stats = social_content_aggregator.get_cache_stats()
        return {
            "status": "success",
            **stats
        }
    except Exception as e:
        logger.error(f"Get cache stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/social-content/cache/clear")
async def clear_cache(platform: str = None):
    """Clear cache for specific platform or all platforms."""
    try:
        social_content_aggregator.clear_cache(platform)
        return {
            "status": "success",
            "message": f"Cache cleared for {platform if platform else 'all platforms'}"
        }
    except Exception as e:
        logger.error(f"Clear cache failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Image Proxy Endpoint (for CORS bypass)

@app.get("/api/v1/proxy-image")
async def proxy_image(url: str):
    """
    Proxy images from social media platforms to bypass CORS restrictions.
    
    This endpoint fetches images from external sources (like Facebook CDN)
    and serves them through our backend, avoiding CORS policy issues.
    
    Args:
        url: The image URL to proxy
    
    Returns:
        Image content with appropriate headers
    
    Example:
        GET /api/v1/proxy-image?url=https://external.xx.fbcdn.net/...
    """
    try:
        logger.debug(f"Proxying image: {url}")
        
        # Validate URL to prevent abuse
        allowed_domains = [
            'fbcdn.net',           # Facebook CDN
            'fbsbx.com',           # Facebook external image CDN (lookaside.fbsbx.com)
            'facebook.com',        # Facebook direct images
            'twimg.com',           # Twitter images
            'cdninstagram.com',    # Instagram CDN
            'instagram.com',       # Instagram direct images
            'scontent.cdninstagram.com', # Instagram content CDN
            'ytimg.com',           # YouTube thumbnails
            'googleusercontent.com', # Google cached images
            'gstatic.com'          # Google static content CDN (for encrypted-tbn0.gstatic.com thumbnails)
        ]
        
        # Check if URL is from an allowed domain
        if not any(domain in url.lower() for domain in allowed_domains):
            logger.warning(f"Attempted to proxy image from unauthorized domain: {url}")
            raise HTTPException(
                status_code=403,
                detail="Image domain not allowed"
            )
        
        # Fetch the image with redirect following
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # Use different headers for Instagram to avoid anti-bot protection
            if 'instagram.com' in url.lower():
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.instagram.com/',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'same-site'
                }
            else:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.google.com/'
                }
            
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Log response details
            content_length = len(response.content)
            logger.info(f"Fetched image: {content_length} bytes, status: {response.status_code}, final URL: {response.url}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # If response is suspiciously small, log warning
            if content_length < 1000:
                logger.warning(f"Suspiciously small image response: {content_length} bytes from {url}")
                logger.warning(f"Response content preview: {response.content[:200]}")
            
            # Determine content type - force image content type to prevent ORB blocking
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            # If content type is generic/octet-stream, try to detect from URL or default to jpeg
            if 'octet-stream' in content_type or not content_type.startswith('image/'):
                if url.lower().endswith('.png') or 'png' in url.lower():
                    content_type = 'image/png'
                elif url.lower().endswith('.gif') or 'gif' in url.lower():
                    content_type = 'image/gif'
                elif url.lower().endswith('.webp') or 'webp' in url.lower():
                    content_type = 'image/webp'
                else:
                    content_type = 'image/jpeg'  # Default to JPEG
            
            logger.debug(f"Serving image with content-type: {content_type}")
            
            # Return image with comprehensive CORS headers to prevent ORB blocking
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Expose-Headers': '*',
                    'Cross-Origin-Resource-Policy': 'cross-origin',  # Critical for ORB
                    'Cross-Origin-Embedder-Policy': 'unsafe-none',  # Allow embedding
                    'X-Content-Type-Options': 'nosniff',
                    'Vary': 'Origin',  # Important for caching with CORS
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error proxying image: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch image: {e.response.status_code}"
        )
    except httpx.TimeoutException:
        logger.error(f"Timeout proxying image: {url}")
        raise HTTPException(
            status_code=504,
            detail="Image fetch timeout"
        )
    except Exception as e:
        logger.error(f"Error proxying image: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to proxy image: {str(e)}"
        )


# OPTIONS handler for proxy-image (CORS preflight)
@app.options("/api/v1/proxy-image")
async def proxy_image_options():
    """Handle CORS preflight requests for image proxy."""
    return Response(
        status_code=200,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '86400',  # Cache preflight for 24 hours
        }
    )


# Search Endpoint

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_events(
    query: SearchQuery,
    max_articles: int = 50,
    min_relevance_score: float = 0.1
):
    """
    Execute end-to-end event search.
    
    This endpoint orchestrates the complete search pipeline:
    1. Scrapes articles from configured sources
    2. Extracts entities and events from articles
    3. Matches and ranks events by relevance to query
    4. Stores results in session for later retrieval/export
    
    Args:
        query: SearchQuery with phrase, filters, and date range
        max_articles: Maximum articles to scrape per source (default: 50)
        min_relevance_score: Minimum relevance score (0.0-1.0) to include results (default: 0.1)
    
    Returns:
        SearchResponse with matched events, session ID, and metadata
    
    Example:
        ```
        POST /api/v1/search
        {
            "phrase": "protest in Mumbai",
            "location": "India",
            "event_type": "protest",
            "date_from": "2025-11-01",
            "date_to": "2025-12-31"
        }
        ```
    """
    try:
        logger.info(f"Search request: '{query.phrase}' (max_articles={max_articles}, min_score={min_relevance_score})")
        
        # Execute search pipeline
        response = await search_service.search(
            query=query,
            max_articles=max_articles,
            min_relevance_score=min_relevance_score
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Search endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/api/v1/search/stream")
async def search_events_stream(
    phrase: str,
    location: str = None,
    event_type: str = None,
    date_from: str = None,
    date_to: str = None,
    max_articles: int = 50,
    min_relevance_score: float = 0.1,
    llm_provider: str = None,
    llm_model: str = None
):
    """
    Execute search with real-time Server-Sent Events (SSE) streaming.
    
    This endpoint streams events as they are extracted, allowing the frontend
    to update in real-time instead of waiting for the entire search to complete.
    
    Event Types:
        - progress: Progress updates (current/total, percentage, message)
        - event: New event extracted (sent immediately)
        - complete: Search completed successfully
        - cancelled: Search cancelled by user
        - error: Error occurred
    
    Args:
        phrase: Search phrase (required)
        location: Location filter (optional)
        event_type: Event type filter (optional)
        date_from: Start date filter YYYY-MM-DD (optional)
        date_to: End date filter YYYY-MM-DD (optional)
        max_articles: Maximum articles to scrape per source
        min_relevance_score: Minimum relevance score (0.0-1.0)
    
    Returns:
        StreamingResponse with Server-Sent Events
    
    Example:
        ```javascript
        const eventSource = new EventSource('/api/v1/search/stream?phrase=bombing');
        eventSource.addEventListener('event', (e) => {
            const eventData = JSON.parse(e.data);
            // Add event to UI immediately
        });
        eventSource.addEventListener('progress', (e) => {
            const progress = JSON.parse(e.data);
            // Update progress bar
        });
        ```
    """
    try:
        # Build SearchQuery from query parameters
        # No default date range - let search engines and "recent" keyword handle recency
        query = SearchQuery(
            phrase=phrase,
            location=location if location else None,
            event_type=event_type if event_type else None,
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None
        )
        
        # Create session first
        session_id = search_service.session_store.create_session(
            query=query,
            results=[],
            status=SearchStatus.PENDING
        )
        
        logger.info(f"Starting streaming search: session={session_id}, query='{query.phrase}'")
        
        async def event_generator():
            """Generate SSE events."""
            try:
                # Send session_id first with proper SSE event type
                yield f"event: session\n"
                yield f"data: {json.dumps({'session_id': session_id})}\n\n"
                
                # Delay to ensure session event is received by frontend
                await asyncio.sleep(1.0)
                
                # Stream search results
                async for event in search_service.search_stream(
                    query=query,
                    session_id=session_id,
                    max_articles_to_process=max_articles,
                    min_relevance_score=min_relevance_score,
                    llm_provider=llm_provider,
                    llm_model=llm_model
                ):
                    # Format as SSE
                    event_type = event.get("event_type", "message")
                    data = event.get("data", {})
                    
                    # Send event
                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # Small delay to prevent overwhelming client
                    await asyncio.sleep(0.01)
                    
            except asyncio.CancelledError:
                logger.info(f"Client disconnected for session {session_id}")
                search_service.session_store.cancel_session(session_id)
                raise
            except Exception as e:
                logger.error(f"Stream error for session {session_id}: {e}", exc_info=True)
                yield f"event: error\n"
                yield f"data: {json.dumps({'message': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "X-Session-ID": session_id,  # Send session ID in header for immediate access
                "Access-Control-Allow-Origin": "*",  # Ensure CORS for SSE
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Expose-Headers": "X-Session-ID"
            }
        )
        
    except Exception as e:
        logger.error(f"Streaming search endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Streaming search failed: {str(e)}"
        )


@app.post("/api/v1/search/cancel/{session_id}")
async def cancel_search(session_id: str):
    """
    Cancel an ongoing search session.
    
    This endpoint marks a session as cancelled. The search will stop
    processing new articles but will keep already extracted events.
    
    Args:
        session_id: Session ID to cancel
    
    Returns:
        Success message with number of events extracted before cancellation
    
    Example:
        ```
        POST /api/v1/search/cancel/550e8400-e29b-41d4-a716-446655440000
        ```
    """
    try:
        logger.info(f"Cancel request received for session {session_id}")
        
        session = search_service.session_store.get_session(session_id)
        
        if not session:
            logger.warning(f"Session {session_id} not found")
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Cancel the session
        search_service.session_store.cancel_session(session_id)
        
        # Get current results
        results = search_service.session_store.get_results(session_id)
        event_count = len(results) if results else 0
        
        logger.info(f"Session {session_id} cancelled. {event_count} event(s) extracted.")
        
        return {
            "status": "cancelled",
            "session_id": session_id,
            "message": f"Search cancelled. {event_count} event(s) extracted.",
            "events_extracted": event_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel search: {str(e)}"
        )


@app.get("/api/v1/search/session/{session_id}")
async def get_session_results(session_id: str):
    """
    Retrieve results from a previous search session.
    
    Args:
        session_id: Session ID from search response
    
    Returns:
        List of events from the session
    """
    try:
        results = search_service.get_session_results(session_id)
        
        if results is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or expired"
            )
        
        return {
            "session_id": session_id,
            "events": results,
            "total_events": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session: {str(e)}"
        )


# Excel Export Endpoints

@app.post("/api/v1/export/excel")
async def export_events_to_excel(session_id: str, include_metadata: bool = True):
    """
    Export events from a session to Excel file.
    
    Args:
        session_id: Session ID from search response
        include_metadata: Whether to include summary/metadata sheet (default: True)
    
    Returns:
        Excel file download (streaming response)
    
    Example:
        ```
        POST /api/v1/export/excel?session_id=abc-123&include_metadata=true
        ```
    """
    try:
        # Retrieve events from session
        events = search_service.get_session_results(session_id)
        
        if events is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or expired"
            )
        
        if not events:
            raise HTTPException(
                status_code=400,
                detail="Session has no events to export"
            )
        
        logger.info(f"Exporting {len(events)} events from session {session_id}")
        
        # Generate Excel file
        excel_bytes = excel_exporter.export_to_bytes(
            events=events,
            include_metadata=include_metadata
        )
        
        # Generate filename
        filename = excel_exporter.get_default_filename()
        
        # Return as streaming response
        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Excel export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Excel export failed: {str(e)}"
        )


@app.post("/api/v1/export/excel/custom")
async def export_custom_events_to_excel(
    events: list[EventData],
    include_metadata: bool = True
):
    """
    Export custom list of events to Excel file.
    
    This endpoint allows exporting a custom selection of events
    without requiring a session ID.
    
    Args:
        events: List of EventData objects to export
        include_metadata: Whether to include summary/metadata sheet (default: True)
    
    Returns:
        Excel file download (streaming response)
    
    Example:
        ```
        POST /api/v1/export/excel/custom
        {
            "events": [...],
            "include_metadata": true
        }
        ```
    """
    try:
        if not events:
            raise HTTPException(
                status_code=400,
                detail="No events provided for export"
            )
        
        logger.info(f"Exporting {len(events)} custom events")
        
        # Generate Excel file
        excel_bytes = excel_exporter.export_to_bytes(
            events=events,
            include_metadata=include_metadata
        )
        
        # Generate filename
        filename = excel_exporter.get_default_filename()
        
        # Return as streaming response
        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom Excel export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Excel export failed: {str(e)}"
        )


# Event Extraction Endpoints

@app.post("/api/v1/extract/event", response_model=EventData)
async def extract_event_from_text(article: ArticleContent):
    """
    Extract event data from article content using Ollama LLM.
    
    Args:
        article: ArticleContent object with title, content, url, etc.
    
    Returns:
        EventData object with extracted event information
    """
    if not event_extractor.is_available():
        raise HTTPException(
            status_code=503,
            detail="Event extraction service not available. Check Ollama connection."
        )
    
    try:
        logger.info(f"Extracting event from article: {article.title[:50]}...")
        
        event_data = await event_extractor.extract_from_article(article)
        
        if event_data is None:
            raise HTTPException(
                status_code=422,
                detail="Failed to extract event data. LLM may have returned invalid format."
            )
        
        return event_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Event extraction failed: {str(e)}")


@app.post("/api/v1/extract/event/simple")
async def extract_event_simple(
    title: str,
    content: str,
    url: str = None
):
    """
    Extract event data from simple text inputs (convenience endpoint).
    
    Args:
        title: Article title
        content: Article content
        url: Optional article URL
    
    Returns:
        EventData object with extracted event information
    """
    if not event_extractor.is_available():
        raise HTTPException(
            status_code=503,
            detail="Event extraction service not available. Check Ollama connection."
        )
    
    try:
        logger.info(f"Extracting event from: {title[:50]}...")
        
        event_data = await event_extractor.extract_event(
            title=title,
            content=content,
            url=url
        )
        
        if event_data is None:
            raise HTTPException(
                status_code=422,
                detail="Failed to extract event data. LLM may have returned invalid format."
            )
        
        return event_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Event extraction failed: {str(e)}")


# Development/Testing endpoint
@app.get("/api/v1/test/ollama")
async def test_ollama_generation():
    """
    Test Ollama generation with a simple prompt.
    
    Returns:
        Dictionary with test prompt and generated response
    """
    if ollama_client is None:
        raise HTTPException(status_code=503, detail="Ollama client not initialized")
    
    try:
        test_prompt = "Say 'Hello, World!' in a friendly way."
        response = ollama_client.generate(test_prompt)
        
        return {
            "status": "success",
            "model": ollama_client.default_model,
            "prompt": test_prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ollama test generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
