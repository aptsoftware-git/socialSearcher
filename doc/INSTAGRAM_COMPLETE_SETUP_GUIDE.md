# Instagram API Setup - Complete Guide

**Date**: January 11, 2026  
**Issue**: Cannot fetch Instagram posts without Business Account  
**Status**: Setup required - Step-by-step guide below

---

## 🚨 **Current Issue**

**Error Message**:
```
Instagram API requires Business Account and media ID. 
Shortcode DRUMPGoketp cannot be directly queried without Business Account setup.
```

**Root Cause**:
- Instagram Graph API does **NOT** allow fetching public posts by shortcode
- Requires **Instagram Business Account** connected to **Facebook Page**
- Must use **Instagram Business Account ID** to query media
- Different from Facebook API (which is pending approval)

---

## 📋 **Prerequisites**

Before you can fetch Instagram posts, you need:

1. ✅ **Instagram Account** (Personal or Business)
2. ✅ **Facebook Page** (Can create new one)
3. ✅ **Facebook App** (Already created - pending review)
4. ⏳ **Facebook App Review Approval** (Required for access tokens)
5. ⏳ **Convert Instagram to Business Account**
6. ⏳ **Connect Instagram Business Account to Facebook Page**

---

## 🔧 **Step-by-Step Setup**

### **Phase 1: Wait for Facebook App Review** ⏳ CURRENT PHASE

**Status**: Your Facebook App is currently under review

**What to Wait For**:
- ✅ Approval for `pages_read_engagement` permission
- ✅ Approval for `pages_show_list` permission
- ✅ Approval for `instagram_basic` permission (if you requested it)

**Timeline**: 
- Typical review: 3-7 business days
- Can take up to 14 days

**While Waiting**:
- You can complete Phase 2-3 below
- Cannot test Instagram API until approval comes

**Check Status**:
1. Go to: https://developers.facebook.com/apps
2. Select your app
3. Go to "App Review" → "Requests"
4. Check approval status

---

### **Phase 2: Convert Instagram to Business Account** (Can do now)

**Option A: Convert Existing Personal Account** ⭐ RECOMMENDED

**Steps**:

1. **Open Instagram Mobile App**:
   - Must use mobile app (cannot do from desktop)
   - iOS or Android

2. **Go to Profile**:
   - Tap profile icon (bottom right)
   - Tap menu (☰ three lines, top right)

3. **Access Settings**:
   - Tap "Settings and privacy"
   - Scroll down to "Account type and tools"

4. **Switch to Professional Account**:
   - Tap "Switch to professional account"
   - Choose account type:
     - **Business** (recommended for API access)
     - Creator (also works, but Business is better)

5. **Choose Category**:
   - Select a category that fits your content
   - Examples: "News & Media", "Public Figure", "Brand", etc.

6. **Review Business Tools**:
   - Enable contact options (Email, Phone - optional)
   - Skip Facebook Page connection for now (we'll do this next)

7. **Complete Setup**:
   - Tap "Done"
   - Your account is now a Business Account ✅

**Option B: Create New Instagram Business Account**

If you prefer a separate account for testing:

1. **Create New Instagram Account**:
   - Use different email
   - Complete basic profile setup

2. **Immediately Convert to Business**:
   - Follow steps above to switch to professional

---

### **Phase 3: Create or Connect Facebook Page** (Can do now)

Instagram Business Accounts must be linked to a Facebook Page.

**Option A: Create New Facebook Page** ⭐ EASIEST

**Steps**:

1. **Go to Facebook**:
   - Visit: https://www.facebook.com/pages/create
   - Or go to facebook.com → Menu → Pages → Create New Page

2. **Create Page**:
   - **Page name**: Choose a name (e.g., "My Social Analyzer")
   - **Category**: Select relevant category (e.g., "App Page", "News & Media")
   - **Description**: Brief description (optional)
   - Tap "Create Page"

3. **Complete Basic Setup**:
   - Add profile picture (optional)
   - Add cover photo (optional)
   - Skip "Invite friends" if you prefer

4. **Page Created** ✅
   - You now have a Facebook Page
   - You're automatically the Page admin

**Option B: Use Existing Facebook Page**

If you already have a Facebook Page:
- Make sure you're the **Admin** of the page
- Check: Go to Page → Settings → Page roles → You should see "Admin"

---

### **Phase 4: Connect Instagram to Facebook Page** (Can do now)

**Steps**:

1. **Open Instagram Mobile App**:
   - Go to your Business Account profile
   - Tap menu (☰ three lines, top right)

2. **Go to Settings**:
   - Tap "Settings and privacy"
   - Under "For professionals", tap "Account type and tools"

3. **Connect to Facebook Page**:
   - Tap "Connect Facebook Page"
   - OR: Settings → Business → Page
   - Choose the Facebook Page you created

4. **Authorize Connection**:
   - If prompted, log into Facebook
   - Authorize Instagram to access your Facebook Page
   - Select the specific page to connect

5. **Verify Connection** ✅:
   - Go back to Instagram profile
   - Tap "Edit profile"
   - You should see "Page" section with linked Facebook Page
   - Connection successful!

---

### **Phase 5: Get Instagram Business Account ID** (After App Review Approval)

⏳ **WAIT FOR FACEBOOK APP REVIEW APPROVAL BEFORE THIS STEP**

Once your Facebook App is approved, you can get your Instagram Business Account ID.

**Method 1: Using Facebook Graph API Explorer** ⭐ EASIEST

**Steps**:

1. **Go to Graph API Explorer**:
   - Visit: https://developers.facebook.com/tools/explorer/

2. **Select Your App**:
   - Top right: Select your Facebook App from dropdown
   - Click "Generate Access Token"
   - Select permissions:
     - `pages_read_engagement`
     - `instagram_basic`
     - `pages_show_list`
   - Click "Generate Token"
   - Grant permissions

3. **Get Facebook Page ID**:
   - In the query box, enter: `/me/accounts`
   - Click "Submit"
   - Response will show your Facebook Pages:
     ```json
     {
       "data": [
         {
           "id": "123456789012345",  // ← This is your Page ID
           "name": "My Social Analyzer",
           "access_token": "EAAxxxxxx..."  // ← Page Access Token
         }
       ]
     }
     ```
   - **Copy the Page ID** (e.g., `123456789012345`)
   - **Copy the Page Access Token** (e.g., `EAAxxxxxx...`)

4. **Get Instagram Business Account ID**:
   - In query box, enter: `/YOUR_PAGE_ID?fields=instagram_business_account`
   - Example: `/123456789012345?fields=instagram_business_account`
   - Click "Submit"
   - Response:
     ```json
     {
       "instagram_business_account": {
         "id": "17841400000000000"  // ← This is your Instagram Business Account ID!
       },
       "id": "123456789012345"
     }
     ```
   - **Copy the Instagram Business Account ID** (e.g., `17841400000000000`)

**Method 2: Using cURL Command**

If you prefer command line:

```bash
# Step 1: Get your Facebook Pages
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_USER_ACCESS_TOKEN"

# Step 2: Get Instagram Business Account ID
curl -X GET "https://graph.facebook.com/v18.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_PAGE_ACCESS_TOKEN"
```

**Method 3: Using Python Script**

We can create a helper script for you (see below).

---

### **Phase 6: Configure Application** (After getting IDs)

Once you have:
- ✅ Facebook Page Access Token
- ✅ Instagram Business Account ID

**Update `.env` file**:

```properties
# Instagram Configuration
INSTAGRAM_ACCESS_TOKEN=YOUR_PAGE_ACCESS_TOKEN_HERE
INSTAGRAM_BUSINESS_ACCOUNT_ID=YOUR_IG_BUSINESS_ACCOUNT_ID_HERE

# Example:
# INSTAGRAM_ACCESS_TOKEN=EAAdeQ76R3WEBxxxxxxxxxxxxxxxxxxxx
# INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400000000000
```

**Note**: The `INSTAGRAM_ACCESS_TOKEN` should be your **Page Access Token**, not your user token!

---

### **Phase 7: Update Code** (After configuration)

The Instagram service needs to be updated to use Business Account ID.

**Current limitation**:
```python
# Current code tries to use shortcode (doesn't work)
shortcode = "DRUMPGoketp"  # From URL
# ❌ Cannot query by shortcode without Business Account
```

**Required approach**:
```python
# Must use Business Account ID
business_account_id = "17841400000000000"
# Get recent media
GET /{business_account_id}/media

# Then filter by timestamp or other criteria
```

**I can help update the code once you complete the setup!**

---

## 🔍 **Testing Your Setup**

### **Test 1: Verify Business Account Connection**

**Using Graph API Explorer**:

```
Query: /me/accounts?fields=instagram_business_account,name
Access Token: Your User Access Token
Expected: Should show your Page with instagram_business_account field
```

**Expected Response**:
```json
{
  "data": [
    {
      "instagram_business_account": {
        "id": "17841400000000000"
      },
      "name": "My Social Analyzer",
      "id": "123456789012345"
    }
  ]
}
```

### **Test 2: Fetch Instagram Media**

**Using Graph API Explorer**:

```
Query: /{YOUR_IG_BUSINESS_ACCOUNT_ID}/media?fields=id,caption,media_type,media_url,permalink,timestamp
Access Token: Your Page Access Token
Expected: Should return list of your recent posts
```

**Expected Response**:
```json
{
  "data": [
    {
      "id": "18027xxxxxxxxx",
      "caption": "Your post caption",
      "media_type": "IMAGE",
      "media_url": "https://scontent.cdninstagram.com/...",
      "permalink": "https://www.instagram.com/p/DRUMPGoketp/",
      "timestamp": "2026-01-10T12:00:00+0000"
    }
  ]
}
```

### **Test 3: Fetch Specific Post**

**Using Graph API Explorer**:

```
Query: /{MEDIA_ID}?fields=id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count
Access Token: Your Page Access Token
Expected: Should return details of specific post
```

---

## ⚠️ **Important Limitations**

### **What You CAN Do** (After Setup):

✅ Fetch posts from **YOUR** Instagram Business Account  
✅ Get media IDs, captions, images, videos  
✅ Get engagement metrics (likes, comments counts)  
✅ Get timestamp and permalink  
✅ Access your own account's content

### **What You CANNOT Do**:

❌ Fetch posts from **OTHER** Instagram accounts (even public ones)  
❌ Search Instagram globally (like YouTube search)  
❌ Get content from personal (non-business) accounts  
❌ Get detailed user info from random accounts  
❌ Get comments content (only count)  

**Why?** Instagram API is very restrictive:
- Protects user privacy
- Prevents scraping
- Only allows access to your own Business Account content

---

## 🎯 **Use Cases**

### **What This Setup Enables**:

**Your Own Instagram Business Account**:
```
✅ Monitor your own posts
✅ Get engagement stats for your posts
✅ Track your content performance
✅ Embed your Instagram posts in your app
✅ Show your Instagram feed on your website
```

**Typical workflow**:
1. You post content on Instagram
2. Your app fetches the post using Business Account ID
3. App displays your Instagram content alongside YouTube, Facebook, etc.

### **What This Does NOT Enable**:

**Random Public Accounts**:
```
❌ Cannot fetch posts from: https://www.instagram.com/p/DRUMPGoketp/
   (unless DRUMPGoketp is posted by YOUR business account)

❌ Cannot search: "Find all Instagram posts about Sydney"
❌ Cannot browse: Other users' profiles
❌ Cannot scrape: Public Instagram content
```

**Why the current error?**
- The URL `https://www.instagram.com/p/DRUMPGoketp/` is probably from **someone else's account**
- Instagram API only allows accessing **your own** Business Account posts
- This is by design - Instagram protects user content

---

## 💡 **Alternative Approaches**

Since Instagram API is so restrictive, here are alternatives:

### **Option 1: Focus on Your Own Instagram Content** ⭐ RECOMMENDED

**Use Case**: 
- You have an Instagram Business Account
- You want to display/analyze your own posts
- Good for: Portfolio, news agency, brand monitoring

**Setup**: Follow all steps above

**Benefit**: Official API, legal, reliable

### **Option 2: Use Instagram Embed** (For Display Only)

**Use Case**:
- Just want to display Instagram posts in your app
- Don't need detailed metadata

**Implementation**:
```html
<!-- Instagram's official embed code -->
<blockquote class="instagram-media" data-instgrm-permalink="https://www.instagram.com/p/DRUMPGoketp/">
</blockquote>
<script async src="//www.instagram.com/embed.js"></script>
```

**Benefit**: No API needed, works for any public post

**Limitation**: Just visual embed, no data extraction

### **Option 3: Manual Entry** (For Specific Posts)

**Use Case**:
- Only need occasional Instagram posts
- Can manually add content

**Implementation**:
- User provides Instagram URL
- You manually review the post
- Enter caption, image URL, engagement stats manually
- Store in database

**Benefit**: No API restrictions

**Limitation**: Manual work, not scalable

### **Option 4: Focus on Other Platforms**

**Recommendation**: 
Since Instagram API is so limited, focus on platforms with better access:

| Platform | Public Content Access | FREE Tier | Status |
|----------|----------------------|-----------|---------|
| **YouTube** | ✅ Excellent | 10,000 quota/day | ✅ Working |
| **Facebook** | ⏳ Good (after approval) | Pages/Groups | ⏳ Pending |
| **Twitter** | ⚠️ Limited | 1 req/15min | ⚠️ Very limited |
| **Instagram** | ❌ Very restricted | Own account only | ❌ Requires setup |

**Strategic Recommendation**:
- ✅ **Primary**: YouTube (unlimited, working perfectly)
- ⏳ **Secondary**: Facebook (pending approval, will work well)
- ⚠️ **Tertiary**: Twitter (limited but works)
- ❌ **Optional**: Instagram (only for your own content)

---

## 🚀 **Quick Start Checklist**

### **NOW** (Can do immediately):

- [ ] **Convert Instagram to Business Account** (5 min)
  - Use mobile app
  - Switch to Professional → Business

- [ ] **Create Facebook Page** (5 min)
  - https://www.facebook.com/pages/create
  - Choose name and category

- [ ] **Connect Instagram to Facebook Page** (5 min)
  - Instagram app → Settings → Connect to Facebook Page
  - Select your page

### **AFTER Facebook App Review Approval** (⏳ Waiting):

- [ ] **Generate Access Tokens**
  - Graph API Explorer
  - Request `pages_read_engagement`, `instagram_basic` permissions

- [ ] **Get Instagram Business Account ID**
  - Use Graph API Explorer
  - Query: `/YOUR_PAGE_ID?fields=instagram_business_account`

- [ ] **Configure `.env`**
  - Add `INSTAGRAM_ACCESS_TOKEN`
  - Add `INSTAGRAM_BUSINESS_ACCOUNT_ID`

- [ ] **Update Code** (I can help with this)
  - Modify `instagram_content_service.py`
  - Use Business Account endpoint

- [ ] **Test Instagram Fetching**
  - Try fetching your own posts
  - Verify engagement data

---

## 📚 **Resources**

### **Official Documentation**:
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api
- Instagram Basic Display API: https://developers.facebook.com/docs/instagram-basic-display-api
- Graph API Explorer: https://developers.facebook.com/tools/explorer/

### **Setup Guides**:
- Convert to Business: https://help.instagram.com/502981923235522
- Connect to Facebook Page: https://help.instagram.com/399237934150902
- Instagram API Quickstart: https://developers.facebook.com/docs/instagram-api/getting-started

### **Important Notes**:
- **Instagram Graph API** (for businesses) vs **Instagram Basic Display API** (for personal)
- We need **Instagram Graph API** (requires Business Account)
- Basic Display API is limited to profile info only

---

## ❓ **FAQ**

### **Q: Can I fetch posts from other Instagram accounts?**
**A**: ❌ No. Instagram API only allows accessing **your own** Business Account posts. You cannot fetch posts from random public accounts.

### **Q: Why is Instagram so restrictive compared to YouTube?**
**A**: Privacy and anti-scraping. Instagram prioritizes user privacy and prevents automated data collection. YouTube is more open because it's a public content platform.

### **Q: Do I need Instagram Business Account?**
**A**: ✅ Yes. Personal accounts cannot use Instagram Graph API. You must convert to Business or Creator account.

### **Q: Can I use someone else's Facebook Page?**
**A**: ⚠️ Only if you're the admin. You must have admin access to the Facebook Page that's connected to the Instagram Business Account.

### **Q: What if I don't want to use Instagram API?**
**A**: You can:
1. Use Instagram Embed (display only)
2. Manual entry (for specific posts)
3. Focus on YouTube/Facebook (better API access)
4. Disable Instagram feature

### **Q: When will Facebook App Review be approved?**
**A**: Typically 3-7 business days, can take up to 14 days. Check status in Facebook App Dashboard.

### **Q: Do I need to pay for Instagram API?**
**A**: ❌ No. Instagram Graph API is free, but:
- Requires Business Account (free)
- Requires Facebook Page (free)
- Requires App Review approval (free, just time)

---

## 🎯 **Recommended Next Steps**

### **For Your Situation**:

Given the current error with `https://www.instagram.com/p/DRUMPGoketp/`:

**Option A: If That's Your Own Post**:
1. ✅ Complete Instagram Business Account setup (above)
2. ⏳ Wait for Facebook App Review approval
3. ✅ Configure Instagram Business Account ID in `.env`
4. ✅ Update code to fetch using Business Account endpoint
5. ✅ You'll be able to fetch your own posts

**Option B: If That's Someone Else's Post** ⭐ RECOMMENDED:
1. ❌ **You cannot fetch it via Instagram API** (API limitation)
2. ✅ **Focus on platforms with better access**:
   - YouTube: Works perfectly, unlimited
   - Facebook: Pending approval, will work for pages/groups
   - Twitter: Works but very limited (1 req/15min)
3. ✅ **For Instagram**: Only use for your own Business Account posts
4. ✅ **Alternative**: Use Instagram Embed for display purposes

**Option C: Disable Instagram for Now**:
1. Comment out Instagram in `config/sources.yaml`
2. Focus on YouTube (working perfectly)
3. Re-enable Instagram after:
   - Facebook App Review approval
   - Business Account setup complete
   - Understanding limitations (own content only)

---

## ✅ **Summary**

**Current Status**:
- ❌ Instagram API not configured
- ⏳ Facebook App Review pending (required for tokens)
- ❌ Instagram Business Account not connected (maybe?)

**What You Need**:
1. ✅ Instagram Business Account (can set up now)
2. ✅ Facebook Page (can create now)
3. ✅ Connect Instagram to Page (can do now)
4. ⏳ Facebook App Review approval (waiting)
5. ⏳ Get Instagram Business Account ID (after approval)
6. ⏳ Configure `.env` with tokens and IDs (after approval)

**Reality Check**:
- Instagram API only works for **YOUR** Business Account posts
- Cannot fetch random public Instagram posts
- If you need to analyze other accounts' posts → Instagram API won't help
- **Recommendation**: Focus on YouTube (unlimited) + Facebook (pending, will be good)

**Timeline**:
- Setup (Phase 2-4): 30 minutes (can do today)
- App Review: 3-14 days (waiting)
- Configuration: 30 minutes (after approval)
- **Total**: ~2-3 weeks until Instagram fully working

---

**Need Help?** Let me know:
1. Is the post you're trying to fetch from YOUR Instagram account or someone else's?
2. Do you have an Instagram Business Account already?
3. Do you have a Facebook Page already?
4. Has your Facebook App Review been approved yet?

I can help with the next steps based on your current status! 🚀
