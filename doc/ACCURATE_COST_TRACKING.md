# Accurate API Cost Tracking - Cache-Aware Implementation

## Problem Statement
API costs were being tracked incorrectly:
1. **Scraping costs** were tracked even when content was served from cache
2. **Analysis costs** were tracked even when results were served from cache
3. Costs were not differentiated by API provider (scrapecreators vs Google CSE vs internal)

This led to inflated cost reports that didn't reflect actual API usage.

## Solution Overview

### Key Principle
**Only track API costs when actual external API calls are made, not when serving from cache.**

## Detailed Implementation

### 1. Scraping Cost Tracking (`/api/v1/social-content/fetch`)

#### Previous Implementation (Incorrect)
```python
# OLD - Tracked cost BEFORE checking cache
db_service.log_api_usage(
    api_type='scraping',
    cost_usd=0.001  # Always charged
)
content = await fetch_content(url)  # Might return from cache
```

**Problem:** Cost was tracked even if content came from cache (no actual API call).

#### New Implementation (Correct)
```python
# Fetch content first
content = await fetch_content(url)  # May return from cache

# Check if from cache
from_cache = content.cached if hasattr(content, 'cached') else False

# Only track cost if NOT from cache (actual API was called)
if not from_cache:
    # Determine API provider based on platform
    if platform in ['twitter', 'facebook', 'instagram']:
        api_provider = 'scrapecreators'  # api.scrapecreators.com
        cost = 0.001  # $0.001 per scrape
    elif platform == 'youtube':
        api_provider = 'google_cse'  # Google CSE API
        cost = 0.0005  # $0.0005 per fetch
    else:
        api_provider = 'internal'  # Google search scraping
        cost = 0.0  # Free
    
    db_service.log_api_usage(
        api_type='scraping',
        api_provider=api_provider,
        cost_usd=cost
    )
```

**Benefits:**
- ✅ Only tracks cost for actual API calls
- ✅ Differentiates between API providers
- ✅ Free for cached content
- ✅ Free for Google search scraping

### 2. Analysis Cost Tracking (`/api/v1/social-content/analyse`)

#### Previous Implementation (Already Correct)
The analysis endpoint was already correctly implemented - it returns early if cached:

```python
# Check cache first
cached_event = get_cached_analysis(url, llm_model)
if cached_event:
    return AnalyseContentResponse(
        event=cached_event,
        llm_model_used="cached"  # Indicates cache hit
    )  # Returns early - no cost tracking reached

# Only reaches here if not cached
event = await extract_event(content)  # Actual LLM API call

# Track cost ONLY when LLM API was actually called
db_service.log_api_usage(
    api_type='analysis',
    api_provider=provider,  # 'claude' or 'ollama'
    tokens_used=tokens,
    cost_usd=cost  # Actual cost from LLM API
)
```

**Benefits:**
- ✅ Already cache-aware (returns before tracking)
- ✅ Tracks actual tokens used
- ✅ Tracks actual cost from Claude API
- ✅ Zero cost for Ollama (local)
- ✅ Zero cost for cached analyses

### 3. Search Cost Tracking (`/api/v1/social-search`)

Search results are not cached, so cost is always tracked:

```python
# Loop through each platform
for site in sites:
    platform = normalize_platform(site)
    
    db_service.log_api_usage(
        api_type='search',
        api_provider='google_cse',
        platform=platform,
        cost_usd=0.005  # $0.005 per platform search
    )
```

**Note:** Search results are real-time and not cached, so every search incurs API cost.

## Cost Structure

### API Provider Costs

| API Provider      | Used For                          | Cost          |
|-------------------|-----------------------------------|---------------|
| google_cse        | Social search, YouTube scraping   | $0.005/search, $0.0005/scrape |
| scrapecreators    | Twitter, Facebook, Instagram      | $0.001/scrape |
| internal          | Google search scraping            | $0 (free)     |
| claude            | Content analysis (LLM)            | $0.001-$0.005 (varies by tokens) |
| ollama            | Content analysis (local LLM)      | $0 (free)     |

### Action Costs

| User Action                          | API Type   | API Called                     | Cost          | Cached? |
|--------------------------------------|------------|--------------------------------|---------------|---------|
| Social search (per platform)         | search     | Google CSE                     | $0.005        | No      |
| View Twitter/FB/IG details (1st time)| scraping   | api.scrapecreators.com         | $0.001        | No      |
| View Twitter/FB/IG details (cached)  | scraping   | (cache)                        | $0.000        | Yes     |
| View YouTube details (1st time)      | scraping   | Google CSE API                 | $0.0005       | No      |
| View YouTube details (cached)        | scraping   | (cache)                        | $0.000        | Yes     |
| View Google result details           | scraping   | Internal scraper               | $0.000        | No      |
| Analyze with Claude (1st time)       | analysis   | Claude API                     | $0.001-$0.005 | No      |
| Analyze with Claude (cached)         | analysis   | (cache)                        | $0.000        | Yes     |
| Analyze with Ollama                  | analysis   | Local Ollama                   | $0.000        | No      |

## Cache Behavior

### Content Cache (Scraping)
- **Duration:** 24 hours (configurable)
- **Key:** URL + platform
- **Behavior:** First view fetches from API, subsequent views within 24h use cache

**Example:**
```
10:00 AM - User views Twitter post → API call → $0.001 cost
10:05 AM - Same user views same post → Cache hit → $0 cost
10:30 AM - Different user views same post → Cache hit → $0 cost
Tomorrow 10:01 AM - User views same post → Cache expired → API call → $0.001 cost
```

### Analysis Cache (LLM)
- **Duration:** Indefinite (until cache clear)
- **Key:** URL + LLM model
- **Behavior:** First analysis calls LLM, subsequent analyses use cached result

**Example:**
```
User analyzes YouTube video with Claude:
1st time → Claude API call → $0.003 cost
2nd time → Cache hit → $0 cost
3rd time → Cache hit → $0 cost
```

## Usage Report Enhancement

### Added Cost Calculation Note

The frontend now displays a comprehensive note explaining how costs are calculated:

```
💡 How Daily Cost is Calculated

• Searches: $0.005 per platform searched (Google CSE API)

• Scrapings: Cost only when fetching new content (not from cache):
  - Twitter, Facebook, Instagram: $0.001 per fetch (api.scrapecreators.com)
  - YouTube: $0.0005 per fetch (Google CSE API)
  - Google search results: $0 (free internal scraping)

• Analyses: Cost only when calling LLM API (not from cache):
  - Claude API: $0.001-$0.005 per analysis (varies by tokens used)
  - Ollama (local): $0 (free)

Note: Cached content and cached analyses are served at zero cost.
Only actual API calls are tracked.
```

**Location:** Admin Dashboard → Usage Reports → Below monthly summary

## Testing Scenarios

### Scenario 1: Fresh Content Fetch (Twitter)

**Actions:**
1. Search Twitter for "breaking news"
2. Click "View Details" on a tweet (first time)

**Expected Database Records:**
```sql
-- Search
INSERT INTO user_api_usage (api_type, api_provider, platform, cost_usd)
VALUES ('search', 'google_cse', 'twitter', 0.005);

-- Scraping (first time)
INSERT INTO user_api_usage (api_type, api_provider, platform, cost_usd)
VALUES ('scraping', 'scrapecreators', 'twitter', 0.001);
```

**Total Cost:** $0.006

### Scenario 2: Cached Content Fetch (Twitter)

**Actions:**
1. Click "View Details" on the same tweet again (within 24 hours)

**Expected Database Records:**
```sql
-- No new records - content served from cache
```

**Total Cost:** $0.000

**Backend Logs:**
```
✅ Content from cache - No API cost tracked
```

### Scenario 3: Fresh Analysis (Claude)

**Actions:**
1. View content details
2. Click "Analyze" (first time for this content)

**Expected Database Records:**
```sql
-- Analysis (first time)
INSERT INTO user_api_usage (api_type, api_provider, tokens_used, cost_usd)
VALUES ('analysis', 'claude', 2500, 0.003);
```

**Total Cost:** $0.003

**Backend Logs:**
```
💰 Tracked analysis cost: $0.003 (claude, 2500 tokens) - NOT from cache
```

### Scenario 4: Cached Analysis (Claude)

**Actions:**
1. Click "Analyze" on the same content again

**Expected Database Records:**
```sql
-- No new records - analysis served from cache
```

**Total Cost:** $0.000

**Backend Logs:**
```
✅ Returning cached analysis for: <url> - No API cost
```

### Scenario 5: Complete Workflow

**Actions:**
1. Search 5 platforms (YouTube, Twitter, Facebook, Instagram, Google)
2. View 3 Twitter posts (2 new, 1 cached)
3. View 2 YouTube videos (both new)
4. Analyze 2 posts with Claude (1 new, 1 cached)

**Expected Costs:**
```
Searches: 5 platforms × $0.005 = $0.025
Scrapings:
  - 2 Twitter (new) × $0.001 = $0.002
  - 1 Twitter (cached) × $0 = $0.000
  - 2 YouTube (new) × $0.0005 = $0.001
Analyses:
  - 1 Claude (new) × $0.003 = $0.003
  - 1 Claude (cached) × $0 = $0.000
  
Total: $0.025 + $0.003 + $0.003 = $0.031
```

**Usage Report:**
```
Date       | YouTube | Twitter | ... | Scrapings | Analyses | Daily Cost
-----------|---------|---------|-----|-----------|----------|------------
2/8/2026   |    1    |    1    | ... |     4     |    1     | $0.031
```

Note: Scrapings = 4 (2 Twitter + 2 YouTube, cached doesn't count)
      Analyses = 1 (only the non-cached one)

## Verification Commands

### Check Recent Scraping Records
```bash
docker exec socialSearcher_db psql -U dbuser -d socialsearcher -c "
SELECT 
    id, user_id, api_type, api_provider, platform, 
    api_calls, cost_usd, request_timestamp 
FROM user_api_usage 
WHERE api_type = 'scraping' 
ORDER BY request_timestamp DESC 
LIMIT 10;
"
```

### Check Recent Analysis Records
```bash
docker exec socialSearcher_db psql -U dbuser -d socialsearcher -c "
SELECT 
    id, user_id, api_type, api_provider, platform,
    tokens_used, cost_usd, request_timestamp 
FROM user_api_usage 
WHERE api_type = 'analysis' 
ORDER BY request_timestamp DESC 
LIMIT 10;
"
```

### Check Total Costs by Type
```bash
docker exec socialSearcher_db psql -U dbuser -d socialsearcher -c "
SELECT 
    api_type,
    api_provider,
    COUNT(*) as call_count,
    SUM(cost_usd) as total_cost
FROM user_api_usage
WHERE DATE(request_timestamp) = CURRENT_DATE
GROUP BY api_type, api_provider
ORDER BY total_cost DESC;
"
```

## Backend Logging

Enhanced logging helps track cache hits vs API calls:

### Scraping Logs
```
# Cache hit
✅ Content from cache - No API cost tracked

# API call
💰 Tracked scraping cost: $0.001 (scrapecreators) - NOT from cache
```

### Analysis Logs
```
# Cache hit
✅ Returning cached analysis for: <url> - No API cost

# API call
💰 Tracked analysis cost: $0.003 (claude, 2500 tokens) - NOT from cache
```

## Files Changed

### Backend
1. **`backend/app/main.py`**
   - `fetch_social_content()`: Moved cost tracking AFTER fetch, added cache check
   - `analyse_social_content()`: Added logging for cache awareness
   - Differentiated API providers (scrapecreators, google_cse, internal)
   - Platform-specific cost calculations

### Frontend
2. **`frontend/src/components/AdminDashboard.tsx`**
   - Added comprehensive cost calculation note
   - Explains cache behavior
   - Shows cost breakdown by API provider

## Deployment Status

✅ Backend scraping cost tracking fixed (cache-aware)  
✅ Backend analysis cost tracking verified (already cache-aware)  
✅ API provider differentiation implemented  
✅ Platform-specific costs configured  
✅ Frontend cost explanation added  
✅ Backend restarted  
✅ Frontend rebuilt and redeployed  
✅ All containers healthy  

## Summary

**Problem:** API costs were tracked even when content/analysis was served from cache, leading to inflated cost reports.

**Solution:**
1. **Scraping:** Check if content is from cache BEFORE tracking cost
2. **Analysis:** Already cache-aware (returns early for cached results)
3. **Differentiate:** Track different costs for different API providers
4. **Document:** Added clear explanation in usage report UI

**Result:** Accurate cost tracking that reflects only actual external API usage.

**Key Innovation:** Cache-aware cost tracking ensures users only pay for actual API calls, not for serving cached data.
