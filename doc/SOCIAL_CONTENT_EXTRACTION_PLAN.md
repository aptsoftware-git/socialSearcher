# Social Media Full Content Extraction - Implementation Plan

**Date:** January 2, 2026  
**Status:** 🟡 Awaiting Clarifications  
**Goal:** Extract full content from Facebook, Twitter/X, YouTube, and Instagram posts

---

## 📋 Credentials Provided

### ✅ Complete Credentials

#### 1. Google/YouTube APIs
```env
YOUTUBE_API_KEY=AIzaSyCTW_aDGUfmg_0fa-6h3pdKJ8CpHwNCMsw
GOOGLE_CSE_API_KEY=AIzaSyCW5_YD0xHdCy6tfqo9l90VYAxM70ALn4Q
GOOGLE_CSE_ID=7488bda26ebca49e4
```
**Status:** ✅ Ready to use

#### 2. Facebook APIs
```env
FACEBOOK_APP_ID=2073969890024801
FACEBOOK_APP_SECRET=65b43b32edf7c7e0c9fe51a19cdd5aef
ConfigureID=1588906565632803
```
**Status:** ⚠️ **Missing Access Token** - Required to fetch posts

**Action Required:**
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app: "APT Social Search"
3. Click "Generate Access Token"
4. Select permissions:
   - `pages_read_engagement`
   - `public_profile`
   - `user_posts` (if needed)
5. Copy token and add to `.env`:
   ```env
   FACEBOOK_ACCESS_TOKEN=EAA...your_token_here
   ```

#### 3. Instagram APIs
```env
INSTAGRAM_APP_ID=1202849454604839
INSTAGRAM_APP_SECRET=1fc377355f53eb59a56269e988d0f9ac
```
**Status:** ⚠️ **Missing Access Token + Business Account Setup**

**Action Required:**
1. Convert Instagram account to Business Account:
   - Open Instagram app
   - Go to Settings → Account → Switch to Professional Account
   - Choose "Business"
2. Connect to Facebook Page:
   - Settings → Business → Connect to Facebook Page
3. Get Access Token:
   - Go to: https://developers.facebook.com/tools/explorer/
   - Select Instagram Graph API
   - Generate token with `instagram_basic` permission
4. Add to `.env`:
   ```env
   INSTAGRAM_ACCESS_TOKEN=IGQ...your_token_here
   ```

#### 4. Twitter/X APIs
```env
TWITTER_API_KEY=mI1HCLHtIJBSd3NxJkAcLhLAv
TWITTER_API_KEY_SECRET=JfMzH2WUXyITl5xXjrIqkXYsnFIVSb5jm7M4WacR8ad4nsBeEf
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAJy56gEAAAAAD60e5d3ckMgelijFspTy6lRmqTs%3D...
TWITTER_ACCESS_TOKEN=2006762126631989248-uGYPSjIhSCJwLbzBEu3PhqN7SbZyqz
TWITTER_ACCESS_TOKEN_SECRET=KLv9Jlz20KBDOQbYiLzwyIKG7iFSR7XQAVQXwbX7vRkmD
```
**Status:** ✅ Ready to use

---

## 🎯 Requirements

### Feature 1: Configurable Search Limit ✅
**Current:** Hardcoded value of 10 results per platform  
**Required:** Load from configuration file

**Decision Needed:**
- Option A: `.env` file → `MAX_SOCIAL_SEARCH_RESULTS=10`
- Option B: `config/sources.yaml` → Add social media section
- Option C: New `config/social_config.yaml` file

**Recommended:** Option A (`.env`) - Already implemented ✅

### Feature 2: Full Content Extraction 🔧
**Current:** Only Google CSE snippets (title, preview text, URL)  
**Required:** Fetch full content using platform APIs

**Content to Extract:**

#### Facebook Posts
- ✅ Post message/text
- ✅ Post images/videos (URLs)
- ✅ Reactions count (likes, love, etc.)
- ✅ Comments count
- ✅ Shares count
- ✅ Post date/time
- ✅ Author name, profile picture
- ❓ Comments content (requires additional permission)

#### Twitter/X Posts
- ✅ Tweet full text (up to 280 chars, or longer for extended tweets)
- ✅ Media (images, videos, GIFs)
- ✅ Retweets count
- ✅ Likes count
- ✅ Replies count
- ✅ Tweet date/time
- ✅ Author info (name, @username, profile pic, verified status)
- ❓ Quoted tweets
- ❓ Thread context

#### YouTube Videos
- ✅ Video title
- ✅ Full description
- ✅ Thumbnail (multiple sizes)
- ✅ Duration
- ✅ View count
- ✅ Like count
- ✅ Comment count
- ✅ Published date
- ✅ Channel info (name, subscriber count)
- ❓ Video captions/subtitles
- ❓ Top comments

#### Instagram Posts
- ✅ Caption text
- ✅ Images/videos (URLs)
- ✅ Likes count
- ✅ Comments count
- ✅ Post date/time
- ✅ Author username, profile pic
- ❓ Hashtags extracted
- ❓ Comments content

**Question:** Include all ✅ items, or also ❓ optional items?

### Feature 3: UI Modal with Event Extraction 🎨
**Current:** Simple result cards with title, snippet, link  
**Required:** 
1. "View Details" button on each result card
2. Modal/popup showing full content
3. "Analyse" button in modal
4. LLM event extraction from full content
5. Display extracted event in modal

**Questions:**
- Should extracted events be saved to database?
- Same format as existing event scraping results?
- Allow editing before saving?

---

## 🏗️ Implementation Architecture

### Backend Components

#### 1. Settings Configuration
**File:** `backend/app/config.py`

```python
class Settings(BaseSettings):
    # Social Media APIs
    YOUTUBE_API_KEY: str = ""
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_ACCESS_TOKEN: str = ""
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_KEY_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    
    # Social Search Configuration
    MAX_SOCIAL_SEARCH_RESULTS: int = 10
    ENABLE_FULL_CONTENT_FETCH: bool = True
    CACHE_SOCIAL_CONTENT_HOURS: int = 24
```

#### 2. Content Services
**Files to create:**

##### `backend/app/services/facebook_content_service.py`
```python
class FacebookContentService:
    async def get_post_content(self, post_url: str) -> FacebookPost:
        """
        Extract post ID from URL
        Call Facebook Graph API
        Return full post content
        """
```

##### `backend/app/services/twitter_content_service.py`
```python
class TwitterContentService:
    async def get_tweet_content(self, tweet_url: str) -> Tweet:
        """
        Extract tweet ID from URL
        Call Twitter API v2
        Return full tweet content
        """
```

##### `backend/app/services/youtube_content_service.py`
```python
class YouTubeContentService:
    async def get_video_content(self, video_url: str) -> YouTubeVideo:
        """
        Extract video ID from URL
        Call YouTube Data API
        Return full video details
        """
```

##### `backend/app/services/instagram_content_service.py`
```python
class InstagramContentService:
    async def get_post_content(self, post_url: str) -> InstagramPost:
        """
        Extract media ID from URL
        Call Instagram Graph API
        Return full post content
        """
```

##### `backend/app/services/social_content_aggregator.py`
```python
class SocialContentAggregator:
    async def fetch_full_content(self, url: str, platform: str):
        """
        Route to appropriate service based on platform
        Handle errors and rate limits
        Cache results
        """
```

#### 3. Data Models
**File:** `backend/app/models.py`

```python
class SocialFullContent(BaseModel):
    url: str
    platform: str  # "facebook", "twitter", "youtube", "instagram"
    content_type: str  # "post", "tweet", "video"
    
    # Common fields
    text: Optional[str]
    author_name: str
    author_username: Optional[str]
    author_profile_pic: Optional[str]
    posted_at: datetime
    
    # Engagement metrics
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    
    # Media
    images: List[str] = []
    videos: List[str] = []
    thumbnails: List[str] = []
    
    # Platform-specific
    platform_data: Dict[str, Any] = {}
    
    # Extracted event (after LLM analysis)
    extracted_event: Optional[EventResult] = None
```

#### 4. API Endpoints
**File:** `backend/app/main.py`

```python
@app.post("/api/v1/social-content/fetch")
async def fetch_social_content(url: str, platform: str):
    """Fetch full content from social media URL"""
    
@app.post("/api/v1/social-content/analyse")
async def analyse_social_content(content: SocialFullContent):
    """Extract event from social media content using LLM"""
```

### Frontend Components

#### 1. Result Card Enhancement
**File:** `frontend/src/components/SocialResultsPanel.tsx`

```tsx
// Add button to each result card
<Button 
  variant="outlined" 
  size="small"
  onClick={() => handleViewDetails(result)}
>
  View Full Content
</Button>
```

#### 2. Content Modal Component
**File:** `frontend/src/components/SocialContentModal.tsx`

```tsx
interface SocialContentModalProps {
  open: boolean;
  onClose: () => void;
  url: string;
  platform: string;
}

// Displays:
// - Full text content
// - Images/videos
// - Engagement metrics
// - "Analyse" button
// - Extracted event (after analysis)
```

#### 3. API Integration
**File:** `frontend/src/services/api.ts`

```tsx
async fetchSocialContent(url: string, platform: string): Promise<SocialFullContent>
async analyseSocialContent(content: SocialFullContent): Promise<EventResult>
```

---

## 🔄 User Flow

### Current Flow (Google CSE Only)
```
User searches "APT threat" 
  ↓
Google CSE returns 10 results per platform
  ↓
Display cards with: Title, Snippet, URL, Thumbnail
  ↓
User clicks link → Opens in new tab
```

### New Flow (With Full Content)
```
User searches "APT threat"
  ↓
Google CSE returns 10 results per platform
  ↓
Display cards with: Title, Snippet, URL, Thumbnail
  ↓
User clicks "View Full Content" button
  ↓
Backend fetches full content from platform API
  ↓
Modal displays: Full text, images, videos, metrics
  ↓
User clicks "Analyse" button
  ↓
Backend sends content to Ollama LLM (qwen2.5:3b)
  ↓
LLM extracts event details
  ↓
Display event in modal: Title, Date, Location, Description
  ↓
User can save event to database
```

---

## ⚡ Performance Considerations

### Rate Limits (Free Tiers)

| Platform | Limit | Mitigation |
|----------|-------|------------|
| YouTube API | 10,000 quota/day | Cache results 24h |
| Facebook Graph API | 200 calls/hour | Queue requests |
| Twitter API v2 | 500,000 tweets/month | Cache aggressively |
| Instagram Graph API | 200 calls/hour | Limit to business needs |

### Caching Strategy
```python
# Cache full content for 24 hours
# Key: f"social_content:{platform}:{post_id}"
# Value: SocialFullContent JSON

redis.setex(
    f"social_content:{platform}:{post_id}",
    86400,  # 24 hours
    json.dumps(content)
)
```

### Error Handling
- **API Rate Limit:** Return cached content or error message
- **Invalid Token:** Log warning, return partial content
- **Network Error:** Retry 3 times with exponential backoff
- **Content Not Found:** Return 404 with helpful message

---

## 📝 TODO Checklist

### Phase 1: Setup & Configuration
- [x] Add all credentials to `.env`
- [ ] Generate Facebook Access Token
- [ ] Setup Instagram Business Account
- [ ] Generate Instagram Access Token
- [x] Add `MAX_SOCIAL_SEARCH_RESULTS` configuration
- [ ] Update `settings.py` to load new environment variables
- [ ] Test all API credentials

### Phase 2: Backend Services
- [ ] Create `facebook_content_service.py`
- [ ] Create `twitter_content_service.py`
- [ ] Create `youtube_content_service.py`
- [ ] Create `instagram_content_service.py`
- [ ] Create `social_content_aggregator.py`
- [ ] Add `SocialFullContent` model
- [ ] Create `/api/v1/social-content/fetch` endpoint
- [ ] Create `/api/v1/social-content/analyse` endpoint
- [ ] Implement caching layer
- [ ] Add error handling and logging

### Phase 3: LLM Integration
- [ ] Create prompt template for social content event extraction
- [ ] Integrate with existing Ollama service
- [ ] Parse LLM output into `EventResult` format
- [ ] Add validation for extracted events

### Phase 4: Frontend UI
- [ ] Add "View Full Content" button to result cards
- [ ] Create `SocialContentModal.tsx` component
- [ ] Implement loading states
- [ ] Add "Analyse" button functionality
- [ ] Display extracted event in modal
- [ ] Add "Save Event" functionality (optional)
- [ ] Update `api.ts` with new endpoints

### Phase 5: Testing & Refinement
- [ ] Test each platform API integration
- [ ] Test modal UI responsiveness
- [ ] Test LLM event extraction accuracy
- [ ] Test error scenarios (rate limits, invalid tokens)
- [ ] Add unit tests for services
- [ ] Performance testing with concurrent requests

---

## 🚀 Next Steps

**Immediate Actions Required:**

1. **Generate Facebook Access Token** (5 minutes)
   - https://developers.facebook.com/tools/explorer/
   - Add to `.env` as `FACEBOOK_ACCESS_TOKEN=`

2. **Setup Instagram Business Account** (10 minutes)
   - Convert to Business Account
   - Connect to Facebook Page
   - Generate Access Token
   - Add to `.env` as `INSTAGRAM_ACCESS_TOKEN=`

3. **Answer Clarification Questions:**
   - Which content fields to include (✅ or ✅+❓)?
   - Should extracted events be saved to database?
   - Any specific UI/UX preferences for the modal?

**Once clarifications received:**
- Begin Phase 2: Backend Services implementation
- Estimated time: 4-6 hours
- Will implement platform by platform, starting with easiest (YouTube)

---

## 📞 Questions to Answer

Please provide answers to these questions so I can proceed:

1. **Access Tokens:**
   - Can you generate Facebook Access Token? (Instructions above)
   - Can you setup Instagram Business Account and generate token?

2. **Content Scope:**
   - Include ALL fields (✅ + ❓) or just basics (✅ only)?
   - Need comments content or just counts?

3. **Event Extraction:**
   - Save extracted events to database automatically?
   - Allow user to edit before saving?
   - Same format/UI as regular scraping results?

4. **Configuration:**
   - OK with `.env` for `MAX_SOCIAL_SEARCH_RESULTS`?
   - Any other configurable parameters needed?

5. **UI/UX:**
   - Modal size preference (small, medium, large, fullscreen)?
   - Should modal be dismissible by clicking outside?
   - Display images in gallery or inline?

**Reply with answers and I'll start implementing immediately!** 🚀
