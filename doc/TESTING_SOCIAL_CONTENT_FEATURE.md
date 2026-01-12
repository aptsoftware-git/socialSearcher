# Testing Social Media Full Content Feature

## ✅ Setup Complete!

### Current Status
- ✅ **Backend:** Running on http://127.0.0.1:8000
- ✅ **Frontend:** Running on http://localhost:5173
- ✅ **Feature:** Social Media Full Content Extraction
- ✅ **Modal:** SocialContentModal component created
- ✅ **Button:** "View Full Content" button added to each result

---

## 🎯 What Has Been Implemented

### 1. Configuration (Feature #1)
✅ **MAX_SOCIAL_SEARCH_RESULTS** is now configurable via `.env` file
- Location: `backend/.env`
- Variable: `MAX_SOCIAL_SEARCH_RESULTS=10`
- Can be changed without code modification

### 2. API Credentials (Feature #2)
✅ All platform credentials configured:
- **YouTube:** API Key configured
- **Facebook:** App ID, Secret, Access Token configured
- **Twitter/X:** Bearer Token configured
- **Instagram:** ⚠️ Requires Business Account (pending)

### 3. UI Implementation (Feature #3)
✅ **"View Full Content" Button:**
- Added to every social media search result card
- Shows loading spinner while fetching
- Fetches full content from platform APIs (not Google snippets)

✅ **Popup Modal (SocialContentModal):**
- Displays full post content (text, title, description)
- Shows author information with profile picture
- Displays all media (images/videos) in gallery
- Shows engagement metrics (likes, comments, shares, views)
- Has "Open Original" button to view on platform

✅ **"Analyse" Button in Modal:**
- Uses existing LLM (Claude/Ollama)
- Extracts structured event information
- Displays event details in the modal:
  - Event Type & Subtype
  - Title & Summary
  - Date & Time
  - Location (venue, city, country)
  - Perpetrator information
  - Casualties (if applicable)
  - Organizations involved
  - Confidence score

---

## 🧪 How to Test

### Step 1: Perform a Social Media Search
1. Open http://localhost:5173 in your browser
2. Enter a search query (e.g., "APT threat", "cyber attack", "security breach")
3. Wait for results to appear

### Step 2: View Search Results
You should see:
- Results grouped by platform (Facebook, Twitter/X, YouTube, Instagram)
- Each result card shows: Title, Snippet, Thumbnail
- **NEW:** "View Full Content" button on each card

### Step 3: Test "View Full Content"
1. Click the **"View Full Content"** button on any result
2. Button shows loading spinner
3. Backend fetches full content using platform API
4. Modal popup opens with complete content

### Step 4: Review Full Content in Modal
The modal displays:
- ✅ Platform icon and name
- ✅ "Cached" badge (if from cache)
- ✅ Author profile picture and name
- ✅ Verification badge (if verified account)
- ✅ Posted date and time
- ✅ "Open Original" button
- ✅ Full text content
- ✅ Title (if available)
- ✅ Media gallery (all images/videos)
- ✅ Engagement metrics with icons

### Step 5: Test "Analyse with AI"
1. In the modal, click **"Analyse with AI"** button
2. Button shows "Analysing with AI..." with spinner
3. Backend sends content to LLM (Claude or Ollama)
4. Extracted event appears in modal below

### Step 6: Review Extracted Event
The event card shows:
- ✅ Event title
- ✅ Event type (color-coded chip)
- ✅ Event sub-type (if applicable)
- ✅ Date and time with calendar icon
- ✅ Location with map icon
- ✅ Summary/description
- ✅ Perpetrator info (if applicable)
- ✅ Casualties (if applicable)
- ✅ Organizations (chips)
- ✅ Confidence score (color-coded)

---

## 📊 Test Scenarios

### Scenario 1: YouTube Video
**Test URL:** Any YouTube video from search results

**Expected:**
- ✅ Video title
- ✅ Description
- ✅ Thumbnail
- ✅ Views, likes, comments count
- ✅ Channel name
- ✅ Video duration
- ✅ Published date

**Example Query:** "security conference 2024"

### Scenario 2: Twitter/X Post
**Test URL:** Any Twitter/X post from search results

**Expected:**
- ✅ Tweet text
- ✅ Author name and username
- ✅ Verification badge (if verified)
- ✅ Images/videos in tweet
- ✅ Likes, retweets, replies count
- ✅ Posted timestamp

**Example Query:** "APT attack news"

### Scenario 3: Facebook Post
**Test URL:** Any Facebook post from search results

**Expected:**
- ✅ Post text
- ✅ Author/Page name
- ✅ Images/videos
- ✅ Reactions, comments, shares count
- ✅ Posted timestamp

**Example Query:** "cyber incident"

### Scenario 4: Instagram Post (⚠️ Pending)
**Status:** Instagram requires Business Account conversion

**Action Needed:**
1. Convert Instagram account to Business
2. Connect to Facebook Page
3. Update `.env` with Instagram token
4. Test Instagram content fetching

---

## 🔍 Verification Checklist

### Backend Verification
- [ ] Backend running on http://127.0.0.1:8000
- [ ] No errors in backend terminal
- [ ] `.env` file has all API credentials
- [ ] `MAX_SOCIAL_SEARCH_RESULTS=10` in `.env`

### Frontend Verification
- [ ] Frontend running on http://localhost:5173
- [ ] No compilation errors
- [ ] Browser console has no errors

### Feature #1: Configurable Search Limit
- [ ] Open `backend/.env`
- [ ] Find `MAX_SOCIAL_SEARCH_RESULTS=10`
- [ ] Change to different value (e.g., `5`)
- [ ] Restart backend
- [ ] Perform search
- [ ] Verify only 5 results per platform (instead of 10)

### Feature #2: Full Content Extraction
- [ ] Perform social media search
- [ ] Click "View Full Content" on YouTube result
  - [ ] Full video details displayed
  - [ ] Engagement metrics visible
- [ ] Click "View Full Content" on Twitter result
  - [ ] Full tweet text displayed
  - [ ] Media gallery works
- [ ] Click "View Full Content" on Facebook result
  - [ ] Full post text displayed
  - [ ] Reactions count visible

### Feature #3: AI Analysis
- [ ] Open modal with full content
- [ ] Click "Analyse with AI" button
- [ ] Loading spinner appears
- [ ] Event card appears after analysis
- [ ] Event contains:
  - [ ] Title
  - [ ] Event type
  - [ ] Date/Location
  - [ ] Summary
  - [ ] Confidence score

---

## 🐛 Troubleshooting

### Issue: "View Full Content" Button Does Nothing
**Cause:** Backend not running or API connection failed

**Solution:**
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: Modal Opens But Empty
**Cause:** API credentials invalid or expired

**Solution:**
1. Check backend logs for API errors
2. Verify credentials in `.env` file
3. Regenerate tokens if expired

### Issue: YouTube Quota Exceeded (403 Error)
**Cause:** YouTube API free tier limit (10,000 quota/day)

**Solution:**
1. Wait 24 hours for quota reset
2. Enable billing in Google Cloud Console for higher quota
3. Check quota usage: https://console.cloud.google.com/apis/dashboard

### Issue: Twitter Bearer Token Invalid (401 Error)
**Cause:** Token expired or revoked

**Solution:**
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Regenerate Bearer Token
3. Update `TWITTER_BEARER_TOKEN` in `.env`
4. Restart backend

### Issue: Facebook Token Invalid (403 Error)
**Cause:** Token expired (tokens expire in 60 days)

**Solution:**
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Generate new Access Token with permissions
4. Extend to long-lived token: https://developers.facebook.com/tools/debug/accesstoken/
5. Update `FACEBOOK_ACCESS_TOKEN` in `.env`
6. Restart backend

### Issue: Instagram Not Working
**Status:** Expected - Requires Business Account

**Solution:** Follow Instagram setup guide in `SOCIAL_CONTENT_IMPLEMENTATION_COMPLETE.md`

### Issue: "Analyse" Button Gives Error
**Cause:** LLM service not configured or down

**Solution:**
1. Check if Ollama is running (if using Ollama)
2. Check Claude API key (if using Claude)
3. Check backend logs for LLM errors

### Issue: Cached Data Stale
**Cause:** Cache duration is 24 hours

**Solution:**
```bash
# Clear cache via API
curl -X POST http://localhost:8000/api/v1/social-content/cache/clear

# Or clear specific platform
curl -X POST "http://localhost:8000/api/v1/social-content/cache/clear?platform=youtube"
```

---

## 📈 Expected Behavior

### First Time (No Cache)
1. Click "View Full Content"
2. Loading spinner: ~2-5 seconds
3. Modal opens with content
4. "Cached" badge: **NOT visible**

### Second Time (From Cache)
1. Click "View Full Content" on same URL
2. Loading spinner: <1 second
3. Modal opens with content
4. "Cached" badge: **VISIBLE** (blue chip)

### Analysis Time
- **Fast:** 3-10 seconds (Ollama local)
- **Medium:** 5-15 seconds (Claude API)
- **Depends on:** Content length, LLM load

---

## 🎯 Success Indicators

### ✅ Feature Working Correctly
- Results show "View Full Content" button
- Button changes to "Loading..." when clicked
- Modal opens with full content within 5 seconds
- Content shows more detail than Google snippet
- Media gallery displays images/videos
- Engagement metrics visible
- "Analyse with AI" extracts event
- No errors in browser console

### ❌ Feature Not Working
- Button does nothing when clicked
- Modal stays blank
- Error alerts appear
- Browser console shows 404 or 500 errors
- Backend logs show API authentication errors

---

## 📝 Next Steps After Testing

### If Everything Works ✅
1. Test with various queries
2. Test all platforms (YouTube, Twitter, Facebook)
3. Test event extraction accuracy
4. Monitor API quota usage
5. Set up Instagram Business Account (if needed)

### If Issues Found ❌
1. Check browser console for errors
2. Check backend logs for API errors
3. Verify API credentials in `.env`
4. Check API quota limits
5. Report specific error messages

---

## 💡 Tips for Best Results

1. **Search Quality:**
   - Use specific queries (e.g., "APT28 attack 2024" vs "attack")
   - Include location or event type
   - Use quotes for exact phrases

2. **Content Analysis:**
   - Posts with more text give better event extraction
   - Videos may have limited text for analysis
   - Images alone won't extract events (need text)

3. **API Limits:**
   - YouTube: ~100-1000 requests/day (free tier)
   - Twitter: 500K tweets/month
   - Facebook: 200 calls/hour
   - Cache reduces API usage by 90%

4. **Performance:**
   - First load: Slow (API call + LLM)
   - Cached load: Fast (<1 second)
   - Clear cache if stale data

---

## 📚 Documentation References

- **Full Implementation Guide:** `doc/SOCIAL_CONTENT_IMPLEMENTATION_COMPLETE.md`
- **Original Plan:** `doc/SOCIAL_CONTENT_EXTRACTION_PLAN.md`
- **Backend API Docs:** http://127.0.0.1:8000/docs (when backend running)
- **Frontend Code:** `frontend/src/components/SocialContentModal.tsx`
- **API Service:** `frontend/src/services/api.ts`

---

**Test Status:** ⏳ **READY FOR TESTING**  
**Last Updated:** January 2, 2026  
**Implementation:** ✅ **COMPLETE**
