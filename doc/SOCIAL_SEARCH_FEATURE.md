# Social Media Search Feature

## Overview

This feature integrates Google Custom Search Engine (CSE) to search social media platforms (Facebook, Twitter/X) alongside regular web sources. Users can enable/disable this functionality via a checkbox in the search form.

## Implementation Details

### Backend Components

#### 1. Social Search Service
**File**: `backend/app/services/social_search_service.py`

- Handles Google Custom Search API integration
- Searches multiple social media sites (Facebook, X/Twitter)
- Returns structured search results with title, link, snippet, and source site
- Implements pagination to fetch up to the requested number of results per site

**Key Methods:**
- `search(query, sites, results_per_site)`: Main search method
- `_fetch_results(client, query, max_results)`: Internal method for API pagination

#### 2. API Endpoint
**Endpoint**: `POST /api/v1/social-search`

**Request Body:**
```json
{
  "query": "cybersecurity breach 2025",
  "sites": ["facebook.com", "x.com"],
  "results_per_site": 10
}
```

**Response:**
```json
{
  "status": "success",
  "query": "cybersecurity breach 2025",
  "sites": ["facebook.com", "x.com"],
  "total_results": 20,
  "results": [
    {
      "title": "Post title",
      "link": "https://...",
      "snippet": "Preview text...",
      "display_link": "facebook.com",
      "formatted_url": "https://...",
      "source_site": "facebook.com",
      "pagemap": {}
    }
  ]
}
```

#### 3. Configuration
**File**: `backend/app/settings.py`

New settings added:
- `google_cse_api_key`: Google Custom Search API Key
- `google_cse_id`: Google Custom Search Engine ID

**Environment Variables** (`.env` file):
```bash
GOOGLE_CSE_API_KEY="Your_Google_CSE_API_Key_Here"
GOOGLE_CSE_ID="Your_Google_CSE_ID_Here"
```

### Frontend Components

#### 1. Updated Types
**File**: `frontend/src/types/events.ts`

Added:
- `use_social_search?: boolean` to `SearchQuery` interface
- `SocialSearchResult` interface
- `SocialSearchResponse` interface

#### 2. Search Form Checkbox
**File**: `frontend/src/components/SearchForm.tsx`

- Added checkbox "Include Social Media Search (Facebook, Twitter/X)"
- Default: **Enabled** (checked)
- When enabled, makes a call to social search API before starting regular search
- Helper text explains the functionality

#### 3. API Service
**File**: `frontend/src/services/api.ts`

Added method:
```typescript
async socialSearch(
  query: string, 
  sites?: string[], 
  resultsPerSite?: number
): Promise<SocialSearchResponse>
```

## Setup Instructions

### 1. Google Custom Search Engine Setup

1. **Create Custom Search Engine**:
   - Go to https://cse.google.com
   - Click "Add" to create a new search engine
   - Add sites to search:
     - `www.facebook.com/*`
     - `www.x.com/*`
   - Get your **Search Engine ID** (cx parameter)

2. **Get API Key**:
   - Go to https://console.cloud.google.com/apis/credentials
   - Create credentials → API Key
   - Enable "Custom Search API" in your Google Cloud project
   - Copy the API key

3. **Configure Backend**:
   Edit `backend/.env`:
   ```bash
   GOOGLE_CSE_API_KEY="Your_Google_CSE_API_Key_Here"
   GOOGLE_CSE_ID="Your_Google_CSE_ID_Here"
   ```

### 2. Install Dependencies

No new dependencies required! The feature uses existing packages:
- Backend: `httpx` (already installed)
- Frontend: `axios` (already installed)

### 3. Start Services

```powershell
# Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm run dev
```

## Usage

### For End Users

1. Open the Event Scraper application
2. Fill in the search form with your query
3. The "Include Social Media Search" checkbox is **checked by default**
4. If you want **only** regular sources (no social media):
   - Uncheck the checkbox
5. Click "Search"

When enabled:
- Frontend calls social search API first
- Results are logged to console (can be displayed in UI - see Future Enhancements)
- Then proceeds with regular streaming search

### For Developers

**Calling Social Search Directly:**

```typescript
import { apiService } from './services/api';

// Search with defaults (Facebook and X, 10 results each)
const results = await apiService.socialSearch('cybersecurity attack');

// Custom sites and results
const results = await apiService.socialSearch(
  'data breach',
  ['facebook.com', 'x.com', 'linkedin.com'],
  15  // 15 results per site
);

console.log(`Found ${results.total_results} results`);
results.results.forEach(result => {
  console.log(`${result.title} - ${result.link}`);
});
```

**Backend API Call:**

```bash
curl -X POST http://localhost:8000/api/v1/social-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cybersecurity breach 2025",
    "sites": ["facebook.com", "x.com"],
    "results_per_site": 10
  }'
```

## Current Limitations

### Google Custom Search API Quotas (Free Tier)
- **100 queries per day** (free tier)
- **10 results per query** (maximum)
- To get more results, the service makes multiple paginated requests

### Implementation Status
✅ Backend API endpoint created  
✅ Frontend checkbox added  
✅ Social search API called when enabled  
⚠️ Results logged to console (not displayed in UI yet)  

## Future Enhancements

### 1. Display Social Results in UI
Create a separate section or tab to display social media results:
```tsx
<SocialResultsPanel results={socialSearchResults} />
```

### 2. Merge Social Results with Regular Events
Process social results through the same event extraction pipeline to extract structured event data.

### 3. Filter by Platform
Add dropdown to select specific platforms:
- Facebook only
- Twitter/X only
- LinkedIn
- Instagram
- All platforms

### 4. Date Range Filtering
Apply date filters to social search results (requires additional CSE configuration).

### 5. Result Caching
Cache social search results to avoid hitting API quotas unnecessarily.

### 6. Upgrade to Paid Plan
For production use with high volume:
- Paid plan: $5 per 1,000 queries
- Up to 10,000 queries per day

## Troubleshooting

### "Social search failed" in console

**Check:**
1. API key is correct in `.env`
2. Search Engine ID is correct in `.env`
3. Custom Search API is enabled in Google Cloud Console
4. You haven't exceeded daily quota (100 queries/day for free tier)

**Debug:**
```bash
# Check backend logs
cd backend
tail -f logs/app.log
```

### No results returned

**Possible causes:**
1. Search query too specific - try broader terms
2. Sites not properly configured in Google CSE
3. Social media platforms blocking CSE crawler

**Solution:**
- Verify sites in Google CSE dashboard: https://cse.google.com
- Ensure patterns are: `www.facebook.com/*` and `www.x.com/*`

### Rate limit errors

**Error:** `429 Too Many Requests`

**Solution:**
- Free tier: 100 queries/day
- Wait 24 hours for quota reset
- Or upgrade to paid plan

## Testing

### Manual Testing

1. **With Social Search Enabled:**
   - Check the checkbox
   - Search for "protest"
   - Open browser console (F12)
   - Look for "Social search results:" log
   - Verify results contain Facebook/Twitter links

2. **With Social Search Disabled:**
   - Uncheck the checkbox
   - Search for "protest"
   - Verify no social search API call is made
   - Regular search still works

### API Testing

```bash
# Test social search endpoint
curl -X POST http://localhost:8000/api/v1/social-search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "results_per_site": 5}'

# Expected response
{
  "status": "success",
  "query": "test",
  "sites": ["facebook.com", "x.com"],
  "total_results": 10,
  "results": [...]
}
```

## API Costs & Quotas

### Free Tier
- **100 queries/day**
- **$0** cost
- Good for: Testing, low-volume personal use

### Paid Tier
- **$5 per 1,000 queries**
- **Up to 10,000 queries/day**
- Good for: Production, enterprise use

### Cost Calculator
- 1 search = 2 queries (Facebook + Twitter)
- 100 free queries = **50 searches/day**
- For 500 searches/day: **1,000 queries = $5/month**

## Files Changed

### Backend
- ✅ `backend/app/services/social_search_service.py` (new)
- ✅ `backend/app/settings.py` (updated)
- ✅ `backend/app/main.py` (updated - added endpoint)
- ✅ `backend/.env` (updated)
- ✅ `backend/.env.example` (updated)

### Frontend
- ✅ `frontend/src/types/events.ts` (updated)
- ✅ `frontend/src/components/SearchForm.tsx` (updated)
- ✅ `frontend/src/services/api.ts` (updated)

### Documentation
- ✅ `doc/SOCIAL_SEARCH_FEATURE.md` (new - this file)

## Summary

The Social Media Search feature is now **implemented and functional**. Users can:
- ✅ Enable/disable via checkbox (default: enabled)
- ✅ Search Facebook and Twitter/X via Google CSE
- ✅ Results are fetched and logged to console

**Next Steps:**
1. Add your actual Google Search Engine ID to `.env`
2. Implement UI to display social results (optional)
3. Consider merging social results with event extraction pipeline

## Questions?

If you need any clarification or additional features:
1. Check backend logs: `backend/logs/app.log`
2. Check browser console: F12 → Console tab
3. Review this documentation
4. Test API endpoint directly with curl
