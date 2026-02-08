#!/bin/bash

# Test Authentication Endpoints
# This script tests the newly implemented authentication system

BASE_URL="http://localhost:8000"

echo "========================================="
echo "Testing Social Searcher Authentication"
echo "========================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Login with default admin
echo "2. Testing Admin Login..."
echo "   Email: admin@aptsoftware.in"
echo "   Password: Admin@123"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@aptsoftware.in",
    "password": "Admin@123",
    "remember_me": true
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed! Cannot proceed with tests."
  echo "Please check if:"
  echo "  1. Backend container is running"
  echo "  2. Database has default admin user"
  echo "  3. Authentication endpoints are loaded"
  exit 1
fi

echo "✅ Login successful! Token received."
echo ""
echo ""

# Test 3: Get current user info
echo "3. Testing 'Get Current User' endpoint..."
curl -s "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# Test 4: Get all users (admin only)
echo "4. Testing 'Get All Users' endpoint (Admin only)..."
curl -s "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# Test 5: Get usage (should be 0 for new user)
echo "5. Testing 'Get My Usage' endpoint..."
curl -s "$BASE_URL/api/v1/auth/my-usage" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# Test 6: Create a test user
echo "6. Testing 'Create User' endpoint..."
CREATE_USER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "Test@1234",
    "full_name": "Test User",
    "is_admin": false
  }')

echo "$CREATE_USER_RESPONSE" | python3 -m json.tool
echo ""

# Extract user ID
USER_ID=$(echo "$CREATE_USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$USER_ID" ]; then
  echo "✅ Test user created with ID: $USER_ID"
  echo ""
  echo ""
  
  # Test 7: Get user usage report
  echo "7. Testing 'Get User Usage Report' endpoint..."
  CURRENT_YEAR=$(date +%Y)
  CURRENT_MONTH=$(date +%-m)
  
  curl -s -X POST "$BASE_URL/api/v1/users/usage-report" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"user_id\": $USER_ID,
      \"year\": $CURRENT_YEAR,
      \"month\": $CURRENT_MONTH
    }" | python3 -m json.tool
  echo ""
  echo ""
  
  # Test 8: Test user login
  echo "8. Testing Test User Login..."
  TEST_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "testuser@example.com",
      "password": "Test@1234",
      "remember_me": false
    }')
  
  echo "$TEST_LOGIN" | python3 -m json.tool
  echo ""
  
  if echo "$TEST_LOGIN" | grep -q "access_token"; then
    echo "✅ Test user can login successfully"
  else
    echo "❌ Test user login failed"
  fi
  echo ""
  echo ""
  
  # Test 9: Deactivate test user
  echo "9. Testing 'Deactivate User' endpoint..."
  curl -s -X DELETE "$BASE_URL/api/v1/users/$USER_ID" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo "✅ Test user deactivated"
else
  echo "⚠️  User creation failed or user already exists"
fi

echo ""
echo "========================================="
echo "All tests completed!"
echo "========================================="
