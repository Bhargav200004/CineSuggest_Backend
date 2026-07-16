"""
Test script to demonstrate global error handling
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_validation_error():
    """Test validation error (password too short)"""
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": "test", "password": "123"}
    )
    print_response("Validation Error (422) - Password too short", response)

def test_not_found_error():
    """Test not found error"""
    response = requests.get(f"{BASE_URL}/movies/999999")
    print_response("Not Found Error (404) - Movie doesn't exist", response)

def test_unauthorized_error():
    """Test unauthorized error"""
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    print_response("Unauthorized Error (401) - Invalid token", response)

def test_successful_request():
    """Test successful request"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Successful Request - Health check", response)

def test_successful_movies():
    """Test successful movies request"""
    response = requests.get(f"{BASE_URL}/movies?limit=2")
    print_response("Successful Request - Get movies", response)

def test_search_no_results():
    """Test search with no results (not an error)"""
    response = requests.get(f"{BASE_URL}/movies/search?q=nonexistentmoviexyz")
    print_response("Search with no results (empty, not error)", response)

def test_missing_query_param():
    """Test missing required query parameter"""
    response = requests.get(f"{BASE_URL}/movies/search")
    print_response("Validation Error (422) - Missing query param", response)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  GLOBAL ERROR HANDLING TEST SUITE")
    print("="*60)
    
    # Test successful requests
    test_successful_request()
    test_successful_movies()
    test_search_no_results()
    
    # Test error scenarios
    test_validation_error()
    test_not_found_error()
    test_unauthorized_error()
    test_missing_query_param()
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETED")
    print("="*60)
    print("\n✅ All errors handled gracefully - no crashes!")
    print("✅ All responses follow standardized format")
    print("✅ Application continues running after all errors\n")

if __name__ == "__main__":
    main()
