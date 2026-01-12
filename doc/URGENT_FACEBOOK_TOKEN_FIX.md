# 🔴 URGENT: Facebook Token Expired

**Date:** January 5, 2026  
**Issue:** Facebook Access Token expired on January 2, 2026  
**Impact:** "View Full Content" button fails for Facebook posts  
**Priority:** 🔥 **HIGH** - Immediate action required  

---

## 📋 Quick Summary

Your Facebook Access Token expired on **Friday, January 2, 2026 at 08:00:00 PST**.

**Current Status:**
- ❌ Facebook API: **Not Working**
- ✅ YouTube API: **Working**
- ✅ Twitter/X API: **Working**
- ⚠️ Instagram API: **Not Set Up** (requires Business Account)

**What's Broken:**
- Clicking "View Full Content" on Facebook posts shows error
- Console logs show: `"Session has expired"`

**What Still Works:**
- YouTube "View Full Content" ✅
- Twitter "View Full Content" ✅
- Google social media search ✅
- Event extraction/analysis ✅

---

## ⚡ Quick Fix (5 Minutes)

### Option A: Automated Script (Recommended)

**After you generate the new token**, run this script:

```powershell
# From project root directory
.\update_facebook_token.ps1 -NewToken "YOUR_NEW_TOKEN_HERE"
```

The script will:
1. ✅ Backup your current .env file
2. ✅ Update FACEBOOK_ACCESS_TOKEN
3. ✅ Offer to restart backend
4. ✅ Done!

### Option B: Manual Update

1. **Generate new token** (see detailed instructions below)
2. **Open:** `backend\.env`
3. **Find line 36:**
   ```env
   FACEBOOK_ACCESS_TOKEN=EAAdeQ76R3WEBQc2goSL...
   ```
4. **Replace with new token**
5. **Save file**
6. **Restart backend:**
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload
   ```

---

## 📚 Detailed Instructions

### Step 1: Generate Short-Lived Token

**I've already opened the Facebook Graph API Explorer for you in the Simple Browser.**

If you need to open it again:
- URL: https://developers.facebook.com/tools/explorer/

**Instructions:**
1. Select your app from dropdown
2. Click "Get Token" → "Get User Access Token"
3. Check these permissions:
   - ✅ pages_read_engagement
   - ✅ pages_show_list
   - ✅ pages_read_user_content
4. Click "Generate Access Token"
5. Copy the token that appears

### Step 2: Extend to Long-Lived Token

**I've also opened the Access Token Debugger for you in the Simple Browser.**

If you need to open it again:
- URL: https://developers.facebook.com/tools/debug/accesstoken/

**Instructions:**
1. Paste the short-lived token
2. Click "Debug"
3. Click "Extend Access Token" at the bottom
4. Copy the new **long-lived token** (60 days validity)

### Step 3: Update Configuration

**Using the automated script (easier):**
```powershell
.\update_facebook_token.ps1 -NewToken "PASTE_YOUR_LONG_LIVED_TOKEN_HERE"
```

**Or manually:**
1. Open `backend\.env`
2. Update line 36 with new token
3. Save and restart backend

---

## 🧪 Test the Fix

After updating the token and restarting backend:

1. **Open:** http://localhost:5173
2. **Search:** Any query (e.g., "APT attack")
3. **Go to Facebook tab**
4. **Click "View Full Content"** on any post
5. **Expected:** Modal opens with full Facebook post content ✅

**Success Indicators:**
- ✅ Modal opens within 2-5 seconds
- ✅ Full post text visible
- ✅ Author name and profile picture
- ✅ Images/videos displayed
- ✅ Reactions, comments, shares count visible
- ✅ No "Session expired" error in console

---

## 📅 Set a Reminder

**New Token Expires:** ~60 days from generation date

**Mark your calendar:**
- **Generate new token:** Early March 2026
- **Set reminder:** 5 days before expiration

**Calendar Entry:**
```
Title: Regenerate Facebook Access Token
Date: March 1, 2026
Reminder: 5 days before
Description: Follow instructions in doc/FACEBOOK_TOKEN_EXPIRED_FIX.md
```

---

## 🔍 Error Details (For Reference)

**From Console Log:**
```
2026-01-05 12:58:49 | ERROR | app.services.facebook_content_service:get_post_content:171 - HTTP error fetching Facebook post 1395524588603953: 400

2026-01-05 12:58:49 | ERROR | app.services.facebook_content_service:get_post_content:172 - Response: {"error":{"message":"Error validating access token: Session has expired on Friday, 02-Jan-26 08:00:00 PST. The current time is Sunday, 04-Jan-26 23:28:51 PST.","type":"OAuthException","code":190,...
```

**Error Breakdown:**
- **Error Code:** 190 (OAuthException)
- **Message:** Session expired on January 2, 2026
- **Cause:** Facebook tokens expire after 60 days
- **Solution:** Generate new token

---

## 📖 Documentation Created

I've created comprehensive documentation for you:

1. **`FACEBOOK_TOKEN_EXPIRED_FIX.md`** - Complete fix guide with screenshots
2. **`update_facebook_token.ps1`** - Automated update script
3. **`URGENT_FACEBOOK_TOKEN_FIX.md`** - This summary (quick reference)

**Locations:**
```
doc/FACEBOOK_TOKEN_EXPIRED_FIX.md
update_facebook_token.ps1
doc/URGENT_FACEBOOK_TOKEN_FIX.md
```

---

## 🔄 Token Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                 Facebook Token Timeline                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Nov 3, 2025        Jan 2, 2026         Mar 5, 2026    │
│       │                  │                   │          │
│   Generated         Expired          Next Renewal       │
│       │                  │                   │          │
│       ├──────60 days─────┤                   │          │
│                                                         │
│       └─────────────────────────120 days─────┘          │
│                   (If renewed today)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘

Current Status: ❌ Expired (Jan 2, 2026)
Action Needed: ⚠️ Generate new token NOW
New Expiry: ✅ ~March 5, 2026 (60 days)
```

---

## ❓ FAQ

### Q: Why did the token expire?
**A:** Facebook tokens expire after 60 days for security. This is standard behavior.

### Q: Can I make it never expire?
**A:** Yes, by converting to a **Page Access Token** (requires linking to Facebook Page). This is more complex but tokens never expire.

### Q: How often do I need to do this?
**A:** Every 60 days, unless you use Page Access Tokens.

### Q: Will this affect other platforms?
**A:** No, YouTube and Twitter tokens are separate and still working fine.

### Q: What if I can't generate a new token?
**A:** Check:
1. You're logged into the correct Facebook account
2. Your app is in your apps list at developers.facebook.com
3. Your Facebook account has access to the app

---

## 🚨 Immediate Actions

### Priority 1 (Now - 5 minutes):
- [ ] Generate new Facebook token (see instructions above)
- [ ] Run update script or manually update .env
- [ ] Restart backend server
- [ ] Test Facebook "View Full Content" button

### Priority 2 (Next 10 minutes):
- [ ] Verify token works on multiple Facebook posts
- [ ] Check token expiration date in debugger
- [ ] Set calendar reminder for March 2026

### Priority 3 (Optional - Later):
- [ ] Consider switching to Page Access Token (never expires)
- [ ] Add token expiration monitoring to backend
- [ ] Document token refresh process for team

---

## 📞 Support Resources

### Facebook Developer Tools:
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **Token Debugger:** https://developers.facebook.com/tools/debug/accesstoken/
- **App Dashboard:** https://developers.facebook.com/apps/

### Documentation:
- **Local Docs:** `doc/FACEBOOK_TOKEN_EXPIRED_FIX.md`
- **Update Script:** `update_facebook_token.ps1`
- **Backend Config:** `backend/.env` (line 36)

### Console Commands:
```powershell
# Update token (automated)
.\update_facebook_token.ps1 -NewToken "YOUR_TOKEN"

# Restart backend
cd backend
python -m uvicorn app.main:app --reload

# Check token expiration
# Visit: https://developers.facebook.com/tools/debug/accesstoken/
```

---

## ✅ Success Checklist

After fixing, verify these:

- [ ] Backend starts without errors
- [ ] No "Session expired" errors in logs
- [ ] Facebook "View Full Content" button works
- [ ] Modal shows full post content
- [ ] Images/videos display correctly
- [ ] Engagement metrics visible (likes, comments, shares)
- [ ] "Analyse with AI" button works on Facebook posts
- [ ] Token expiration date is ~60 days from now

---

## 🎯 Current Status Summary

| Platform | API Status | "View Full Content" | Issue | Action |
|----------|-----------|---------------------|-------|--------|
| **Facebook** | ❌ Expired | ❌ Broken | Token expired Jan 2 | 🔥 **FIX NOW** |
| YouTube | ✅ Working | ✅ Working | None | ✅ OK |
| Twitter/X | ✅ Working | ✅ Working | None | ✅ OK |
| Instagram | ⚠️ Not Setup | ⚠️ Not Setup | Business Account needed | ⏳ Later |

---

**Priority:** 🔥 **URGENT - Fix Required**  
**Estimated Time:** 5 minutes  
**Difficulty:** Easy  
**Impact:** High (Facebook feature completely broken)  

**Status:** ⚠️ **WAITING FOR YOUR ACTION**

---

**Last Updated:** January 5, 2026  
**Created By:** GitHub Copilot  
**Documentation:** Complete ✅
