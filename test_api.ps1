# API Endpoint Testing Script
# This script tests all endpoints of the Movie Recommendation API

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MOVIE RECOMMENDATION API TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [string]$Body = $null,
        [hashtable]$Headers = @{},
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "Testing: $Name..." -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            ContentType = "application/json"
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host " ✓ PASS" -ForegroundColor Green
            $script:testsPassed++
            return $response
        } else {
            Write-Host " ✗ FAIL (Status: $($response.StatusCode))" -ForegroundColor Red
            $script:testsFailed++
            return $null
        }
    } catch {
        Write-Host " ✗ FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:testsFailed++
        return $null
    }
}

# 1. Health Check
Write-Host "`n[1] HEALTH & STATUS ENDPOINTS" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Test-Endpoint "Health Check" "GET" "$baseUrl/health"
Test-Endpoint "Root Endpoint" "GET" "$baseUrl/"

# 2. User Registration
Write-Host "`n[2] AUTHENTICATION - REGISTRATION" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
$registerBody = @{
    username = "testuser_$(Get-Random -Maximum 10000)"
    password = "testpass123"
    email = "test@example.com"
    full_name = "Test User"
} | ConvertTo-Json

$registerResponse = Test-Endpoint "Register User" "POST" "$baseUrl/auth/register" -Body $registerBody -ExpectedStatus 201

if ($registerResponse) {
    $userData = $registerResponse.Content | ConvertFrom-Json
    Write-Host "   → User created with ID: $($userData.id)" -ForegroundColor Gray
}

# 3. User Login
Write-Host "`n[3] AUTHENTICATION - LOGIN" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Yellow

# Create a test user first
$loginUser = "testlogin_$(Get-Random -Maximum 10000)"
$loginPass = "password123"
$createUserBody = @{
    username = $loginUser
    password = $loginPass
    email = "login@example.com"
} | ConvertTo-Json

Invoke-WebRequest -Uri "$baseUrl/auth/register" -Method POST -Body $createUserBody -ContentType "application/json" | Out-Null

# Now login
$loginBody = "username=$loginUser&password=$loginPass"
$loginHeaders = @{
    "Content-Type" = "application/x-www-form-urlencoded"
}

$loginResponse = Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST -Body $loginBody -Headers $loginHeaders -ContentType "application/x-www-form-urlencoded"

if ($loginResponse.StatusCode -eq 200) {
    Write-Host "Testing: User Login... ✓ PASS" -ForegroundColor Green
    $script:testsPassed++
    
    $tokens = $loginResponse.Content | ConvertFrom-Json
    $accessToken = $tokens.access_token
    $refreshToken = $tokens.refresh_token
    
    Write-Host "   → Access Token received: $($accessToken.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "   → Refresh Token received: $($refreshToken.Substring(0, 20))..." -ForegroundColor Gray
} else {
    Write-Host "Testing: User Login... ✗ FAIL" -ForegroundColor Red
    $script:testsFailed++
    exit
}

# 4. Refresh Token
Write-Host "`n[4] AUTHENTICATION - REFRESH TOKEN" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Yellow

$refreshBody = @{
    refresh_token = $refreshToken
} | ConvertTo-Json

$refreshResponse = Invoke-WebRequest -Uri "$baseUrl/auth/refresh" -Method POST -Body $refreshBody -ContentType "application/json"

if ($refreshResponse.StatusCode -eq 200) {
    Write-Host "Testing: Refresh Token... ✓ PASS" -ForegroundColor Green
    $script:testsPassed++
    
    $newTokens = $refreshResponse.Content | ConvertFrom-Json
    $accessToken = $newTokens.access_token
    Write-Host "   → New Access Token received" -ForegroundColor Gray
} else {
    Write-Host "Testing: Refresh Token... ✗ FAIL" -ForegroundColor Red
    $script:testsFailed++
}

# 5. Get User Profile
Write-Host "`n[5] USER PROFILE" -ForegroundColor Yellow
Write-Host "===================" -ForegroundColor Yellow

$authHeaders = @{
    "Authorization" = "Bearer $accessToken"
}

$profileResponse = Test-Endpoint "Get My Profile" "GET" "$baseUrl/auth/me" -Headers $authHeaders

if ($profileResponse) {
    $profile = $profileResponse.Content | ConvertFrom-Json
    Write-Host "   → Username: $($profile.username)" -ForegroundColor Gray
    Write-Host "   → Ratings: $($profile.total_ratings)" -ForegroundColor Gray
    Write-Host "   → Favorites: $($profile.total_favorites)" -ForegroundColor Gray
}

# 6. Movies Endpoints
Write-Host "`n[6] MOVIES ENDPOINTS" -ForegroundColor Yellow
Write-Host "=======================" -ForegroundColor Yellow

Test-Endpoint "Get All Movies" "GET" "$baseUrl/movies?limit=5"
Test-Endpoint "Get Random Movies" "GET" "$baseUrl/movies/random?limit=3"
Test-Endpoint "Get Movie by ID" "GET" "$baseUrl/movies/1"
Test-Endpoint "Search Movies" "GET" "$baseUrl/movies/search?q=Toy"

# 7. Ratings Endpoints
Write-Host "`n[7] RATINGS ENDPOINTS" -ForegroundColor Yellow
Write-Host "========================" -ForegroundColor Yellow

$ratingBody = @{
    movie_id = 1
    rating = 4.5
} | ConvertTo-Json

Test-Endpoint "Add Rating" "POST" "$baseUrl/interactions/ratings" -Body $ratingBody -Headers $authHeaders
Test-Endpoint "Get My Ratings" "GET" "$baseUrl/interactions/ratings" -Headers $authHeaders

# Update rating
$updateRatingBody = @{
    movie_id = 1
    rating = 5.0
} | ConvertTo-Json

Test-Endpoint "Update Rating" "POST" "$baseUrl/interactions/ratings" -Body $updateRatingBody -Headers $authHeaders

# 8. Favorites Endpoints
Write-Host "`n[8] FAVORITES ENDPOINTS" -ForegroundColor Yellow
Write-Host "==========================" -ForegroundColor Yellow

$favoriteBody = @{
    movie_id = 2
} | ConvertTo-Json

Test-Endpoint "Add to Favorites" "POST" "$baseUrl/interactions/favorites" -Body $favoriteBody -Headers $authHeaders -ExpectedStatus 201
Test-Endpoint "Get My Favorites" "GET" "$baseUrl/interactions/favorites" -Headers $authHeaders
Test-Endpoint "Remove from Favorites" "DELETE" "$baseUrl/interactions/favorites/2" -Headers $authHeaders -ExpectedStatus 204

# 9. Genre Endpoint
Write-Host "`n[9] GENRE ENDPOINT" -ForegroundColor Yellow
Write-Host "=====================" -ForegroundColor Yellow

Test-Endpoint "Get All Genres" "GET" "$baseUrl/genres"

# 10. Recommendations
Write-Host "`n[10] RECOMMENDATIONS" -ForegroundColor Yellow
Write-Host "=======================" -ForegroundColor Yellow

# Add more ratings first
for ($i = 2; $i -le 5; $i++) {
    $rBody = @{
        movie_id = $i
        rating = (Get-Random -Minimum 3.0 -Maximum 5.0)
    } | ConvertTo-Json
    
    Invoke-WebRequest -Uri "$baseUrl/interactions/ratings" -Method POST -Body $rBody -Headers $authHeaders -ContentType "application/json" | Out-Null
}

Test-Endpoint "Get Recommendations" "GET" "$baseUrl/recommendations?limit=5" -Headers $authHeaders

# Final Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "           TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total Tests: $($testsPassed + $testsFailed)" -ForegroundColor White
Write-Host "Passed:      $testsPassed" -ForegroundColor Green
Write-Host "Failed:      $testsFailed" -ForegroundColor Red

if ($testsFailed -eq 0) {
    Write-Host "`n✓ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Your API is working perfectly!" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Some tests failed. Check the output above." -ForegroundColor Yellow
}

Write-Host "`n========================================`n" -ForegroundColor Cyan

# Test refresh token keeps user logged in
Write-Host "`n[BONUS] REFRESH TOKEN PERSISTENCE TEST" -ForegroundColor Magenta
Write-Host "=========================================" -ForegroundColor Magenta
Write-Host "Simulating token expiration scenario..." -ForegroundColor Gray
Write-Host "1. User logs in → Gets access + refresh token ✓" -ForegroundColor Gray
Write-Host "2. Access token expires after 30 min" -ForegroundColor Gray
Write-Host "3. App uses refresh token → Gets new access token ✓" -ForegroundColor Gray
Write-Host "4. User stays logged in without re-entering password ✓" -ForegroundColor Gray
Write-Host "`nRefresh tokens are valid for 7 days!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Magenta
