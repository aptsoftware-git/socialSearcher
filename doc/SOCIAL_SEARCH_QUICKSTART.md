# Social Media Search Integration - Quick Start

## ⚡ Quick Setup (5 minutes)

### 1. Get Your Google Custom Search Engine ID

You already have the API key: `AIzaSyCr0h6TbSn-LbLje1cUEj9es7fQdZekOhY`

Now get your Search Engine ID:
1. Go to https://cse.google.com
2. Find your search engine (with Facebook and Twitter configured)
3. Click on it
4. Look for the **Search engine ID** (starts with a letter, contains numbers and colons)
5. Copy that ID

### 2. Update Backend Configuration

Edit `backend/.env` and add your Search Engine ID:

```bash
# ===== Google Custom Search Engine (Social Media Search) =====
GOOGLE_CSE_API_KEY="Your_Google_CSE_API_Key_Here"        # <- Replace this!
GOOGLE_CSE_ID="Your_Google_CSE_ID_Here"    # <- Replace this!
```

### 3. Restart Backend

```powershell
cd backend
# Stop the current backend (Ctrl+C)
# Start it again
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Test It!

1. Open the frontend: http://localhost:5173
2. You'll see a new checkbox: **"Include Social Media Search (Facebook, Twitter/X)"** ✓ (checked by default)
3. Enter a search query and click "Search"
4. Open browser console (F12) to see social search results

## 🎯 How It Works

**When checkbox is CHECKED (default):**
- Frontend calls social search API first
- Gets results from Facebook and Twitter/X
- Then proceeds with regular search
- Results logged to console (you can implement UI display later)

**When checkbox is UNCHECKED:**
- Only regular search (existing functionality)
- No social media search

## 📊 Current Status

| Feature | Status |
|---------|--------|
| Backend API endpoint | ✅ Complete |
| Frontend checkbox | ✅ Complete |
| API integration | ✅ Complete |
| Social results in console | ✅ Working |
| Social results in UI | ⚠️ To be implemented |

## 🔧 API Details

**Endpoint:** `POST /api/v1/social-search`

**Request:**
```json
{
  "query": "cybersecurity breach",
  "sites": ["facebook.com", "x.com"],
  "results_per_site": 10
}
```

**Response:**
```json
{
  "status": "success",
  "query": "cybersecurity breach",
  "total_results": 20,
  "results": [
    {
      "title": "...",
      "link": "https://...",
      "snippet": "...",
      "source_site": "facebook.com"
    }
  ]
}
```

## 📝 Notes

1. **Free tier quota:** 100 queries/day (50 searches with 2 sites)
2. **Default sites:** Facebook and Twitter/X
3. **Results per site:** 10 (configurable)
4. **Currently:** Results are logged to console, not displayed in UI yet

## 🚀 Next Steps (Optional)

If you want to display social results in the UI:

1. Create a `SocialResultsPanel` component
2. Store social results in state
3. Display them in a separate section or tab
4. Style them differently from regular events

## 📚 Full Documentation

See `doc/SOCIAL_SEARCH_FEATURE.md` for complete documentation including:
- Detailed implementation
- API reference
- Troubleshooting
- Future enhancements
- Cost calculator

## ❓ Testing

### Quick Test:

1. **Backend test:**
```bash
curl -X POST http://localhost:8000/api/v1/social-search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "results_per_site": 5}'
```

2. **Frontend test:**
   - Go to http://localhost:5173
   - Search for anything with checkbox checked
   - Open console (F12) → Look for "Social search results:"

### Expected Console Output:
```
Social search results: {
  status: "success",
  total_results: 20,
  results: [...]
}
```

## ⚠️ Important

**Don't forget to:**
1. ✅ Add your actual Search Engine ID to `backend/.env`
2. ✅ Restart the backend after updating `.env`
3. ✅ Verify sites are configured in your Google CSE (facebook.com, x.com)

## 🎉 That's It!

The feature is ready to use. Just add your Search Engine ID and restart the backend!
