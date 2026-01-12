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
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class StreamEvent(BaseModel):
    """SSE stream event for real-time updates."""
    event_type: str  # 'progress', 'event', 'complete', 'error'
    session_id: str
    data: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ProgressUpdate(BaseModel):
    """Progress update for SSE streaming."""
    current: int  # Current article being processed
    total: int  # Total articles to process
    status: str  # Status message
    percentage: float  # 0-100


class SearchResponse(BaseModel):
    """Response from search API."""
    session_id: str  # UUID as string
    events: List[EventData]
    query: SearchQuery
    total_events: int
    processing_time_seconds: float
    articles_scraped: int = 0
    sources_scraped: int = 0
    status: str = "success"  # success, no_sources, no_articles, no_events, error, cancelled
    message: str = ""
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SourcesListResponse(BaseModel):
    """Response for listing configured sources."""
    sources: List[SourceConfig]
    total_count: int
    enabled_count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    ollama_status: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OllamaStatusResponse(BaseModel):
    """Ollama service status response."""
    status: str
    model: str
    available_models: List[str] = Field(default_factory=list)
    base_url: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ExportRequest(BaseModel):
    """Request to export events to Excel."""
    event_ids: List[str] = Field(..., min_length=1, description="List of event IDs to export")
    session_id: UUID = Field(..., description="Session ID from search response")


class SocialSearchRequest(BaseModel):
    """Request for social media search using Google Custom Search."""
    query: str = Field(..., description="Search query string")
    sites: Optional[List[str]] = Field(None, description="List of sites to search (e.g., ['youtube.com', 'x.com', 'facebook.com', 'instagram.com'])")
    results_per_site: int = Field(10, ge=1, le=100, description="Number of results to fetch per site")


class SocialSearchResult(BaseModel):
    """Individual search result from Google Custom Search."""
    title: str
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
