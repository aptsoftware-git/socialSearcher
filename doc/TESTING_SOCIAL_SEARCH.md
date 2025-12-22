# Testing Social Search - Updated Behavior

## 🎯 New Behavior (Testing Mode)

The frontend has been updated so that when the **Social Search checkbox is enabled**, it will:

1. ✅ **ONLY** call the social search API
2. ❌ **SKIP** the regular streaming search completely
3. ✅ Display results count and completion message
4. ✅ Log detailed results to browser console

This allows you to test the social search functionality in isolation.

## 📝 Changes Made

### Frontend Updates

**File**: `frontend/src/components/SearchForm.tsx`

**Changes:**
1. When checkbox is **checked**: 
   - Calls social search API
   - Shows results in console with detailed logging
   - Displays completion message
   - **Returns early** (skips regular search)

2. When checkbox is **unchecked**:
   - Runs regular streaming search only
   - Normal behavior (unchanged)

**Checkbox label updated to:**
> "Use Social Media Search ONLY (Facebook, Twitter/X) - Testing Mode"

**Helper text:**
> "When checked: Uses ONLY Google Custom Search (regular search is disabled for testing)"

**Warning message:**
> "⚠️ Testing Mode: Regular streaming search will be skipped when this is enabled"

## 🧪 How to Test

### Step 1: Start Backend (if not running)

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Start Frontend (if not running)

```powershell
cd frontend
npm run dev
```

### Step 3: Test Social Search ONLY

1. Open http://localhost:5173
2. **Ensure checkbox is CHECKED**: "Use Social Media Search ONLY..."
3. Enter a search query (e.g., "cybersecurity")
4. Click "Search"
5. Open browser console (F12 → Console tab)

**Expected Console Output:**
```
🔍 Starting social search for: cybersecurity
✅ Social search completed!
📊 Total results: 20
🌐 Sites searched: facebook.com, x.com
📝 Results: [Array of results]
```

**Expected UI Message:**
```
✅ Social search completed. Found 20 results from facebook.com, x.com
```

**Expected Behavior:**
- No streaming search starts
- No progress bar appears
- Only social search API is called
- Results logged to console

### Step 4: Test Regular Search ONLY

1. **UNCHECK** the checkbox
2. Enter a search query
3. Click "Search"

**Expected Behavior:**
- Regular streaming search starts
- Progress bar appears
- Events displayed as usual
- Social search API is NOT called

## 📊 Console Logging

When social search runs, you'll see detailed console logs:

```javascript
🔍 Starting social search for: your_query
✅ Social search completed!
📊 Total results: 20
🌐 Sites searched: ["facebook.com", "x.com"]
📝 Results: [
  {
    title: "...",
    link: "https://facebook.com/...",
    snippet: "...",
    source_site: "facebook.com",
    display_link: "facebook.com",
    formatted_url: "https://..."
  },
  // ... more results
]
```

## 🔧 API Call Details

**Endpoint Called:** `POST /api/v1/social-search`

**Request:**
```json
{
  "query": "your_search_query",
  "sites": null,
  "results_per_site": 10
}
```

**Response:**
```json
{
  "status": "success",
  "query": "your_search_query",
  "sites": ["facebook.com", "x.com"],
  "total_results": 20,
  "results": [...]
}
```

## ⚠️ Troubleshooting

### "Social search failed" Error

**Possible causes:**
1. Backend not running
2. Google CSE ID not configured in `.env`
3. API key invalid
4. Daily quota exceeded (100 queries/day)

**Check:**
```bash
# Check backend .env file
cat backend/.env | grep GOOGLE_CSE

# Should show:
GOOGLE_CSE_API_KEY=your_actual_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
```

### Backend Not Responding

**Check backend logs:**
```powershell
cd backend
tail -f logs/app.log
```

**Or check terminal output where backend is running**

### CORS Errors

If you see CORS errors in browser console:
1. Check backend CORS configuration in `.env`
2. Ensure frontend URL is in `CORS_ORIGINS`
3. Restart backend after changing `.env`

## 🎯 Testing Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Google CSE ID added to `backend/.env`
- [ ] Backend restarted after adding CSE ID
- [ ] Checkbox shows "Testing Mode" warning
- [ ] With checkbox CHECKED: Only social search runs
- [ ] With checkbox UNCHECKED: Only regular search runs
- [ ] Console shows detailed social search logs
- [ ] Completion message appears in UI
- [ ] No errors in browser console
- [ ] No errors in backend logs

## 📝 Next Steps After Testing

Once you've confirmed social search works:

1. **Option A:** Keep testing mode as-is
   - Users choose between social OR regular search

2. **Option B:** Merge both searches
   - Update code to run both searches together
   - Display results from both sources
   - Combine into unified event list

3. **Option C:** Add UI for social results
   - Create SocialResultsPanel component
   - Display social results separately
   - Add filtering and sorting

## 🚀 Quick Test Commands

### Test Backend API Directly

```bash
curl -X POST http://localhost:8000/api/v1/social-search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "results_per_site": 5}'
```

### Check Backend Health

```bash
curl http://localhost:8000/api/v1/health
```

### Check Backend Logs

```powershell
cd backend
Get-Content logs/app.log -Tail 50
```

## ✅ Summary

**Current Behavior:**
- Checkbox CHECKED = Social search ONLY (for testing)
- Checkbox UNCHECKED = Regular search ONLY

**Console Output:** Detailed logs with emojis for easy identification

**UI Message:** Shows total results and sites searched

**Error Handling:** Clear error messages if social search fails

**Ready to test!** Just ensure your Google CSE ID is in the `.env` file and backend is restarted.
