"""
Test script to verify CORS headers are being sent correctly
"""
import requests

# Test CORS
url = "http://182.73.137.36:8000/api/v1/llm/usage"
headers = {
    "Origin": "http://182.73.137.36:5173"
}

print(f"Testing CORS for: {url}")
print(f"Origin: {headers['Origin']}")
print("-" * 60)

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    # Check for CORS headers
    print("\n" + "="  * 60)
    if "access-control-allow-origin" in response.headers:
        print(f"✓ CORS Header Present: {response.headers['access-control-allow-origin']}")
    else:
        print("✗ CORS Header MISSING!")
        print("\nThis means the backend is not sending the Access-Control-Allow-Origin header.")
        print("The CORS middleware might not be working correctly.")
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Cannot connect to backend server!")
    print("Make sure the backend is running on http://182.73.137.36:8000")
except Exception as e:
    print(f"✗ ERROR: {e}")
