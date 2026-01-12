"""
Instagram Business Account ID Finder

This script helps you get your Instagram Business Account ID after:
1. Converting Instagram to Business Account
2. Connecting Instagram to Facebook Page  
3. Getting Facebook App Review approval

Usage:
    python get_instagram_id.py

Requirements:
    - Facebook App approved with pages_read_engagement and instagram_basic permissions
    - User Access Token from Graph API Explorer
"""

import httpx
import json
from typing import Optional, Dict, Any


def get_instagram_business_account_id(user_access_token: str) -> Optional[Dict[str, Any]]:
    """
    Get Instagram Business Account ID using Facebook Graph API.
    
    Args:
        user_access_token: User access token from Graph API Explorer
        
    Returns:
        Dictionary with Page ID, Page Access Token, and Instagram Business Account ID
    """
    base_url = "https://graph.facebook.com/v18.0"
    
    try:
        print("🔍 Step 1: Getting your Facebook Pages...")
        print("-" * 60)
        
        # Step 1: Get user's Facebook Pages
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{base_url}/me/accounts",
                params={
                    "access_token": user_access_token,
                    "fields": "id,name,access_token"
                }
            )
            response.raise_for_status()
            pages_data = response.json()
        
        if "data" not in pages_data or not pages_data["data"]:
            print("❌ No Facebook Pages found.")
            print("   Create a page at: https://www.facebook.com/pages/create")
            return None
        
        print(f"✅ Found {len(pages_data['data'])} Facebook Page(s):\n")
        
        results = []
        
        for idx, page in enumerate(pages_data["data"], 1):
            page_id = page["id"]
            page_name = page["name"]
            page_access_token = page["access_token"]
            
            print(f"📄 Page {idx}: {page_name}")
            print(f"   Page ID: {page_id}")
            
            # Step 2: Get Instagram Business Account for this page
            print(f"   🔍 Checking for connected Instagram account...")
            
            response = client.get(
                f"{base_url}/{page_id}",
                params={
                    "fields": "instagram_business_account",
                    "access_token": page_access_token
                }
            )
            response.raise_for_status()
            ig_data = response.json()
            
            if "instagram_business_account" in ig_data:
                ig_account_id = ig_data["instagram_business_account"]["id"]
                print(f"   ✅ Instagram Business Account ID: {ig_account_id}")
                
                # Get Instagram username
                response = client.get(
                    f"{base_url}/{ig_account_id}",
                    params={
                        "fields": "username,name,profile_picture_url",
                        "access_token": page_access_token
                    }
                )
                response.raise_for_status()
                ig_profile = response.json()
                
                print(f"   📱 Instagram Username: @{ig_profile.get('username', 'unknown')}")
                print(f"   👤 Instagram Name: {ig_profile.get('name', 'unknown')}")
                
                results.append({
                    "page_id": page_id,
                    "page_name": page_name,
                    "page_access_token": page_access_token,
                    "instagram_business_account_id": ig_account_id,
                    "instagram_username": ig_profile.get('username'),
                    "instagram_name": ig_profile.get('name')
                })
            else:
                print(f"   ⚠️ No Instagram account connected to this page")
                print(f"   → Connect at: https://www.instagram.com/ (Settings → Connected Accounts)")
            
            print()
        
        if not results:
            print("❌ No Instagram Business Accounts found.")
            print("\n📋 Next Steps:")
            print("   1. Convert Instagram account to Business Account")
            print("   2. Connect Instagram to your Facebook Page")
            print("   3. Run this script again")
            print("\n   See: doc/INSTAGRAM_COMPLETE_SETUP_GUIDE.md")
            return None
        
        print("=" * 60)
        print("✅ SUCCESS! Instagram Business Account(s) Found")
        print("=" * 60)
        print()
        
        for idx, result in enumerate(results, 1):
            print(f"Configuration {idx}:")
            print(f"  Instagram Username: @{result['instagram_username']}")
            print(f"  Instagram Business Account ID: {result['instagram_business_account_id']}")
            print(f"  Page Access Token: {result['page_access_token'][:50]}...")
            print()
        
        print("=" * 60)
        print("📝 Add to your .env file:")
        print("=" * 60)
        print()
        
        # Show config for first Instagram account found
        first = results[0]
        print(f"INSTAGRAM_ACCESS_TOKEN={first['page_access_token']}")
        print(f"INSTAGRAM_BUSINESS_ACCOUNT_ID={first['instagram_business_account_id']}")
        print()
        
        if len(results) > 1:
            print("⚠️  Note: Multiple Instagram accounts found. Using the first one above.")
            print("   If you want to use a different account, copy its tokens instead.")
            print()
        
        return results
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        
        if e.response.status_code == 400:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            print(f"\n   Error Message: {error_message}")
            
            if "token" in error_message.lower():
                print("\n   💡 Token issue detected:")
                print("      1. Go to: https://developers.facebook.com/tools/explorer/")
                print("      2. Select your app")
                print("      3. Click 'Generate Access Token'")
                print("      4. Select permissions: pages_read_engagement, instagram_basic")
                print("      5. Copy the new token and run this script again")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function."""
    print("=" * 60)
    print("Instagram Business Account ID Finder")
    print("=" * 60)
    print()
    
    print("📋 Prerequisites:")
    print("   1. ✅ Instagram converted to Business Account")
    print("   2. ✅ Instagram connected to Facebook Page")
    print("   3. ✅ Facebook App Review approved")
    print("   4. ⏳ User Access Token from Graph API Explorer")
    print()
    
    print("🔗 Get User Access Token:")
    print("   1. Go to: https://developers.facebook.com/tools/explorer/")
    print("   2. Select your app (top right dropdown)")
    print("   3. Click 'Generate Access Token'")
    print("   4. Select permissions:")
    print("      - pages_read_engagement")
    print("      - pages_show_list")
    print("      - instagram_basic")
    print("   5. Click 'Generate Token'")
    print("   6. Copy the token (starts with 'EAAxxxxxx...')")
    print()
    print("=" * 60)
    print()
    
    # Get token from user
    user_access_token = input("Paste your User Access Token here: ").strip()
    
    if not user_access_token:
        print("❌ No token provided. Exiting.")
        return
    
    if not user_access_token.startswith("EAA"):
        print("⚠️  Warning: Token doesn't start with 'EAA'. This might not be a valid token.")
        proceed = input("   Continue anyway? (y/n): ").strip().lower()
        if proceed != "y":
            print("Exiting.")
            return
    
    print()
    print("=" * 60)
    
    # Get Instagram Business Account ID
    results = get_instagram_business_account_id(user_access_token)
    
    if results:
        print("=" * 60)
        print("✅ Configuration Complete!")
        print("=" * 60)
        print()
        print("📋 Next Steps:")
        print("   1. Copy the INSTAGRAM_* variables above")
        print("   2. Paste them into your .env file")
        print("   3. Restart the backend:")
        print("      cd backend")
        print("      python -m uvicorn app.main:app --reload")
        print("   4. Test Instagram fetching with your own posts")
        print()
        print("⚠️  Remember: Instagram API only works with YOUR business account posts!")
        print()
    else:
        print("=" * 60)
        print("❌ Setup Incomplete")
        print("=" * 60)
        print()
        print("📋 See: doc/INSTAGRAM_COMPLETE_SETUP_GUIDE.md for detailed steps")
        print()


if __name__ == "__main__":
    main()
