"""
Production configuration loader with environment variable support.
"""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Event Scraper API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # SSL/HTTPS
    ssl_enabled: bool = False
    ssl_cert_path: str = "./ssl/cert.pem"
    ssl_key_path: str = "./ssl/key.pem"
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"  # Qwen 2.5 3B - Good balance of speed and quality
    ollama_timeout: int = 60  # Timeout per article
    ollama_total_timeout: int = 300  # 5 minutes total timeout
    
    # Claude API
    claude_api_key: str = ""  # Set via CLAUDE_API_KEY in .env
    default_claude_model: str = "claude-3-5-haiku-20241022"  # Claude 3.5 Haiku - Fast and cost-effective
    claude_max_concurrent: int = 5  # Max concurrent Claude API requests
    claude_timeout: int = 30  # Claude API timeout in seconds
    
    # LLM Provider Selection
    default_llm_provider: str = "claude"  # "claude" or "ollama" - Changed to Claude as primary
    enable_llm_fallback: bool = True  # Fallback to alternate provider on failure (Claude → Ollama)
    
    # Scraping Limits (Global defaults - can be overridden per source)
    max_search_results: int = 10  # Maximum URL results to extract from search page
    max_articles_to_process: int = 5  # Maximum articles to scrape and process with LLM
    
    # Sources
    sources_config_path: str = "../config/sources.yaml"
    
    # Scraping
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    scraper_retry_delay: int = 2
    scraper_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    scraper_respect_robots: bool = False  # Set to True for production to respect robots.txt
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 60
    rate_limit_per_domain: bool = True
    
    # Session
    session_timeout: int = 3600
    session_max_size: int = 100
    
    # Logging
    log_dir: str = "logs"
    log_file: str = "app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"
    
    # Security
    enable_security_headers: bool = False
    api_key: str = ""
    
    # Performance (optimized for dual Xeon Gold 6140 - 72 threads)
    max_concurrent_scrapes: int = 10  # Increase parallel scraping
    max_concurrent_llm: int = 4  # Process multiple articles with LLM in parallel
    max_events_per_search: int = 100
    
    # NLP
    spacy_model: str = "en_core_web_sm"
    ner_confidence_threshold: float = 0.5
    
    # Query Matching Weights
    weight_text: float = 0.4
    weight_location: float = 0.25
    weight_date: float = 0.2
    weight_event_type: float = 0.15
    
    # Export
    export_max_rows: int = 1000
    export_temp_dir: str = "temp"
    
    # Google Custom Search Engine
    google_cse_api_key: str = ""  # Shared API key for both CSEs - Set via GOOGLE_CSE_API_KEY in .env
    google_cse_id: str = ""  # CSE #1: Web Search (articles/news, excludes social media) - Set via GOOGLE_CSE_ID in .env
    google_cse_social_id: str = ""  # CSE #2: Social Media Search ONLY (YouTube, Twitter/X, Facebook, Instagram) - Set via GOOGLE_CSE_SOCIAL_ID in .env
    
    # Social Media API Keys
    youtube_api_key: str = ""  # YouTube Data API v3
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    facebook_access_token: str = ""
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    instagram_access_token: str = ""
    twitter_api_key: str = ""
    twitter_api_key_secret: str = ""
    twitter_bearer_token: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    # Social Media Search Configuration
    max_social_search_results: int = 10
    enable_full_content_fetch: bool = True
    cache_social_content_hours: int = 24
    
    # ScrapeCreators Third-Party API Configuration
    scrapecreators_api_key: str = ""  # ScrapeCreators API key for third-party scraping
    twitter_scraper: str = "NATIVE"   # Options: NATIVE or SCRAPECREATORS
    facebook_scraper: str = "NATIVE"  # Options: NATIVE or SCRAPECREATORS
    instagram_scraper: str = "NATIVE" # Options: NATIVE or SCRAPECREATORS
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def ollama_url(self) -> str:
        """Alias for ollama_base_url for backward compatibility."""
        return self.ollama_base_url
    
    @property
    def log_path(self) -> Path:
        """Get full log file path."""
        return Path(self.log_dir) / self.log_file
    
    @property
    def sources_config_full_path(self) -> Path:
        """Get full path to sources config."""
        return Path(__file__).parent.parent / self.sources_config_path
    
    model_config = {
        "env_file": ".env",  # Look for .env in backend/ directory (same level as app/)
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields in .env
    }


# Global settings instance
settings = Settings()
