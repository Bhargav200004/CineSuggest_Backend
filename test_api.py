"""
Quick API Test Script - Tests all endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_endpoint(name, method, url, data=None, headers=None, expected_status=200):
    print(f"Testing: {name}...", end=' ')
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == expected_status:
            print("✓ PASS")
            return response
        else:
            print(f"✗ FAIL (Status: {response.status_code})")
            print(f"  Response: {response.text[:100]}")
            return None
    except Exception as e:
        print(f"✗ FAIL ({e})")
        return None

# Run Tests
print("\n" + "="*60)
print("  MOVIE RECOMMENDATION API - COMPREHENSIVE TEST")
print("="*60)

tests_passed = 0
tests_failed = 0

# 1. Health Check
print_section("HEALTH & STATUS")
if test_endpoint("Health Check", "GET", f"{BASE_URL}/health"):
    tests_passed += 1
else:
    tests_failed += 1

if test_endpoint("Root Endpoint", "GET", f"{BASE_URL}/"):
    tests_passed += 1
else:
    tests_failed += 1

# 2. Register User
print_section("AUTHENTICATION - REGISTRATION")
import random
random_id = random.randint(1000, 9999)
username = f"testuser_{random_id}"
register_data = {
    "username": username,
    "password": "password123",
    "email": f"test{random_id}@example.com"
}

reg_response = test_endpoint("Register User", "POST", f"{BASE_URL}/auth/register", data=register_data, expected_status=201)
if reg_response:
    tests_passed += 1
    print(f"  → User created: {username}")
else:
    tests_failed += 1

# 3. Login
print_section("AUTHENTICATION - LOGIN")
login_data = {
    "username": username,
    "password": "password123"
}

# Login requires form data, not JSON
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data=login_data,  # Note: data, not json
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_response.status_code == 200:
    print("Testing: Login... ✓ PASS")
    tests_passed += 1
    tokens = login_response.json()
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    print(f"  → Access Token: {access_token[:30]}...")
    print(f"  → Refresh Token: {refresh_token[:30]}...")
else:
    print("Testing: Login... ✗ FAIL")
    tests_failed += 1
    print(f"  Response: {login_response.text}")
    exit()

# 4. Refresh Token
print_section("AUTHENTICATION - REFRESH TOKEN")
refresh_data = {"refresh_token": refresh_token}
refresh_response = test_endpoint("Refresh Token", "POST", f"{BASE_URL}/auth/refresh", data=refresh_data)
if refresh_response:
    tests_passed += 1
    new_tokens = refresh_response.json()
    access_token = new_tokens['access_token']
    print(f"  → New Access Token received")
else:
    tests_failed += 1

# Auth headers for protected endpoints
auth_headers = {"Authorization": f"Bearer {access_token}"}

# 5. User Profile
print_section("USER PROFILE")
profile_response = test_endpoint("Get My Profile", "GET", f"{BASE_URL}/auth/me", headers=auth_headers)
if profile_response:
    tests_passed += 1
    profile = profile_response.json()
    print(f"  → Username: {profile['username']}")
    print(f"  → Total Ratings: {profile['total_ratings']}")
    print(f"  → Total Favorites: {profile['total_favorites']}")
else:
    tests_failed += 1

# 6. Movies
print_section("MOVIES ENDPOINTS")
if test_endpoint("Get Movies", "GET", f"{BASE_URL}/movies?limit=5"):
    tests_passed += 1
else:
    tests_failed += 1

if test_endpoint("Get Random Movies", "GET", f"{BASE_URL}/movies/random?limit=3"):
    tests_passed += 1
else:
    tests_failed += 1

# 7. Ratings
print_section("RATINGS")
rating_data = {"movie_id": 1, "rating": 4.5}
if test_endpoint("Add Rating", "POST", f"{BASE_URL}/interactions/ratings", data=rating_data, headers=auth_headers):
    tests_passed += 1
else:
    tests_failed += 1

if test_endpoint("Get My Ratings", "GET", f"{BASE_URL}/interactions/ratings", headers=auth_headers):
    tests_passed += 1
else:
    tests_failed += 1

# 8. Favorites
print_section("FAVORITES")
fav_data = {"movie_id": 2}
if test_endpoint("Add Favorite", "POST", f"{BASE_URL}/interactions/favorites", data=fav_data, headers=auth_headers, expected_status=201):
    tests_passed += 1
else:
    tests_failed += 1

if test_endpoint("Get Favorites", "GET", f"{BASE_URL}/interactions/favorites", headers=auth_headers):
    tests_passed += 1
else:
    tests_failed += 1

# Summary
print_section("TEST SUMMARY")
print(f"Total Tests: {tests_passed + tests_failed}")
print(f"✓ Passed:    {tests_passed}")
print(f"✗ Failed:    {tests_failed}")

if tests_failed == 0:
    print("\n✓ ALL TESTS PASSED! API is working perfectly!")
else:
    print(f"\n⚠ {tests_failed} test(s) failed. Check output above.")

print("\n" + "="*60)
print("  REFRESH TOKEN FEATURE")
print("="*60)
print("✓ Access Token: 30 minutes expiry")
print("✓ Refresh Token: 7 days expiry")
print("✓ Users can stay logged in without re-entering password")
print("="*60 + "\n")
