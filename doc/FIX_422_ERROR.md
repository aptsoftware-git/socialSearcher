# Fix for 422 Error - Backend Updated

## ❌ Problem

Backend returned `422 Unprocessable Entity` when frontend called `/api/v1/social-search`

**Root Cause:** The endpoint was expecting query parameters, but frontend was sending JSON body.

## ✅ Solution Applied

### 1. Added Pydantic Models

**File:** `backend/app/models.py`

Added new models:
```python
class SocialSearchRequest(BaseModel):
    query: str
    sites: Optional[List[str]] = None
    results_per_site: int = 10

class SocialSearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    display_link: str
    formatted_url: str
    source_site: str
    pagemap: Optional[Dict[str, Any]] = None

class SocialSearchResponse(BaseModel):
    status: str
    query: str
    sites: List[str]
    total_results: int
    results: List[SocialSearchResult]
```

### 2. Updated API Endpoint

**File:** `backend/app/main.py`

**Before:**
```python
@app.post("/api/v1/social-search")
async def social_search(
    query: str,
    sites: List[str] = None,
    results_per_site: int = 10
):
```

**After:**
```python
@app.post("/api/v1/social-search", response_model=SocialSearchResponse)
async def social_search(request: SocialSearchRequest):
```

Now the endpoint:
- ✅ Accepts JSON body (not query parameters)
- ✅ Uses Pydantic model for validation
- ✅ Returns properly typed response
- ✅ Matches frontend's API call

### 3. Updated Imports

Added to `main.py` imports:
```python
from app.models import (
    # ... existing imports
    SocialSearchRequest,
    SocialSearchResponse
)
```

## 🔄 Action Required

**You MUST restart the backend** for changes to take effect:

```powershell
# In the backend terminal, press Ctrl+C to stop
# Then restart:
cd C:\Anu\APT\apt\defender\scraping\socialSearcher\backend
python -m uvicorn app.main:app --reload --port 8000
```

## 🧪 Test After Restart

### Option 1: Test with Python Script

```powershell
cd backend
python test_social_search.py
```

### Option 2: Test with curl

```bash
curl -X POST http://localhost:8000/api/v1/social-search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "results_per_site": 5}'
```

### Option 3: Test from Frontend

1. Open http://localhost:5173
2. Enter a search query
3. Ensure checkbox is checked
4. Click "Search"
5. Check browser console (F12)

## ✅ Expected Behavior After Restart

**Request from frontend:**
```json
{
  "query": "cybersecurity breach",
  "sites": null,
  "results_per_site": 10
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "query": "cybersecurity breach",
  "sites": ["facebook.com", "x.com"],
  "total_results": 20,
  "results": [
    {
      "title": "...",
      "link": "https://...",
      "snippet": "...",
      "display_link": "facebook.com",
      "formatted_url": "https://...",
      "source_site": "facebook.com"
    }
  ]
}
```

## 📝 Summary of Changes

| File | Change | Status |
|------|--------|--------|
| `backend/app/models.py` | Added 3 new models | ✅ Complete |
| `backend/app/main.py` | Updated endpoint signature | ✅ Complete |
| `backend/app/main.py` | Updated imports | ✅ Complete |
| `backend/test_social_search.py` | Created test script | ✅ Complete |

## ⚠️ Important

**The 422 error will persist until you restart the backend!**

After restart:
- ✅ Endpoint accepts JSON body
- ✅ Proper validation with Pydantic
- ✅ Type-safe response
- ✅ No more 422 errors

## 🎯 Next Steps

1. **Stop backend** (Ctrl+C in terminal)
2. **Restart backend**
3. **Test** using one of the methods above
4. **Verify** no 422 errors in logs
5. **Test from frontend** - should work now!
