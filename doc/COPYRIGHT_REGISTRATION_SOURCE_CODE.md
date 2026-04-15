# COPYRIGHT REGISTRATION - SOURCE CODE DOCUMENTATION

## Project Information

**Software Name:** Social Searcher - Event Intelligence Platform

**Software Type:** Web Application (Full Stack)

**Nature of Work:** Original Computer Software

**Description:** AI-powered web intelligence tool for extracting, analyzing, and exporting structured event data from news sources and social media platforms using Large Language Models (Claude AI/Anthropic) and natural language processing.

**Technology Stack:**
- Backend: Python 3.8+, FastAPI, AsyncIO
- Frontend: React 18.2, TypeScript, Material-UI
- AI/ML: Claude API (Anthropic), Natural Language Processing
- Database: PostgreSQL
- Deployment: Docker, Nginx

**Primary Features:**
1. Intelligent event extraction from news articles and social media
2. AI-powered content analysis using Claude API
3. Multi-platform social media search (YouTube, Twitter/X, Facebook, Instagram)
4. Advanced entity extraction and event classification
5. Real-time streaming search with progress tracking
6. Excel export functionality for analyzed events
7. User authentication and role-based access control
8. API usage tracking and cost analysis

**Owner/Author:** APT Software
**Domain:** tigerosint.aptsoftware.in
**Date of Creation:** 2024-2026
**Date of Publication:** 2026

---

## COPYRIGHT NOTICE

© 2024-2026 APT Software. All Rights Reserved.

This software and associated documentation files constitute proprietary and confidential information of APT Software. Unauthorized copying, distribution, modification, or use of this software, via any medium, is strictly prohibited without express written permission from APT Software.

---

## SOURCE CODE DOCUMENTATION

### Part 1: First 10 Pages of Source Code

The following sections contain the first 500+ lines of core source code from the application:

---

#### File: backend/app/main.py (Lines 1-250)

```python
"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException, Depends
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
from app.services.database_service import db_service
from app.routers.auth_router import router as auth_router, user_router
from app.auth import get_current_active_user, TokenData
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
    AnalyseContentResponse,
    ExportSocialEventsRequest
)

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Event Scraper API",
    version="1.0.0",
    description="Web scraping tool for event extraction and summarization"
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)

# CORS Configuration
cors_origins = [origin.strip() for origin in settings.cors_origins.split(',')] if settings.cors_origins else ["http://localhost:5173"]
# logger.info(f"CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Ollama client
ollama_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global ollama_client
    
    # logger.info("Starting Event Scraper API...")
    # logger.info(f"Ollama URL: {settings.ollama_url}")
    # logger.info(f"Ollama Model: {settings.ollama_model}")
    
    # Log social media API configuration status
    # logger.info("=== Social Media API Configuration ===")
    # logger.info(f"YouTube API: {'✓ Configured' if settings.youtube_api_key else '✗ Not configured'}")
    # logger.info(f"Facebook API: {'✓ Configured' if settings.facebook_access_token else '✗ Not configured'}")
    # if settings.facebook_access_token:
    #     logger.info(f"  Token: {settings.facebook_access_token[:20]}...")
    # logger.info(f"Twitter API: {'✓ Configured' if settings.twitter_bearer_token else '✗ Not configured'}")
    # logger.info(f"Instagram API: {'✓ Configured' if settings.instagram_access_token else '✗ Not configured'}")
    # logger.info("=======================================")
    
    # Initialize Ollama client
    try:
        ollama_client = OllamaClient(
            base_url=settings.ollama_url,
            default_model=settings.ollama_model
        )
        # logger.info("Ollama client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama client: {e}")
        logger.warning("API will start but Ollama features may not work")
    
    # Load source configurations
    try:
        sources = config_manager.load_sources()
        # logger.info(f"Loaded {len(sources)} sources ({config_manager.get_enabled_count()} enabled)")
    except FileNotFoundError:
        logger.warning("sources.yaml not found - create it in config/ directory")
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    # logger.info("Shutting down Event Scraper API...")


# Health Check Endpoints

@app.get("/health")
async def root_health_check():
    """
    Simple health check endpoint for Docker health checks.
    
    Returns:
        Dictionary with health status
    """
    return {"status": "healthy"}


@app.get("/v1/health")
async def health_check():
    """
    Detailed health check endpoint with database connectivity.
    
    Returns:
        Dictionary with health status and timestamp
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "llm": "configured"
        }
    }
    
    return health_status


@app.get("/v1/ollama/status")
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


@app.get("/v1/llm/status")
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


@app.get("/v1/llm/models")
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


@app.get("/v1/llm/usage")
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
```

---

#### File: backend/app/models.py (Lines 1-250)

```python
"""
Pydantic models for the Event Scraper API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from uuid import UUID, uuid4


class EventType(str, Enum):
    """Enumeration of event types as per requirement document."""
    # Violence & Security Events
    PROTEST = "protest"
    DEMONSTRATION = "demonstration"
    ATTACK = "attack"
    EXPLOSION = "explosion"
    BOMBING = "bombing"
    SHOOTING = "shooting"
    THEFT = "theft"
    KIDNAPPING = "kidnapping"
    MILITARY_OPERATION = "military_operation"
    
    # Cyber Events
    CYBER_ATTACK = "cyber_attack"
    CYBER_INCIDENT = "cyber_incident"
    DATA_BREACH = "data_breach"
    
    # Meetings & Conferences
    CONFERENCE = "conference"
    MEETING = "meeting"
    SUMMIT = "summit"
    
    # Disasters & Accidents
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    
    # Political & Military
    ELECTION = "election"
    POLITICAL_EVENT = "political_event"
    
    # Other/Unknown
    OTHER = "other"


class PerpetratorType(str, Enum):
    """Classification of perpetrator types."""
    TERRORIST_GROUP = "terrorist_group"
    STATE_ACTOR = "state_actor"
    CRIMINAL_ORGANIZATION = "criminal_organization"
    INDIVIDUAL = "individual"
    MULTIPLE_PARTIES = "multiple_parties"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    MILITARY_OPERATION = "military_operation"
    
    # Crisis Events
    TERRORIST_ACTIVITY = "terrorist_activity"
    CIVIL_UNREST = "civil_unrest"
    HUMANITARIAN_CRISIS = "humanitarian_crisis"
    
    # Other
    OTHER = "other"


class Location(BaseModel):
    """Location information."""
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": float, "lon": float}
    
    def __str__(self) -> str:
        """Return human-readable location string."""
        parts = [p for p in [self.city, self.state, self.country] if p]
        return ", ".join(parts) if parts else "Unknown"


class ExtractedEntities(BaseModel):
    """Named entities extracted from text using spaCy."""
    persons: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)


class ArticleContent(BaseModel):
    """Raw article content from web scraping."""
    id: UUID = Field(default_factory=uuid4)
    url: str
    title: Optional[str] = None
    content: str
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    source_name: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class EventData(BaseModel):
    """Structured event data extracted from article."""
    # Core event information
    event_type: EventType
    event_sub_type: Optional[str] = None  # Secondary classification (e.g., "suicide bombing", "mass shooting")
    title: str
    summary: str
    
    # Perpetrator information (separate from participants)
    perpetrator: Optional[str] = None  # Who carried out the event (for attacks, bombings, etc.)
    perpetrator_type: Optional[PerpetratorType] = None  # Classification of perpetrator
    
    # Location details (full and parsed components)
    location: Location  # Contains city, region, country parsed separately
    
    # Temporal information
    event_date: Optional[datetime] = None  # When the event occurred
    event_time: Optional[str] = None  # Time of day if available (HH:MM format or text like "morning")
    
    # People and organizations involved
    participants: List[str] = Field(default_factory=list)  # Individuals involved
    organizations: List[str] = Field(default_factory=list)  # Organizations involved
    
    # Impact assessment
    casualties: Optional[Dict[str, int]] = None  # {"killed": int, "injured": int}
    impact: Optional[str] = None
    
    # Source metadata
    source_name: Optional[str] = None  # News source name (e.g., "BBC News")
    source_url: Optional[str] = None  # URL of the source article
    article_published_date: Optional[datetime] = None  # When article was published
    collection_timestamp: Optional[datetime] = None  # When the system collected/scraped the content
    
    # Quality metrics
    confidence: float = Field(ge=0.0, le=1.0)  # Extraction confidence score
    
    # Raw content for reference
    full_content: Optional[str] = None  # Complete article text that was processed
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Event(BaseModel):
    """Complete event with source article and extracted data."""
    id: UUID = Field(default_factory=uuid4)
    article: ArticleContent
    entities: ExtractedEntities
    event_data: EventData
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class SearchQuery(BaseModel):
    """User search query parameters."""
    phrase: str = Field(..., min_length=1, description="Search phrase or keywords")
    location: Optional[str] = Field(None, description="Location filter (city, country, region)")
    event_type: Optional[EventType] = Field(None, description="Filter by event type")
    date_from: Optional[Union[datetime, date, str]] = Field(None, description="Start date filter (YYYY-MM-DD or ISO datetime)")
    date_to: Optional[Union[datetime, date, str]] = Field(None, description="End date filter (YYYY-MM-DD or ISO datetime)")
    max_results: int = Field(default=50, ge=1, le=500, description="Maximum results to return")
    
    @field_validator('date_from', 'date_to', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date string to datetime object."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            # Convert date to datetime at start of day
            return datetime.combine(v, datetime.min.time())
        if isinstance(v, str):
            # Try to parse date-only string (YYYY-MM-DD)
            try:
                parsed_date = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return parsed_date
            except ValueError:
                # Try date-only format
                try:
                    parsed_date = datetime.strptime(v, '%Y-%m-%d')
                    return parsed_date
                except ValueError:
                    raise ValueError(f"Invalid date format: {v}. Expected YYYY-MM-DD or ISO datetime")
        return v
    
    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure date_to is after date_from."""
        if v and info.data.get('date_from') and v < info.data['date_from']:
            raise ValueError('date_to must be after date_from')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SourceConfig(BaseModel):
    """Configuration for a single news source."""
    name: str
    base_url: str
    enabled: bool = True
    api_based: bool = Field(default=False, description="Whether this source uses an API instead of HTML scraping")
    search_url_template: Optional[str] = None  # URL template with {query} placeholder
    rate_limit: float = Field(default=1.0, ge=0.1, description="Minimum seconds between requests")
    selectors: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    
    # HTTP request configuration (for generic search engine support)
    request_method: str = Field(default="GET", description="HTTP method to use (GET or POST)")
    request_data: Optional[Dict[str, str]] = Field(None, description="Form data for POST requests (supports {query} placeholder)")
    
    # Scraping limits (optional - if not set, global defaults are used)
    max_search_results: Optional[int] = Field(None, description="Maximum URL results to extract from search (overrides global)")
    max_articles_to_process: Optional[int] = Field(None, description="Maximum articles to scrape and process (overrides global)")
    
    # Selectors that might be in the config
    # {
    #   "article_links": "a.article-link",
    #   "title": "h1.article-title",
    #   "content": "div.article-body",
    #   "date": "time.publish-date",
    #   "author": "span.author-name"
    # }


class SearchStatus(str, Enum):
    """Search session status."""
    PENDING = "pending"
    PROCESSING = "processing"
```

---

### Part 2: Last 10 Pages of Source Code

The following sections contain the last 500+ lines of core source code from the application:

---

#### File: backend/app/models.py (Lines 344-594)

```python
    link: str
    snippet: str
    display_link: str
    formatted_url: str
    source_site: str
    pagemap: Optional[Dict[str, Any]] = None


class SocialSearchResponse(BaseModel):
    """Response from social media search."""
    status: str
    query: str
    sites: List[str]
    total_results: int
    results: List[SocialSearchResult]
    counts: Optional[Dict[str, int]] = None  # Platform-wise counts


# ===== Social Media Full Content Models =====

class SocialContentAuthor(BaseModel):
    """Author/creator information for social media content."""
    name: str
    username: Optional[str] = None
    profile_url: Optional[str] = None
    profile_picture: Optional[str] = None
    verified: bool = False


class SocialContentMedia(BaseModel):
    """Media attachments (images, videos) for social content."""
    type: str  # "image", "video", "gif"
    url: str
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None  # For videos, in seconds


class SocialContentEngagement(BaseModel):
    """Engagement metrics for social content."""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    retweets: int = 0  # Twitter specific
    replies: int = 0   # Twitter specific


class SocialFullContent(BaseModel):
    """Full content fetched from social media platform APIs."""
    # Identification
    platform: str  # "facebook", "twitter", "youtube", "instagram"
    content_type: str  # "post", "tweet", "video", "story"
    url: str
    platform_id: str  # Post/Tweet/Video ID from the platform
    
    # Content
    text: Optional[str] = None
    title: Optional[str] = None  # For YouTube videos
    description: Optional[str] = None  # For YouTube videos
    
    # Author/Creator
    author: SocialContentAuthor
    
    # Timestamps
    posted_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Media
    media: List[SocialContentMedia] = Field(default_factory=list)
    
    # Engagement
    engagement: SocialContentEngagement = Field(default_factory=SocialContentEngagement)
    
    # Platform-specific data (stored as JSON)
    platform_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Extracted event (after LLM analysis)
    extracted_event: Optional['EventData'] = None
    
    # Cache metadata
    cached: bool = False
    cache_expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FetchContentRequest(BaseModel):
    """Request to fetch full content from a social media URL."""
    url: str = Field(..., description="Social media post/tweet/video URL")
    platform: str = Field(..., description="Platform name: facebook, twitter, youtube, instagram")
    force_refresh: bool = Field(False, description="Force refresh even if cached")
    llm_model: Optional[str] = Field(None, description="LLM model name to check for cached analysis")


class FetchContentResponse(BaseModel):
    """Response with full social media content."""
    status: str
    content: Optional[SocialFullContent] = None
    error: Optional[str] = None
    from_cache: bool = False
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None


class AnalyseContentRequest(BaseModel):
    """Request to analyse social content and extract events."""
    content: SocialFullContent
    llm_model: Optional[str] = Field(None, description="LLM model to use (default: from settings)")


class AnalyseContentResponse(BaseModel):
    """Response with extracted event from social content."""
    status: str
    event: Optional[EventData] = None
    error: Optional[str] = None
    llm_model_used: Optional[str] = None
    processing_time_seconds: Optional[float] = None


class SocialEventExportItem(BaseModel):
    """Social search result with optional cached content and analysis."""
    url: str
    platform: str
    title: str
    snippet: str
    display_link: str
    cached_content: Optional[SocialFullContent] = None
    cached_analysis: Optional[EventData] = None


class ExportSocialEventsRequest(BaseModel):
    """Request to export social media search results."""
    items: List[SocialEventExportItem]
    platform_filter: Optional[str] = Field(None, description="Platform name for filename (e.g., 'youtube', 'twitter')")
    llm_model: Optional[str] = Field(None, description="LLM model used for analysis")


# ==================== AUTHENTICATION MODELS ====================

class UserResponse(BaseModel):
    """User response model (without password)."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CreateUserRequest(BaseModel):
    """Create user request model (for admin)."""
    email: str
    username: str
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    is_admin: bool = False


class UpdateUserRequest(BaseModel):
    """Update user request model."""
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None  # Optional password for admin reset


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    old_password: str
    new_password: str


class UsageDailyBreakdown(BaseModel):
    """Daily usage breakdown."""
    usage_date: date
    total_searches: int = 0
    youtube_searches: int = 0
    twitter_searches: int = 0
    facebook_searches: int = 0
    instagram_searches: int = 0
    google_searches: int = 0
    total_scrapings: int = 0
    paid_scrapings: int = 0
    free_scrapings: int = 0
    total_analyses: int = 0
    google_api_calls: int = 0
    scrapecreators_credits: int = 0
    claude_tokens: int = 0
    daily_cost_usd: float = 0.0


class UsageMonthlySummary(BaseModel):
    """Monthly usage summary."""
    year: int
    month: int
    total_searches: int = 0
    youtube_searches: int = 0
    twitter_searches: int = 0
    facebook_searches: int = 0
    instagram_searches: int = 0
    google_searches: int = 0
    total_scrapings: int = 0
    paid_scrapings: int = 0
    free_scrapings: int = 0
    total_analyses: int = 0
    google_api_calls: int = 0
    scrapecreators_credits: int = 0
    claude_tokens: int = 0
    monthly_cost_usd: float = 0.0
    daily_breakdown: List[UsageDailyBreakdown] = []


class UserUsageReportRequest(BaseModel):
    """Request for user usage report."""
    user_id: int
    year: int
    month: int


class UserUsageReportResponse(BaseModel):
    """Response for user usage report."""
    user: UserResponse
    usage: UsageMonthlySummary
```

---

#### File: backend/app/main.py (Lines 1337-1587)

```python
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


@app.post("/v1/export/social-events")
async def export_social_events(
    request: ExportSocialEventsRequest
):
    """
    Export social media search results to Excel, including cached content and analysis.
    
    This endpoint exports social search results with their cached content and AI analysis
    if available. Supports platform-specific exports.
    
    Args:
        request: ExportSocialEventsRequest with items and optional platform filter
    
    Returns:
        Excel file download (streaming response)
    
    Example:
        ```
        POST /api/v1/export/social-events
        {
            "items": [
                {
                    "url": "https://youtube.com/watch?v=...",
                    "platform": "youtube",
                    "title": "Video Title",
                    "snippet": "Description...",
                    "display_link": "youtube.com",
                    "cached_content": {...},
                    "cached_analysis": {...}
                }
            ],
            "platform_filter": "youtube",
            "llm_model": "claude-3-haiku-20240307"
        }
        ```
    """
    try:
        if not request.items:
            raise HTTPException(
                status_code=400,
                detail="No items provided for export"
            )
        
        logger.info(f"Exporting {len(request.items)} social media events (platform: {request.platform_filter})")
        
        # Convert Pydantic models to dicts for export
        items_dict = [item.model_dump() for item in request.items]
        
        # Debug: Log first item to see structure
        if items_dict:
            first_item = items_dict[0]
            # logger.info(f"First item URL: {first_item.get('url', 'N/A')[:50]}...")
            # logger.info(f"First item - cached_content: {first_item.get('cached_content') is not None}")
            # logger.info(f"First item - cached_analysis: {first_item.get('cached_analysis') is not None}")
            if first_item.get('cached_analysis'):
                analysis = first_item['cached_analysis']
                # logger.info(f"Analysis title: {analysis.get('title', 'N/A')[:80]}...")
                # logger.info(f"Analysis event_type: {analysis.get('event_type', 'N/A')}")
            pass
        
        # Generate Excel file
        excel_bytes = excel_exporter.export_social_events_to_excel(
            items=items_dict,
            platform_filter=request.platform_filter
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_name = request.platform_filter.lower() if request.platform_filter else "social"
        filename = f"{platform_name}_events_{timestamp}.xlsx"
        
        # logger.info(f"Generated social export file: {filename}")
        
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
        logger.error(f"Social events export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Social events export failed: {str(e)}"
        )


# Event Extraction Endpoints

@app.post("/v1/extract/event", response_model=EventData)
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
        # logger.info(f"Extracting event from article: {article.title[:50]}...")
        
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


@app.post("/v1/extract/event/simple")
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
        # logger.info(f"Extracting event from: {title[:50]}...")
        
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
@app.get("/v1/test/ollama")
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
```

---

#### File: frontend/src/App.tsx (Lines 1-100)

```tsx
import { useState, useEffect } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, Box } from '@mui/material';
import SearchForm from './components/SearchForm';
import EventList from './components/EventList';
import ProgressBar from './components/ProgressBar';
import LLMConfigDropdown from './components/LLMConfigDropdown';
import SocialResultsPanel from './components/SocialResultsPanel';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import ProfileMenu from './components/ProfileMenu';
import { EventData, ProgressUpdate, SocialSearchResult } from './types/events';
import { streamService } from './services/streamService';
import { apiService } from './services/api';
import logoImage from './assets/aptvigilosint.webp';
import makeInIndiaLogo from './assets/Make_In_India.png';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  company?: string;
  profile_image_url?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Search state
  const [events, setEvents] = useState<EventData[]>([]);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchSummary, setSearchSummary] = useState<{ message: string; total_events: number } | null>(null);
  const [socialResults, setSocialResults] = useState<SocialSearchResult[]>([]);
  const [socialSearchQuery, setSocialSearchQuery] = useState<string>('');
  const [socialSearchSites, setSocialSearchSites] = useState<string[]>([]);
  const [socialSearchCounts, setSocialSearchCounts] = useState<{
    total: number;
    youtube: number;
    twitter: number;
    facebook: number;
    instagram: number;
    google: number;
  } | undefined>(undefined);
  
  // Track which platforms have no more results available
  const [platformsExhausted, setPlatformsExhausted] = useState<{
    youtube: boolean;
    twitter: boolean;
    facebook: boolean;
    instagram: boolean;
    google: boolean;
  }>({
    youtube: false,
    twitter: false,
    facebook: false,
    instagram: false,
    google: false,
  });

  // Check authentication on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLoginSuccess = (loggedInUser: User, authToken: string) => {
    setUser(loggedInUser);
```

---

## DECLARATION

This source code documentation contains the first 10 pages and last 10 pages of the original computer software titled "Social Searcher - Event Intelligence Platform". The complete source code comprises approximately 12,000+ lines across multiple Python, TypeScript, and React files.

The source code is original work created by the development team at APT Software and incorporates original algorithms, data structures, and implementations for:
- AI-powered event extraction and analysis
- Multi-platform social media integration
- Real-time streaming data processing
- Advanced natural language processing
- Secure authentication and authorization
- Complex data aggregation and export functionality

This documentation is submitted for copyright registration purposes as per the requirements of the Copyright Office, Government of India.

---

**Date:** February 25, 2026

**Submitted by:** APT Software

**Contact:** tigerosint.aptsoftware.in

---

## END OF DOCUMENT
