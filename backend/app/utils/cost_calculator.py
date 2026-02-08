"""
Cost calculation utilities for different API services.
"""

from typing import Dict, Any

# Pricing constants based on requirements
GOOGLE_CSE_COST_PER_CALL = 0.005  # $0.005 per API call
SCRAPECREATORS_FREELANCE_COST_PER_CREDIT = 0.00188  # $47 / 25,000 credits
CLAUDE_HAIKU_COST_AVERAGE = 0.0010  # $0.001 per analysis (with 50% caching)

# Platform-specific credit usage for ScrapeCreators
SCRAPECREATORS_CREDITS = {
    'youtube': 0,  # Direct scraping via Google CSE, count as 1 Google API call
    'twitter': 1.5,  # 1-2 credits average
    'facebook': 2.5,  # 2-3 credits average
    'instagram': 2.5,  # 2-3 credits average
    'google': 0,  # Direct scraping, no cost
    'web': 0,  # Direct scraping, no cost
}


class CostCalculator:
    """Calculate costs for different API operations."""
    
    @staticmethod
    def calculate_google_cse_cost(api_calls: int) -> float:
        """
        Calculate Google Custom Search API cost.
        
        Args:
            api_calls: Number of API calls made
        
        Returns:
            Cost in USD
        """
        return api_calls * GOOGLE_CSE_COST_PER_CALL
    
    @staticmethod
    def calculate_scrapecreators_cost(credits_used: int) -> float:
        """
        Calculate ScrapeCreators API cost (Freelance plan).
        
        Args:
            credits_used: Number of credits consumed
        
        Returns:
            Cost in USD
        """
        return credits_used * SCRAPECREATORS_FREELANCE_COST_PER_CREDIT
    
    @staticmethod
    def calculate_claude_analysis_cost(analyses_count: int = 1) -> float:
        """
        Calculate Claude AI analysis cost (with caching).
        
        Args:
            analyses_count: Number of analyses performed
        
        Returns:
            Cost in USD
        """
        return analyses_count * CLAUDE_HAIKU_COST_AVERAGE
    
    @staticmethod
    def get_platform_credits(platform: str) -> float:
        """
        Get average credits needed for a platform.
        
        Args:
            platform: Platform name
        
        Returns:
            Average credits needed
        """
        return SCRAPECREATORS_CREDITS.get(platform.lower(), 0)
    
    @staticmethod
    def calculate_search_cost(platforms: list, max_results: int = 20) -> Dict[str, Any]:
        """
        Calculate cost for a multi-platform search.
        
        Args:
            platforms: List of platforms to search
            max_results: Max results per platform (affects API calls)
        
        Returns:
            Dictionary with cost breakdown
        """
        # Each platform with max_results=20 requires 2 API calls
        # max_results=10 requires 1 call, max_results=50 requires 5 calls
        api_calls_per_platform = max(1, max_results // 10)
        total_api_calls = len(platforms) * api_calls_per_platform
        total_cost = CostCalculator.calculate_google_cse_cost(total_api_calls)
        
        return {
            'platforms': len(platforms),
            'max_results_per_platform': max_results,
            'api_calls_per_platform': api_calls_per_platform,
            'total_api_calls': total_api_calls,
            'cost_per_search': total_cost
        }
    
    @staticmethod
    def calculate_scraping_cost(platform: str) -> Dict[str, Any]:
        """
        Calculate cost for scraping full content from a platform.
        
        Args:
            platform: Platform name
        
        Returns:
            Dictionary with cost breakdown
        """
        credits = CostCalculator.get_platform_credits(platform)
        
        if platform.lower() == 'youtube':
            # YouTube counts as 1 Google API call
            return {
                'platform': platform,
                'api_provider': 'google_cse',
                'api_calls': 1,
                'credits_used': 0,
                'cost_usd': GOOGLE_CSE_COST_PER_CALL
            }
        elif credits > 0:
            # Twitter, Facebook, Instagram use ScrapeCreators
            return {
                'platform': platform,
                'api_provider': 'scrapecreators',
                'api_calls': 0,
                'credits_used': int(credits),
                'cost_usd': CostCalculator.calculate_scrapecreators_cost(credits)
            }
        else:
            # Google/Web - direct scraping, no cost
            return {
                'platform': platform,
                'api_provider': 'direct',
                'api_calls': 0,
                'credits_used': 0,
                'cost_usd': 0.0
            }


# Global instance
cost_calculator = CostCalculator()
