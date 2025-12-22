# Facebook Image Missing - Action Plan

**Date:** December 22, 2025  
**Status:** 🔍 Backend & Frontend Logging Enhanced  
**Key Finding:** Google CSE web interface SHOWS images for Facebook, but your app doesn't

---

## The Situation

✅ **Google CSE Web Interface** (https://cse.google.com/cse?cx=30671ef5d35724992)  
   → Shows Facebook images

❌ **Your Application**  
   → Facebook images missing  
   → YouTube, Instagram, Twitter images working

✅ **Same API Key Used**  
   → Same search engine ID  
   → Same query

**Conclusion:** The data IS available from Google, but we're not extracting it correctly!

---

## What I've Added

### Backend Logging (social_search_service.py)
Added detailed logging for Facebook results:
```python
logger.info(f"=== FACEBOOK ITEM FROM GOOGLE CSE ===")
logger.info(f"Title: ...")
logger.info(f"Link: ...")
logger.info(f"Pagemap keys: ...")
logger.info(f"Full pagemap: {json.dumps(pagemap, indent=2)}")
```

### Frontend Logging (SocialResultsPanel.tsx)
Added detailed console logging:
```typescript
console.log('=== FACEBOOK RESULT ===')
console.log('Pagemap keys:', Object.keys(result.pagemap))
console.log('Full pagemap:', JSON.stringify(result.pagemap, null, 2))
```

---

## Testing Steps

### Step 1: Open Backend Terminal
Look at the terminal where backend is running (should show startup logs)

### Step 2: Open Browser Console
1. Press **F12**
2. Go to **Console** tab
3. Clear console (trash icon)

### Step 3: Perform a Search
1. Go to: http://localhost:5173
2. Check "Use Social Media Search ONLY..."
3. Search for: **"Tejas crash Dubai"** (or any term that returns Facebook results)
4. Click **Search**

### Step 4: Check Backend Logs
In the backend terminal, look for:
```
=== FACEBOOK ITEM FROM GOOGLE CSE ===
Title: [Title]
Link: https://www.facebook.com/...
Pagemap keys: ['cse_image', 'metatags', ...]
Full pagemap: {
  "cse_image": [{...}],
  "metatags": [{...}]
}
```

### Step 5: Check Frontend Console
In the browser console, look for:
```
=== FACEBOOK RESULT ===
Title: [Title]
Link: https://www.facebook.com/...
Pagemap keys: ["cse_image", "metatags", ...]
Full pagemap: {...}
```

---

## What to Compare

### Check These Questions:

#### Q1: Does Backend Show Image Data?
Look in backend logs for:
```
✓ Has cse_image: [{'src': 'https://...'}]
```
or
```
✓ Has metatags
  ✓ og:image: https://...
```

**If YES** → Data is coming from Google  
**If NO** → Something wrong with API call

#### Q2: Does Frontend Receive Image Data?
Look in browser console for:
```
Pagemap keys: ["cse_image", "metatags", ...]
```

**Compare with Backend:** Should be identical!

#### Q3: Does Frontend Extract the Image?
Look for:
```
✓ Using cse_image src: https://...
```
or
```
✓ Using og:image: https://...
```

**If YES** → Image URL extracted successfully  
**If NO** → Extraction logic has a bug

#### Q4: Does the Image Display?
Look at the actual Facebook result card.

**If NO** → Check Network tab for image loading errors

---

## Possible Issues & Solutions

### Issue 1: Backend Gets Image, Frontend Doesn't
**Symptom:**
- Backend logs show: `✓ Has cse_image`
- Frontend logs show: `Pagemap keys: []` or missing cse_image

**Cause:** Data not being passed correctly from backend to frontend

**Solution:** Check the API response structure

### Issue 2: Frontend Gets Image Data, But Doesn't Extract It
**Symptom:**
- Frontend logs show: `Pagemap keys: ["cse_image", ...]`
- But also shows: `✗ No image found in pagemap`

**Cause:** Extraction logic not handling the data format correctly

**Possible reasons:**
1. `cse_image[0].src` might be at different path
2. Data might not be an array
3. Property name might be different

**Solution:** Look at the EXACT structure in the logs and adjust extraction logic

### Issue 3: Image URL Extracted But Doesn't Display
**Symptom:**
- Frontend logs show: `✓ Using cse_image src: https://...`
- But image doesn't show on card

**Cause:** CORS, 403, or image loading error

**Solution:**
1. Check Network tab (F12 → Network → Filter: Img)
2. Look for failed requests
3. May need image proxy

---

## Comparison Test

### Test 1: Same Query, Different Interface

**In Google CSE Web Interface:**
1. Go to: https://cse.google.com/cse?cx=30671ef5d35724992
2. Search: "Tejas crash Dubai"
3. Find a Facebook result with an image
4. Note the image URL

**In Your Application:**
1. Search: "Tejas crash Dubai"
2. Check console logs
3. Look for the SAME Facebook result
4. Compare the image URL

**Expected:** URLs should be identical!

---

## Data Structure Examples

### Expected CSE Response (What Backend Should Receive):
```json
{
  "items": [{
    "title": "...",
    "link": "https://www.facebook.com/...",
    "pagemap": {
      "cse_image": [{
        "src": "https://external.xx.fbcdn.net/..."
      }],
      "metatags": [{
        "og:image": "https://external.xx.fbcdn.net/...",
        "og:title": "..."
      }]
    }
  }]
}
```

### What Frontend Should Receive:
```typescript
{
  title: "...",
  link: "https://www.facebook.com/...",
  source_site: "facebook.com",
  pagemap: {
    cse_image: [{
      src: "https://external.xx.fbcdn.net/..."
    }],
    metatags: [{
      "og:image": "https://external.xx.fbcdn.net/..."
    }]
  }
}
```

---

## Debug Commands

### Check Backend Logs:
```powershell
# In backend terminal - already showing logs
# Look for "=== FACEBOOK ITEM FROM GOOGLE CSE ==="
```

### Check Frontend Console:
```javascript
// In browser console (F12)
// Filter by typing: FACEBOOK
```

### Test API Directly:
```powershell
# Test backend endpoint directly
curl http://localhost:8000/api/v1/social-search -X POST -H "Content-Type: application/json" -d "{\"query\":\"Tejas crash Dubai\",\"sites\":[\"facebook.com\"]}"
```

### Compare with Google CSE API:
```powershell
# Direct Google CSE API call
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=30671ef5d35724992&q=site:facebook.com+Tejas+crash+Dubai"
```

---

## Quick Fixes (If Needed)

### Fix 1: If pagemap Structure is Different
Based on logs, we might need to adjust extraction:

```typescript
// Instead of:
pagemap['cse_image'][0]?.src

// Might need:
pagemap['cse_image']?.src  // If not an array
// or
pagemap['cse_image'][0]?.['src']  // Different access
// or  
pagemap['cse_image']?.[0]  // If src is the value itself
```

### Fix 2: If Image is in Different Field
```typescript
// Check all possible fields:
console.log('All pagemap data:', pagemap);
console.log('Keys:', Object.keys(pagemap));

// Try each key:
for (const [key, value] of Object.entries(pagemap)) {
  console.log(`${key}:`, value);
}
```

### Fix 3: If CORS is Blocking
Add image proxy in backend:
```python
@app.get("/api/v1/image-proxy")
async def image_proxy(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "image/jpeg")
        )
```

---

## Expected Output Example

### Backend Terminal:
```
2025-12-22 00:41:47 | INFO | app.services.social_search_service | === FACEBOOK ITEM FROM GOOGLE CSE ===
2025-12-22 00:41:47 | INFO | app.services.social_search_service | Title: IAF's Tejas fighter jet crashes at Dubai Air Show
2025-12-22 00:41:47 | INFO | app.services.social_search_service | Link: https://www.facebook.com/...
2025-12-22 00:41:47 | INFO | app.services.social_search_service | Pagemap keys: ['cse_image', 'metatags']
2025-12-22 00:41:47 | INFO | app.services.social_search_service | Full pagemap: {
  "cse_image": [
    {
      "src": "https://external.xx.fbcdn.net/..."
    }
  ]
}
2025-12-22 00:41:47 | INFO | app.services.social_search_service | ✓ Has cse_image: [{'src': 'https://...'}]
```

### Browser Console:
```
=== FACEBOOK RESULT ===
Title: IAF's Tejas fighter jet crashes at Dubai Air Show
Link: https://www.facebook.com/...
Pagemap keys: ["cse_image", "metatags"]
Full pagemap: {
  "cse_image": [{
    "src": "https://external.xx.fbcdn.net/..."
  }]
}
Found cse_image: [{src: "https://..."}]
✓ Using cse_image src: https://external.xx.fbcdn.net/...
```

---

## Action Items

1. ☑️ Backend logging enhanced
2. ☑️ Frontend logging enhanced  
3. ☑️ Backend restarted
4. ☑️ Frontend running

**NOW YOU NEED TO:**

1. **Open browser console (F12)**
2. **Perform a search**
3. **Look at BOTH backend terminal AND browser console**
4. **Copy and paste the logs here** - especially:
   - Backend: `=== FACEBOOK ITEM FROM GOOGLE CSE ===` section
   - Frontend: `=== FACEBOOK RESULT ===` section

This will tell us EXACTLY where the problem is! 🎯

---

## Summary

🔍 **Root Cause:** Google HAS the images, we're just not extracting/displaying them correctly  
📊 **Diagnosis:** Need to see actual data structure from logs  
🛠️ **Solution:** Will adjust extraction logic based on what logs reveal  

**The logs will tell us everything!** Please run a search and share what you see. 🚀
