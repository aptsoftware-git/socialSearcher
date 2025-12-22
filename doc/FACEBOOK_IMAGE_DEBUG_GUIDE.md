# Facebook Image Debug - Testing Guide

**Date:** December 22, 2025  
**Issue:** Facebook images not displaying  
**Status:** 🔍 Enhanced Debug Logging Active

---

## What Was Added

Added comprehensive console logging to track exactly what image data is available from Google Custom Search Engine for Facebook results.

---

## How to Test

### Step 1: Open Browser DevTools
1. Open your browser (Chrome/Edge recommended)
2. Press **F12** to open Developer Tools
3. Click on the **Console** tab
4. Clear console (trash icon) for a fresh start

### Step 2: Perform a Search
1. Go to your frontend application
2. Check "Use Social Media Search ONLY..."
3. Enter a search query (e.g., "breaking news" or "Tejas crash Dubai")
4. Click **Search**

### Step 3: Watch Console Output
You should see detailed logs for each result. For Facebook results, look for:

```
=== FACEBOOK RESULT ===
Title: [Post title]
Link: https://www.facebook.com/...
Pagemap keys: ["metatags", "cse_image", ...]
Full pagemap: {
  "metatags": [...],
  "cse_image": [...],
  ...
}
```

---

## What to Look For

### Case 1: Image Found ✓
```
Processing result from: facebook.com
=== FACEBOOK RESULT ===
Title: Breaking News Post
Link: https://www.facebook.com/...
Pagemap keys: ["metatags", "cse_image"]
Found cse_image: [{src: "https://..."}]
✓ Using cse_image src: https://...
```
**Expected:** Image should display on left side

### Case 2: Image in Metatags
```
Processing result from: facebook.com
=== FACEBOOK RESULT ===
Pagemap keys: ["metatags"]
Found metatags, keys: ["og:image", "og:title", ...]
✓ Using og:image: https://...
```
**Expected:** Image should display on left side

### Case 3: No Image Available
```
Processing result from: facebook.com
=== FACEBOOK RESULT ===
Pagemap keys: ["metatags"]
Found metatags, keys: ["og:title", "og:description"]
✗ No image found in pagemap for: facebook.com
```
**Expected:** No image shown (card displays without image on left)

### Case 4: No Pagemap
```
Processing result from: facebook.com
No pagemap found for: facebook.com [Title]
```
**Expected:** No image shown

---

## What to Report Back

Please copy and paste from the console:

### For a Facebook result WITH an image:
```
=== FACEBOOK RESULT ===
[paste the full output here]
```

### For a Facebook result WITHOUT an image:
```
=== FACEBOOK RESULT ===
[paste the full output here]
```

---

## Common Findings

### If you see this:
```json
{
  "metatags": [{
    "og:image": "https://external.xx.fbcdn.net/..."
  }]
}
```
✅ **Good!** Facebook has an image, and it should display.

### If you see this:
```json
{
  "metatags": [{
    "og:title": "...",
    "og:description": "..."
  }]
}
```
❌ **No image available** - Facebook didn't provide image metadata for this post.

### If you see this:
```json
{
  "cse_image": [{
    "src": "https://..."
  }]
}
```
✅ **Perfect!** Google CSE extracted the image successfully.

---

## Troubleshooting

### Images URLs Found But Not Displaying?

If console shows: `✓ Using og:image: https://...` but image doesn't show:

1. **Check Network Tab:**
   - Open DevTools → Network tab
   - Filter by "Img"
   - Look for failed image requests
   - Check status code (403 = blocked, 404 = not found)

2. **Common Causes:**
   - **CORS blocking:** Facebook blocking cross-origin requests
   - **Authentication required:** Image needs login
   - **Invalid URL:** Link expired or moved
   - **Content-Security-Policy:** Browser blocking mixed content

3. **Verify in New Tab:**
   - Copy the image URL from console
   - Open in new browser tab
   - If it loads → CORS issue
   - If it doesn't load → Invalid URL

### Example CORS Error:
```
Access to image at 'https://external.xx.fbcdn.net/...' 
from origin 'http://localhost:5173' has been blocked by 
CORS policy
```

---

## Quick Fix for Testing (If CORS is the issue)

### Option 1: Use a CORS Proxy (Development Only)
Temporarily modify the image URL extraction:

```typescript
if (meta['og:image']) {
  const imageUrl = meta['og:image'] as string;
  // Use CORS proxy for testing
  return `https://corsproxy.io/?${encodeURIComponent(imageUrl)}`;
}
```

### Option 2: Backend Proxy (Better Solution)
Create an endpoint in backend to proxy images:

```python
@app.get("/api/v1/proxy-image")
async def proxy_image(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return Response(content=response.content, media_type="image/jpeg")
```

Then use: `/api/v1/proxy-image?url=${encodeURIComponent(imageUrl)}`

---

## Expected Console Output Example

Here's what a successful run looks like:

```
Processing result from: facebook.com
=== FACEBOOK RESULT ===
Title: IAF's Tejas fighter jet crashes at Dubai Air Show
Link: https://www.facebook.com/news/...
Pagemap keys: ["metatags", "cse_image", "cse_thumbnail"]
Full pagemap: {
  "metatags": [{
    "og:image": "https://external.xx.fbcdn.net/safe_image.php?...",
    "og:title": "IAF's Tejas fighter jet crashes...",
    "og:description": "The accident occurred..."
  }],
  "cse_image": [{
    "src": "https://external.xx.fbcdn.net/..."
  }]
}
Found cse_image: [{src: "https://external.xx.fbcdn.net/..."}]
✓ Using cse_image src: https://external.xx.fbcdn.net/...

Processing result from: x.com
...
```

---

## Next Steps After Testing

### If Images ARE Found in Pagemap:
1. Check if they're displaying
2. If not, check Network tab for CORS/loading errors
3. May need to implement image proxy

### If Images ARE NOT in Pagemap:
1. This is expected for many Facebook posts
2. Facebook often restricts bot access
3. Google CSE might not be able to extract images
4. Consider showing placeholder icon

### Alternative: Show Placeholder When No Image
```typescript
{!imageUrl && (
  <Box sx={{ width: 120, height: 120, bgcolor: 'grey.100', 
             display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <FacebookIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.3 }} />
  </Box>
)}
```

---

## Summary

🔍 **Enhanced logging is now active**  
📊 **Console will show exactly what data is available**  
🎯 **We can then determine if it's a data issue or display issue**  

**Please run a search and share what you see in the console!**

---

## Quick Commands

### Clear Console:
- **Chrome/Edge:** Ctrl + L or click trash icon
- **Firefox:** Ctrl + Shift + L

### Filter Console:
- Type "FACEBOOK" in the filter box to see only Facebook logs
- Type "✓" to see only successful image finds
- Type "✗" to see only failures

### Copy Console Output:
- Right-click in console
- Select "Save as..." to export all logs
- Or select text and Ctrl+C to copy

---

Good luck! The logs will tell us exactly what's happening. 🚀
