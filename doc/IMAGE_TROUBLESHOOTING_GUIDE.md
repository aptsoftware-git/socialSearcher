# Facebook/Instagram Image Not Showing - Troubleshooting

**Date:** December 22, 2025  
**Status:** 🔧 Investigating  
**Issue:** Images still not displaying after proxy implementation

---

## Issue Fixed: Proxy URL Format

### The Bug:
```typescript
// WRONG - This goes to frontend server (localhost:5173)
return `/api/v1/proxy-image?url=${encodeURIComponent(imageUrl)}`;
```

### The Fix:
```typescript
// CORRECT - This goes to backend server (localhost:8000)
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
return `${backendUrl}/api/v1/proxy-image?url=${encodeURIComponent(imageUrl)}`;
```

---

## Testing Steps

### Step 1: Verify Backend is Running
✅ Backend restarted and running on `http://127.0.0.1:8000`

### Step 2: Hard Refresh Browser
**IMPORTANT:** Vite may have cached the old code
1. Press **Ctrl+Shift+Delete**
2. Clear cached images and files
3. Press **Ctrl+F5** for hard refresh
4. Or close browser completely and reopen

### Step 3: Check Browser Console
Press **F12** → Console tab

**Look for:**
```
🔄 Using proxy for: https://external.xx.fbcdn.net/...
```

**Proxy URL should be:**
```
http://127.0.0.1:8000/api/v1/proxy-image?url=https%3A%2F%2Fexternal.xx.fbcdn.net%2F...
```

### Step 4: Check Network Tab
Press **F12** → Network tab

**Look for requests to:**
```
http://127.0.0.1:8000/api/v1/proxy-image?url=...
```

**Should see:**
- Status: **200 OK**
- Type: **jpeg** or **png**
- Size: **Actual size** (not 0.0 kB)

---

## Diagnostic Checklist

### ✓ Check 1: Console Logs

**Open Browser Console (F12 → Console)**

**For Facebook results, you should see:**
```
Processing result from: facebook.com | Title: ...
📋 Pagemap keys for facebook.com: ["cse_image", "metatags"]
✅ Using cse_image: https://external.xx.fbcdn.net/...
🔄 Using proxy for: https://external.xx.fbcdn.net/...
```

**If you DON'T see "🔄 Using proxy":**
- Frontend code not updated
- Hard refresh needed

**If you see "❌ No image found":**
- Google CSE didn't return image data
- This specific Facebook post has no image

### ✓ Check 2: Network Requests

**Open Network Tab (F12 → Network)**

**Filter by: "proxy"**

**Should see:**
```
Request URL: http://127.0.0.1:8000/api/v1/proxy-image?url=https%3A%2F%2Fexternal.xx.fbcdn.net%2F...
Status: 200 OK
Content-Type: image/jpeg
Size: 45.2 kB
```

**If you see 404 Not Found:**
- Backend endpoint not registered
- Backend needs restart

**If you see 403 Forbidden:**
- Domain not in whitelist
- Check backend logs

**If you see 504 Timeout:**
- Facebook CDN slow/unreachable
- Increase timeout

### ✓ Check 3: Image Element

**Inspect the image element:**
```html
<img src="http://127.0.0.1:8000/api/v1/proxy-image?url=..." />
```

**Should NOT be:**
```html
<img src="http://localhost:5173/api/v1/proxy-image?url=..." />
```

### ✓ Check 4: Backend Logs

**In backend terminal, look for:**
```
DEBUG: Proxying image: https://external.xx.fbcdn.net/...
```

**If you see errors:**
```
ERROR: HTTP error proxying image: 403
ERROR: Failed to proxy image: ...
```

Check what the error says.

---

## Common Issues & Solutions

### Issue 1: "Network error" or "ERR_CONNECTION_REFUSED"

**Cause:** Frontend trying to connect to wrong URL

**Check Console:**
```javascript
// Should log the FULL URL
console.log('Proxy URL:', proxiedImageUrl);
```

**Solution:**
- Verify `VITE_API_BASE_URL` in `.env` file
- Hard refresh browser
- Restart frontend dev server

### Issue 2: "404 Not Found" on proxy-image endpoint

**Cause:** Backend endpoint not registered or backend not restarted

**Solution:**
```powershell
# Restart backend
cd backend
python -m uvicorn app.main:app --reload
```

**Verify endpoint exists:**
```powershell
curl http://127.0.0.1:8000/docs
# Check if /api/v1/proxy-image appears in the API docs
```

### Issue 3: "403 Forbidden" from proxy

**Cause:** Domain not in whitelist

**Check backend code (main.py):**
```python
allowed_domains = [
    'fbcdn.net',           # Facebook
    'twimg.com',           # Twitter
    'cdninstagram.com',    # Instagram
    'ytimg.com',           # YouTube
]
```

**Solution:**
Add the domain if missing, then restart backend.

### Issue 4: "CORS error" still appearing

**Cause:** Image URL not being proxied

**Check Console:**
```
✅ Using cse_image: https://external.xx.fbcdn.net/...
```

**Should also see:**
```
🔄 Using proxy for: https://external.xx.fbcdn.net/...
```

**If missing "🔄 Using proxy":**
- getProxiedImageUrl() not being called
- Check sourceSite string
- Hard refresh needed

### Issue 5: Images load for YouTube but not Facebook

**This is EXPECTED if:**
- YouTube doesn't have CORS restrictions
- YouTube images load directly
- Facebook/Instagram need proxy

**Verify in console:**
```
// YouTube (direct)
Processing result from: youtube.com
✅ Using cse_image: https://i.ytimg.com/...
(No proxy message - loads directly)

// Facebook (proxied)
Processing result from: facebook.com
✅ Using cse_image: https://external.xx.fbcdn.net/...
🔄 Using proxy for: https://external.xx.fbcdn.net/...
```

---

## Manual Test Commands

### Test 1: Direct Backend Proxy Test
```powershell
# Test proxy endpoint directly
curl "http://127.0.0.1:8000/api/v1/proxy-image?url=https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg"

# Should return image data
```

### Test 2: Check Backend API Docs
```powershell
# Open in browser
http://127.0.0.1:8000/docs

# Look for GET /api/v1/proxy-image
```

### Test 3: Check Frontend Environment
```javascript
// In browser console
console.log('Backend URL:', import.meta.env.VITE_API_BASE_URL);
// Should log: http://127.0.0.1:8000
```

### Test 4: Verify Proxy Logic
```javascript
// In browser console, test the function
const testUrl = 'https://external.xx.fbcdn.net/test.jpg';
const testSite = 'facebook.com';
const needsProxy = testSite.includes('facebook') || 
                  testSite.includes('instagram') ||
                  testUrl.includes('fbcdn.net');
console.log('Needs proxy:', needsProxy); // Should be true
```

---

## Environment Variables Check

### Frontend (.env or vite.config.ts)
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**If not set, defaults to:** `http://127.0.0.1:8000`

### Verify in Browser Console:
```javascript
import.meta.env.VITE_API_BASE_URL
// Should output: "http://127.0.0.1:8000"
```

---

## Step-by-Step Debug Process

### 1. Clear Everything
```powershell
# Stop all servers
# Ctrl+C in all terminals

# Clear browser
# Ctrl+Shift+Delete → Clear all

# Restart backend
cd backend
python -m uvicorn app.main:app --reload

# Restart frontend
cd frontend
npm run dev
```

### 2. Open Browser Console Before Search
```
F12 → Console tab → Clear console
```

### 3. Perform Search
```
Search for: "Tejas crash"
Enable: Social Search
Click: Search
```

### 4. Watch Console Output
```
Look for each Facebook result:
1. Processing result from: facebook.com | Title: ...
2. 📋 Pagemap keys: [...]
3. ✅ Using cse_image: https://...
4. 🔄 Using proxy for: https://...  ← THIS IS CRITICAL
```

### 5. Check Network Tab
```
Filter: "proxy"
Look for: 127.0.0.1:8000/api/v1/proxy-image
Status: 200 OK
```

### 6. Check Image Element
```
Right-click image area → Inspect
Look at <img src="..." />
Should start with: http://127.0.0.1:8000
```

---

## What Each Log Means

### Console Output Explained:

```
Processing result from: facebook.com | Title: [Title]
→ Starting to process this Facebook result

📋 Pagemap keys for facebook.com: ["cse_image", "metatags"]
→ Google CSE provided these fields

✅ Using cse_image: https://external.xx.fbcdn.net/safe_image.php?...
→ Successfully extracted image URL from pagemap

🔄 Using proxy for: https://external.xx.fbcdn.net/...
→ Routing through backend proxy (CRITICAL - must see this!)
```

**If you see all 4 lines:**
- ✅ Extraction working
- ✅ Proxy being used
- Check Network tab for 200 OK

**If you see lines 1-3 but NOT line 4:**
- ❌ Proxy not being triggered
- Frontend code not updated
- Hard refresh needed

**If you only see lines 1-2:**
- ❌ Image extraction failing
- Check pagemap structure
- May need to adjust extraction logic

---

## Expected vs Actual

### Expected (Working):
```
Console:
✅ Using cse_image: https://external.xx.fbcdn.net/...
🔄 Using proxy for: https://external.xx.fbcdn.net/...

Network Tab:
http://127.0.0.1:8000/api/v1/proxy-image?url=...
Status: 200 OK
Size: 45.2 kB

Visual:
[IMAGE DISPLAYS] ✅
```

### Actual (If Not Working):
Please provide:
1. Console output for a Facebook result
2. Network tab screenshot showing proxy requests
3. Any error messages

---

## Quick Fix Checklist

- [ ] Backend restarted with new proxy endpoint
- [ ] Frontend hard refreshed (Ctrl+F5)
- [ ] Browser cache cleared
- [ ] Console shows "🔄 Using proxy" for Facebook
- [ ] Network tab shows requests to 127.0.0.1:8000
- [ ] Proxy requests return 200 OK (not 404/403)

---

## Next Steps

1. **Hard refresh browser** (Ctrl+F5)
2. **Open console and Network tab** (F12)
3. **Perform a search**
4. **Share the console logs** showing:
   - Whether you see "🔄 Using proxy"
   - Any error messages
5. **Share Network tab screenshot** showing:
   - Proxy requests and their status

This will help identify exactly where the issue is! 🔍
