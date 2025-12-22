"""
Quick test script for social search API.
Run this after backend is started.
"""

import requests
import json

# Backend URL
BASE_URL = "http://localhost:8000"

# Test data
test_request = {
    "query": "cybersecurity breach",
    "sites": ["facebook.com", "x.com"],
    "results_per_site": 5
}

print("🧪 Testing Social Search API...\n")
print(f"📡 Sending request to: {BASE_URL}/api/v1/social-search")
print(f"📝 Request body: {json.dumps(test_request, indent=2)}\n")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/social-search",
        json=test_request,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"📝 Query: {data['query']}")
        print(f"🌐 Sites: {', '.join(data['sites'])}")
        print(f"📊 Total Results: {data['total_results']}")
        print(f"\n📋 Results Preview:")
        for i, result in enumerate(data['results'][:3], 1):
            print(f"\n  {i}. {result['title']}")
            print(f"     🔗 {result['link']}")
            print(f"     📄 {result['snippet'][:100]}...")
            print(f"     🏷️  Source: {result['source_site']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Error: Cannot connect to backend")
    print("   Make sure backend is running: python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Test complete!")
