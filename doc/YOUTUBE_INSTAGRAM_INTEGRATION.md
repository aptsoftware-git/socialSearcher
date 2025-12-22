# YouTube and Instagram Integration

**Date:** 2025-01-XX  
**Status:** ✅ Complete  
**Type:** Feature Enhancement

---

## Overview

Extended the social media search functionality to include **YouTube** and **Instagram** in addition to the existing Facebook and Twitter/X support. This provides comprehensive coverage of major social media platforms.

---

## Changes Summary

### Backend Updates

#### 1. **social_search_service.py**
- Updated default sites list from 2 to 4 platforms
- **Old:** `['facebook.com', 'x.com']`
- **New:** `['facebook.com', 'x.com', 'youtube.com', 'instagram.com']`

### Frontend Updates

#### 1. **SocialResultsPanel.tsx**

**Imports:**
- Added `YouTube as YouTubeIcon` from `@mui/icons-material`
- Added `Instagram as InstagramIcon` from `@mui/icons-material`

**Platform Filtering:**
```typescript
// Added new result filters
const youtubeResults = results.filter(r => 
  r.source_site.includes('youtube')
);
const instagramResults = results.filter(r => 
  r.source_site.includes('instagram')
);

// Updated otherResults to exclude new platforms
const otherResults = results.filter(r => 
  !r.source_site.includes('facebook') && 
  !r.source_site.includes('twitter') && 
  !r.source_site.includes('x.com') &&
  !r.source_site.includes('youtube') &&
  !r.source_site.includes('instagram')
);
```

**Icon Function:**
```typescript
const getSiteIcon = (site: string) => {
  if (site.includes('facebook')) {
    return <FacebookIcon sx={{ fontSize: 20 }} />;
  } else if (site.includes('twitter') || site.includes('x.com')) {
    return <TwitterIcon sx={{ fontSize: 20 }} />;
  } else if (site.includes('youtube')) {
    return <YouTubeIcon sx={{ fontSize: 20 }} />;
  } else if (site.includes('instagram')) {
    return <InstagramIcon sx={{ fontSize: 20 }} />;
  }
  return <WebIcon sx={{ fontSize: 20 }} />;
};
```

**Color Function:**
```typescript
const getSiteColor = (site: string): "primary" | "info" | "error" | "warning" | "default" => {
  if (site.includes('facebook')) return 'primary';      // Blue
  if (site.includes('twitter') || site.includes('x.com')) return 'info';  // Light Blue
  if (site.includes('youtube')) return 'error';         // Red
  if (site.includes('instagram')) return 'warning';     // Orange/Yellow
  return 'default';
};
```

**Summary Text:**
Updated to show counts for all 4 platforms:
```
Found X results for "query" (Y Facebook, Z Twitter/X, A YouTube, B Instagram)
```

**Tabs:**
- Changed from `variant="fullWidth"` to `variant="scrollable"` for better mobile support
- Added YouTube tab (index 2) with red badge
- Added Instagram tab (index 3) with orange/yellow badge
- Updated "Other" tab to index 4

**Tab Panels:**
- Added YouTube TabPanel at index 2
- Added Instagram TabPanel at index 3
- Updated Other TabPanel to index 4

#### 2. **SearchForm.tsx**
- Updated checkbox label from:
  - "Use Social Media Search ONLY (Facebook, Twitter/X) - Testing Mode"
  - To: "Use Social Media Search ONLY (Facebook, Twitter/X, YouTube, Instagram) - Testing Mode"

---

## Platform Details

| Platform | Icon | Badge Color | Site Pattern |
|----------|------|-------------|--------------|
| Facebook | FacebookIcon | primary (blue) | `facebook.com` |
| Twitter/X | TwitterIcon | info (light blue) | `twitter.com`, `x.com` |
| YouTube | YouTubeIcon | error (red) | `youtube.com` |
| Instagram | InstagramIcon | warning (orange) | `instagram.com` |

---

## User Interface

### Tabs Layout
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Social Media Search Results                               │
│ Found 24 results (6 Facebook, 8 Twitter/X, 5 YouTube, 5 Ins) │
├─────────────────────────────────────────────────────────────┤
│ [Facebook (6)] [Twitter/X (8)] [YouTube (5)] [Instagram (5)] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Result Card with Image]                                    │
│  [Result Card]                                               │
│  [Result Card with Image]                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Features per Tab
- Badge showing result count
- Platform-specific icon with color coding
- Numbered results (Result #1 of 5)
- Image display when available
- Source site chip with icon
- Title with external link icon
- Snippet preview (max 3 lines)
- Full URL display

---

## Testing

### To Test:
1. Ensure Google Custom Search Engine is configured with all 4 sites:
   - `www.facebook.com/*`
   - `www.x.com/*` or `www.twitter.com/*`
   - `www.youtube.com/*`
   - `www.instagram.com/*`

2. Start the backend:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload
   ```

3. Start the frontend:
   ```powershell
   cd frontend
   npm run dev
   ```

4. Test queries that should return results from all platforms

5. Verify:
   - ✅ All 4 tabs appear
   - ✅ Badge counts are correct
   - ✅ Icons display properly
   - ✅ Colors match platform branding
   - ✅ Results filter correctly by platform
   - ✅ Images load when available
   - ✅ Tabs are scrollable on mobile

---

## Configuration

### Google Custom Search Engine Setup

1. Go to https://programmablesearchengine.google.com/
2. Edit your search engine
3. Under "Sites to search", ensure you have:
   ```
   www.facebook.com/*
   www.x.com/*
   www.youtube.com/*
   www.instagram.com/*
   ```
4. Save changes

### Backend Configuration (.env)
```env
GOOGLE_CSE_API_KEY=AIzaSyCr0h6TbSn-LbLje1cUEj9es7fQdZekOhY
GOOGLE_CSE_ID=your_search_engine_id
```

---

## API Impact

### Request (unchanged)
```json
POST /api/v1/social-search
{
  "query": "breaking news",
  "sites": ["facebook.com", "x.com", "youtube.com", "instagram.com"],
  "results_per_site": 10
}
```

### Response (structure unchanged, more diverse sources)
```json
{
  "status": "success",
  "query": "breaking news",
  "sites": ["facebook.com", "x.com", "youtube.com", "instagram.com"],
  "total_results": 24,
  "results": [
    {
      "title": "Breaking News Coverage",
      "link": "https://youtube.com/watch?v=...",
      "snippet": "...",
      "display_link": "www.youtube.com",
      "formatted_url": "https://www.youtube.com/...",
      "source_site": "youtube.com",
      "pagemap": {...}
    }
  ]
}
```

---

## Known Limitations

1. **Google CSE Free Tier:** 100 queries per day limit
2. **Results per Platform:** Max 10 results per site per query
3. **Image Availability:** Not all social media posts have images accessible via CSE
4. **Instagram Limitations:** Instagram results may be limited due to platform's privacy settings
5. **YouTube Results:** Typically return video pages, not individual posts

---

## Future Enhancements

- [ ] Add LinkedIn support
- [ ] Add TikTok support
- [ ] Add Reddit support
- [ ] Implement platform-specific result cards (e.g., YouTube video preview)
- [ ] Add filter options (date range, content type)
- [ ] Cache results to reduce API calls
- [ ] Add export functionality (CSV, JSON)

---

## Files Modified

### Backend
- `backend/app/services/social_search_service.py`

### Frontend
- `frontend/src/components/SocialResultsPanel.tsx`
- `frontend/src/components/SearchForm.tsx`

### Documentation
- `doc/YOUTUBE_INSTAGRAM_INTEGRATION.md` (this file)

---

## Related Documentation

- [Social Search API](API.md#social-search-endpoint)
- [Configuration Guide](CONFIGURATION.md#google-custom-search)
- [Developer Guide](DEVELOPER_GUIDE.md)

---

## Summary

✅ **Backend:** Default sites list updated to include YouTube and Instagram  
✅ **Frontend:** UI updated with 4 tabs, icons, colors, and filtering  
✅ **User Experience:** Comprehensive social media coverage with clear platform separation  
✅ **Responsive Design:** Scrollable tabs for mobile devices  
✅ **Testing:** No errors found in TypeScript compilation  

The social media search feature now supports **4 major platforms** with a polished, tabbed interface that makes it easy to explore results by platform.
