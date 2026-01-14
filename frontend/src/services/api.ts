import axios, { AxiosInstance } from 'axios';
import { 
  SearchQuery, 
  SearchResponse, 
  SessionResponse, 
  EventData, 
  SocialSearchResponse,
  FetchContentRequest,
  FetchContentResponse,
  AnalyseContentRequest,
  AnalyseContentResponse,
  SocialFullContent
} from '../types/events';

/**
 * API Service for communicating with the backend
 */
class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 600000, // 10 minutes for scraping + LLM processing
    });
  }

  /**
   * Execute a search with the given query parameters
   */
  async searchEvents(query: SearchQuery): Promise<SearchResponse> {
    // Clean the query - remove empty strings and undefined values
    // Backend expects null/undefined for optional fields, not empty strings
    const cleanedQuery: Partial<SearchQuery> = {
      phrase: query.phrase.trim(),
    };
    
    if (query.location?.trim()) {
      cleanedQuery.location = query.location.trim();
    }
    
    if (query.event_type) {
      cleanedQuery.event_type = query.event_type;
    }
    
    if (query.date_from) {
      cleanedQuery.date_from = query.date_from;
    }
    
    if (query.date_to) {
      cleanedQuery.date_to = query.date_to;
    }

    const response = await this.client.post<SearchResponse>('/api/v1/search', cleanedQuery);
    return response.data;
  }

  /**
   * Get results from a previous search session
   */
  async getSession(sessionId: string): Promise<SessionResponse> {
    const response = await this.client.get<SessionResponse>(`/api/v1/search/session/${sessionId}`);
    return response.data;
  }

  /**
   * Search social media platforms using Google Custom Search
   */
  async socialSearch(query: string, sites?: string[], resultsPerSite?: number): Promise<SocialSearchResponse> {
    const response = await this.client.post<SocialSearchResponse>('/api/v1/social-search', {
      query: query,
      sites: sites,
      results_per_site: resultsPerSite || 10
    });
    return response.data;
  }

  /**
   * Export events to Excel from a session
   */
  async exportExcelFromSession(sessionId: string): Promise<Blob> {
    const response = await this.client.post(
      `/api/v1/export/excel?session_id=${sessionId}`,
      {},
      { responseType: 'blob' }
    );
    return response.data;
  }

  /**
   * Export custom events to Excel
   */
  async exportExcelCustom(events: EventData[]): Promise<Blob> {
    const response = await this.client.post(
      '/api/v1/export/excel/custom',
      events,  // Send events array directly, not wrapped in object
      { responseType: 'blob' }
    );
    return response.data;
  }

  /**
   * Download a blob as a file
   */
  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Fetch full content from social media URL
   */
  async fetchSocialContent(request: FetchContentRequest): Promise<FetchContentResponse> {
    const response = await this.client.post<FetchContentResponse>(
      '/api/v1/social-content/fetch',
      request
    );
    return response.data;
  }

  /**
   * Analyse social content and extract event using LLM
   */
  async analyseSocialContent(request: AnalyseContentRequest): Promise<AnalyseContentResponse> {
    const response = await this.client.post<AnalyseContentResponse>(
      '/api/v1/social-content/analyse',
      request
    );
    return response.data;
  }

  /**
   * Check cache status for multiple URLs
   */
  async checkCacheStatus(urls: Array<{url: string, platform: string}>, llmModel?: string): Promise<{
    status: string;
    cache_status: Record<string, {content_cached: boolean, analysis_cached: boolean}>;
  }> {
    const response = await this.client.post('/api/v1/social-content/cache-status', {
      urls,
      llm_model: llmModel
    });
    return response.data;
  }

  /**
   * Get social content cache statistics
   */
  async getSocialContentCacheStats(): Promise<{
    total_cached: number;
    active_cached: number;
    expired_cached: number;
    platforms: Record<string, number>;
  }> {
    const response = await this.client.get('/api/v1/social-content/cache/stats');
    return response.data;
  }

  /**
   * Clear social content cache
   */
  async clearSocialContentCache(platform?: string): Promise<{ message: string; cleared: number }> {
    const url = platform 
      ? `/api/v1/social-content/cache/clear?platform=${platform}`
      : '/api/v1/social-content/cache/clear';
    const response = await this.client.post(url);
    return response.data;
  }

  /**
   * Export social media search results to Excel
   */
  async exportSocialEvents(
    items: Array<{
      url: string;
      platform: string;
      title: string;
      snippet: string;
      display_link: string;
      cached_content?: SocialFullContent;
      cached_analysis?: EventData;
    }>,
    platformFilter?: string,
    llmModel?: string
  ): Promise<Blob> {
    const response = await this.client.post(
      '/api/v1/export/social-events',
      {
        items,
        platform_filter: platformFilter,
        llm_model: llmModel
      },
      { responseType: 'blob' }
    );
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
