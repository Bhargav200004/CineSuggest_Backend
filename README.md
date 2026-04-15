# 🎬 Movie Recommendation API

A production-ready FastAPI backend for a movie recommendation system with JWT authentication, user ratings, favorites, and personalized recommendations.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-4169E1?logo=postgresql)](https://www.postgresql.org)
[![SQLite](https://img.shields.io/badge/SQLite-Supported-003B57?logo=sqlite)](https://www.sqlite.org)

## 🌟 Features

- ✅ **JWT Authentication** - Secure user registration and login with access & refresh tokens
- ✅ **Refresh Token Support** - Stay logged in for 7 days without re-entering password
- ✅ **Movie Database** - Rich movie metadata with posters from TMDb
- ✅ **User Ratings** - Rate movies from 0.5 to 5.0 stars
- ✅ **Favorites** - Mark movies as favorites
- ✅ **Personalized Recommendations** - Collaborative filtering using scikit-surprise SVD
- ✅ **Search & Filter** - Search movies by title, filter by genre
- ✅ **PostgreSQL & SQLite** - Supports both databases (Supabase optimized)
- ✅ **Optimized Data Loading** - Batch processing for fast Supabase imports
- ✅ **CORS Enabled** - Ready for frontend integration
- ✅ **Auto-generated Docs** - Interactive API documentation
- ✅ **Global Error Handling** - Comprehensive error handling with standardized responses

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Database Setup](#-database-setup)
- [Loading Data to Supabase](#-loading-data-to-supabase)
- [Authentication with Refresh Tokens](#-authentication)
- [Global Error Handling](#-global-error-handling)
- [API Endpoints](#-api-endpoints)
- [API Response Examples](#-api-response-examples)
- [Storage Optimization](#-storage-optimization)
- [Frontend Integration](#-frontend-integration)
- [Deployment](#-deployment)

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd MovieRecommendation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and update the SECRET_KEY:

```env
DATABASE_URL=sqlite:///./movies.db
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
TMDB_API_KEY=0248e4a7336b921b867f98eb4ffc39cd
```

> ⚠️ **Important**: Change the `SECRET_KEY` in production! Generate one with:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 3. Load Movie Data

```bash
# This will load movies from CSV files into the database
# With optimized batch processing for better performance
python load_data.py
```

⏱️ **Note**: Loading ~45,000 movies may take 5-15 minutes due to poster fetching from TMDb API.

### 4. Run the Server

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 💾 Database Setup

### Option 1: SQLite (Default - Local Development)

SQLite is pre-configured and ready to use. No additional setup needed!

```env
DATABASE_URL=sqlite:///./movies.db
```

**Pros**: Zero configuration, perfect for development  
**Cons**: Not suitable for production with multiple users

### Option 2: PostgreSQL (Recommended for Production)

#### Using Supabase (Free Tier)

1. **Create a Supabase Account**: [https://supabase.com](https://supabase.com)

2. **Create a New Project**

3. **Get Database Connection String**:
   - Go to Project Settings → Database
   - Copy the "Connection String" (URI format)
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

4. **Update `.env`**:
   ```env
   DATABASE_URL=postgresql://postgres:your-password@db.xxxxx.supabase.co:5432/postgres
   ```

5. **Load Data**:
   ```bash
   python load_data.py
   ```

#### Using Local PostgreSQL

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb movies_db

# Update .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/movies_db
```

---

## 📊 Loading Data to Supabase

### Step-by-Step Guide for Production

#### **Step 1: Create Supabase Project**

1. Visit [https://supabase.com](https://supabase.com) and sign up
2. Click **"New Project"**
3. Fill in project details:
   - **Name**: `movie-recommendation-db`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
4. Wait 2-3 minutes for provisioning

#### **Step 2: Get Connection String**

1. Go to **Project Settings** → **Database**
2. Scroll to **Connection String** section
3. Select **URI** format
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you set

#### **Step 3: Update Environment Variables**

Update your `.env` file:

```env
DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
TMDB_API_KEY=0248e4a7336b921b867f98eb4ffc39cd
```

#### **Step 4: Run Optimized Data Loader**

The improved `load_data.py` script features:
- ✅ **Batch Processing**: Inserts 1000 records per batch (configurable)
- ✅ **Progress Logging**: Real-time updates on loading progress
- ✅ **Async Poster Fetching**: Parallel TMDb API requests
- ✅ **Error Handling**: Graceful failures with detailed error messages
- ✅ **Performance Metrics**: Total time tracking

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the loader
python load_data.py
```

**Expected Output:**
```
2024-XX-XX XX:XX:XX - INFO - Dropping and re-creating database tables...
2024-XX-XX XX:XX:XX - INFO - Preparing movies from movies_metadata.csv...
2024-XX-XX XX:XX:XX - INFO - Fetching posters for 45466 movies asynchronously...
2024-XX-XX XX:XX:XX - INFO - Poster fetching complete.
2024-XX-XX XX:XX:XX - INFO - Processed 100 movies so far...
2024-XX-XX XX:XX:XX - INFO - Inserting 45466 movies in batches of 1000...
2024-XX-XX XX:XX:XX - INFO -   Batch 1/46 inserted (1000/45466 movies)
2024-XX-XX XX:XX:XX - INFO -   Batch 2/46 inserted (2000/45466 movies)
...
2024-XX-XX XX:XX:XX - INFO - Movies inserted successfully.
2024-XX-XX XX:XX:XX - INFO - ✅ Total Movies: 45466
2024-XX-XX XX:XX:XX - INFO - Preparing users from ratings_small.csv...
2024-XX-XX XX:XX:XX - INFO - Inserting 671 users in batches of 1000...
2024-XX-XX XX:XX:XX - INFO -   Batch 1/1 inserted (671/671 users)
2024-XX-XX XX:XX:XX - INFO - ✅ Total Users: 671
2024-XX-XX XX:XX:XX - INFO - Preparing ratings...
2024-XX-XX XX:XX:XX - INFO - Processed 10000 ratings...
2024-XX-XX XX:XX:XX - INFO - Inserting 100004 ratings in batches of 1000...
2024-XX-XX XX:XX:XX - INFO -   Batch 1/101 inserted (1000/100004 ratings)
...
2024-XX-XX XX:XX:XX - INFO - ✅ Total Ratings: 100004
2024-XX-XX XX:XX:XX - INFO - Time taken == 0:08:45.123456
```

#### **Step 5: Verify Data in Supabase**

1. Go to Supabase Dashboard → **Table Editor**
2. Verify these tables exist:
   - `users` (~671 rows)
   - `movies` (~45,000 rows)
   - `ratings` (~100,000 rows)
   - `favorites` (empty initially)
3. Click on each table to view sample data

#### **Step 6: Performance Optimization Tips**

**Faster Loading:**
- Increase `BATCH_SIZE` in `load_data.py` to 2000-5000 for Supabase
- Use direct connection (not pooler) for bulk imports
- Run during off-peak hours for better network speed

**Troubleshooting:**
- **Connection timeout**: Check firewall and database URL
- **Rate limiting**: Reduce batch size or add delays
- **Memory errors**: Load data in chunks (modify script to process partial CSVs)

---

## 🧹 Storage Optimization

### Files to Delete After Loading to Supabase

Once data is successfully loaded to Supabase, delete these files to **save ~50MB+ on GitHub**:

#### **Delete Large CSV Files:**

```bash
# Windows PowerShell
Remove-Item movies_metadata.csv
Remove-Item ratings_small.csv
Remove-Item movies.db  # SQLite file (not needed with Supabase)

# macOS/Linux
rm movies_metadata.csv
rm ratings_small.csv
rm movies.db
```

**Total savings: ~50-60 MB**

#### **Update .gitignore:**

Add these lines to prevent re-adding:

```gitignore
# Large dataset files (loaded to Supabase)
*.csv
movies_metadata.csv
ratings_small.csv

# Local databases
*.db
movies.db

# Environment variables (never commit)
.env

# Python cache
__pycache__/
*.pyc
*.pyo
venv/

# IDE
.vscode/
.idea/
```

#### **Commit and Push:**

```bash
# Stage and commit deletions
git rm movies_metadata.csv ratings_small.csv movies.db
git add .gitignore
git commit -m "Remove large dataset files after Supabase migration"
git push
```

#### **What to Keep:**

✅ **Keep these files** (still needed):
- `load_data.py` - For re-loading data or migrations
- `.env.example` - Template for environment setup
- All Python source files (.py)
- `requirements.txt`
- Documentation files (README, guides)

---

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)** with **refresh token** support for secure, persistent authentication.

### Key Features:
- ✅ **Access Tokens**: Short-lived (30 minutes) for API requests
- ✅ **Refresh Tokens**: Long-lived (7 days) to stay logged in
- ✅ **No Re-login**: Users stay authenticated without entering password again
- ✅ **Automatic Token Rotation**: New tokens issued on refresh for security

### Registration Flow

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123",
    "full_name": "John Doe"
  }'
```

**Response**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe"
}
```

### Login Flow

```bash
# Login to get access and refresh tokens
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=secure123"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save both tokens securely!**
- `access_token` - Use for API requests (expires in 30 minutes, configurable)
- `refresh_token` - Use to get new tokens (expires in 7 days, configurable)

**🔒 Security Note**: In production, store refresh tokens in HTTP-only cookies or secure storage, NOT localStorage.

### Using the Access Token

Include the token in the `Authorization` header for protected endpoints:

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Refresh Token Flow (Stay Logged In!)

When your access token expires (after 30 minutes), use the refresh token to get new tokens **without re-entering your password**:

```bash
# Refresh your access token
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response**:
```json
{
  "access_token": "NEW_ACCESS_TOKEN...",
  "token_type": "bearer"
}
```

**🔑 Important Notes:**
- ✅ Users stay logged in for 7 days without password re-entry
- ✅ Access token refreshed automatically (30 minutes → fresh token)
- ✅ Secure token rotation for enhanced security
- ✅ Perfect for mobile apps, SPAs, and desktop clients
- ⚠️ Implement token refresh BEFORE access token expires
- ⚠️ In production, consider refresh token rotation (issue new refresh token on each refresh)

**Implementation in Client:**

```javascript
// Check if access token is about to expire (e.g., 5 minutes before)
function isTokenExpiringSoon(token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  const expiryTime = payload.exp * 1000; // Convert to milliseconds
  const currentTime = Date.now();
  const fiveMinutes = 5 * 60 * 1000;
  return (expiryTime - currentTime) < fiveMinutes;
}

// Auto-refresh logic
async function makeAuthenticatedRequest(endpoint) {
  let accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  
  // Refresh if expiring soon
  if (isTokenExpiringSoon(accessToken)) {
    const response = await fetch('/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    const data = await response.json();
    accessToken = data.access_token;
    localStorage.setItem('access_token', accessToken);
  }
  
  // Make request with fresh token
  return fetch(endpoint, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
}
```

---

## 🛡️ Global Error Handling

The API implements **comprehensive global error handling** to ensure no error crashes the application. All errors are caught and returned with a standardized JSON response format.

### Error Response Format

All errors follow this consistent structure:

```json
{
  "success": false,
  "error": {
    "type": "NotFoundException",
    "message": "Movie not found: 99999",
    "status_code": 404,
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "path": "/movies/99999"
  }
}
```

### Error Types

The API handles all error types gracefully:

| Error Type | Status Code | Description |
|------------|-------------|-------------|
| `ValidationError` | 422 | Request validation failed (invalid input data) |
| `NotFoundException` | 404 | Requested resource not found |
| `UnauthorizedException` | 401 | Authentication failed or token invalid |
| `ForbiddenException` | 403 | Access forbidden (insufficient permissions) |
| `ConflictException` | 409 | Resource already exists (e.g., duplicate username) |
| `BadRequestException` | 400 | Invalid request format or parameters |
| `DatabaseError` | 500 | Database operation failed |
| `InternalServerError` | 500 | Unexpected server error |

### Error Handling Examples

#### 1. Validation Error (422)

When you send invalid data:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "123"}'
```

**Response**:
```json
{
  "success": false,
  "error": {
    "type": "ValidationError",
    "message": "Request validation failed",
    "status_code": 422,
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "path": "/auth/register",
    "details": {
      "validation_errors": [
        {
          "field": "body -> password",
          "message": "ensure this value has at least 6 characters",
          "type": "value_error.any_str.min_length"
        }
      ]
    }
  }
}
```

#### 2. Not Found Error (404)

When requesting a non-existent resource:

```bash
curl "http://localhost:8000/movies/999999"
```

**Response**:
```json
{
  "success": false,
  "error": {
    "type": "NotFoundException",
    "message": "Movie not found: 999999",
    "status_code": 404,
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "path": "/movies/999999"
  }
}
```

#### 3. Unauthorized Error (401)

When using invalid or expired token:

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer invalid_token"
```

**Response**:
```json
{
  "success": false,
  "error": {
    "type": "UnauthorizedException",
    "message": "Could not validate credentials",
    "status_code": 401,
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "path": "/auth/me"
  }
}
```

#### 4. Conflict Error (409)

When trying to register with an existing username:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "existing_user",
    "password": "password123"
  }'
```

**Response**:
```json
{
  "success": false,
  "error": {
    "type": "ConflictException",
    "message": "Username already registered",
    "status_code": 409,
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "path": "/auth/register"
  }
}
```

#### 5. Database Error (500)

When a database operation fails:

```json
{
  "success": false,
  "error": {
    "type": "DatabaseError",
    "message": "Database integrity constraint violated",
    "status_code": 500,
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "path": "/interactions/ratings"
  }
}
```

### Error Handling Implementation

The error handling system consists of:

1. **Custom Exception Classes** (`exceptions.py`):
   - Base `MovieAPIException` class
   - Specific exception types for different error scenarios
   - Consistent error attributes (message, status_code, details)

2. **Global Error Handlers** (`error_handlers.py`):
   - Catches ALL exceptions (FastAPI, SQLAlchemy, Pydantic, Python)
   - Standardizes error response format
   - Logs errors with full stack traces for debugging
   - Prevents application crashes

3. **Automatic Registration** (`main.py`):
   - All handlers registered on application startup
   - No endpoint can fail without being caught

### Client-Side Error Handling

Frontend applications should check the `success` field:

```javascript
async function makeRequest(endpoint) {
  const response = await fetch(endpoint);
  const data = await response.json();
  
  if (!data.success) {
    // Handle error
    console.error(`Error ${data.error.status_code}: ${data.error.message}`);
    
    // Show user-friendly message based on error type
    switch(data.error.type) {
      case 'ValidationError':
        showValidationErrors(data.error.details.validation_errors);
        break;
      case 'UnauthorizedException':
        redirectToLogin();
        break;
      case 'NotFoundException':
        show404Page();
        break;
      default:
        showGenericError(data.error.message);
    }
    return null;
  }
  
  // Success - process data
  return data;
}
```

### Logging

All errors are automatically logged with:
- ✅ Full stack traces for debugging
- ✅ Request path and method
- ✅ Error type and message
- ✅ Timestamp for audit trails

Check application logs for detailed error information in production.

---

## 📚 API Endpoints

### 🔓 Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login (get access + refresh tokens) |
| POST | `/auth/refresh` | Refresh access token (stay logged in) |
| GET | `/movies` | Get all movies (paginated) |
| GET | `/movies/{movie_id}` | Get movie details by ID |
| GET | `/movies/search?q=query` | Search movies by title |
| GET | `/movies/random?limit=10` | Get random movies |
| GET | `/genres` | Get all available genres |

### 🔒 Protected Endpoints (Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/me` | Get current user profile |
| POST | `/interactions/ratings` | Rate a movie |
| DELETE | `/interactions/ratings/{movie_id}` | Delete a rating |
| POST | `/interactions/favorites` | Add to favorites |
| DELETE | `/interactions/favorites/{movie_id}` | Remove from favorites |
| GET | `/interactions/favorites` | Get user's favorite movies |
| GET | `/interactions/ratings` | Get user's ratings |
| GET | `/recommendations` | Get personalized recommendations |

---

## 📄 API Response Examples

### Get Movies

**Request**:
```bash
GET /movies?skip=0&limit=10
```

**Response**:
```json
{
  "movies": [
    {
      "id": 1,
      "title": "Toy Story",
      "genre": "Animation|Comedy|Family",
      "overview": "Led by Woody, Andy's toys live happily in his room...",
      "release_date": "1995-10-30",
      "poster_path": "https://image.tmdb.org/t/p/w500/rhIRbceoE9lR4veEXuwCC2wARtG.jpg",
      "revenue": 373554033,
      "runtime": "81.0",
      "original_language": "en",
      "user_rating": 4.5,
      "is_favorite": true
    }
  ]
}
```

### Get Movie Details

**Request**:
```bash
GET /movies/1
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "title": "Toy Story",
  "genre": "Animation|Comedy|Family",
  "overview": "Led by Woody, Andy's toys live happily in his room until Andy's birthday brings Buzz Lightyear onto the scene...",
  "release_date": "1995-10-30",
  "poster_path": "https://image.tmdb.org/t/p/w500/rhIRbceoE9lR4veEXuwCC2wARtG.jpg",
  "revenue": 373554033,
  "runtime": "81.0",
  "original_language": "en",
  "user_rating": 4.5,
  "is_favorite": true
}
```

### Search Movies

**Request**:
```bash
GET /movies/search?q=Matrix&limit=5
```

**Response**:
```json
{
  "movies": [
    {
      "id": 603,
      "title": "The Matrix",
      "genre": "Action|Science Fiction",
      "overview": "Set in the 22nd century, The Matrix tells the story...",
      "release_date": "1999-03-30",
      "poster_path": "https://image.tmdb.org/t/p/w500/...",
      "revenue": 463517383,
      "runtime": "136.0",
      "original_language": "en",
      "user_rating": 0,
      "is_favorite": false
    }
  ]
}
```

### Rate a Movie

**Request**:
```bash
POST /interactions/ratings
Authorization: Bearer <token>
Content-Type: application/json

{
  "movie_id": 1,
  "rating": 4.5
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "movie_id": 1,
  "rating": 4.5
}
```

### Add to Favorites

**Request**:
```bash
POST /interactions/favorites
Authorization: Bearer <token>
Content-Type: application/json

{
  "movie_id": 1
}
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "movie_id": 1
}
```

### Get User Profile

**Request**:
```bash
GET /auth/me
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "total_ratings": 42,
  "total_favorites": 15
}
```

### Get Personalized Recommendations

**Request**:
```bash
GET /recommendations?limit=10
Authorization: Bearer <token>
```

**Response**:
```json
{
  "recommendations": [
    {
      "id": 155,
      "title": "The Dark Knight",
      "genre": "Action|Crime|Drama",
      "overview": "Batman raises the stakes in his war on crime...",
      "release_date": "2008-07-18",
      "poster_path": "https://image.tmdb.org/t/p/w500/...",
      "revenue": 1004558444,
      "runtime": "152.0",
      "original_language": "en",
      "user_rating": 0,
      "is_favorite": false
    }
  ]
}
```

---

## 🎨 Frontend Integration

### JavaScript/TypeScript Example

```javascript
// API configuration
const API_BASE_URL = 'http://localhost:8000';
let authToken = null;

// Register user
async function register(username, email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  return await response.json();
}

// Login with refresh token support
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });
  
  const data = await response.json();
  authToken = data.access_token;
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
}

// Refresh access token
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  const data = await response.json();
  authToken = data.access_token;
  localStorage.setItem('access_token', data.access_token);
  return data;
}

// Get movies
async function getMovies(skip = 0, limit = 20) {
  const response = await fetch(
    `${API_BASE_URL}/movies?skip=${skip}&limit=${limit}`,
    {
      headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {}
    }
  );
  return await response.json();
}

// Rate a movie
async function rateMovie(movieId, rating) {
  const response = await fetch(`${API_BASE_URL}/interactions/ratings`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({ movie_id: movieId, rating })
  });
  return await response.json();
}

// Add to favorites
async function addFavorite(movieId) {
  const response = await fetch(`${API_BASE_URL}/interactions/favorites`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({ movie_id: movieId })
  });
  return await response.json();
}

// Search movies
async function searchMovies(query) {
  const response = await fetch(
    `${API_BASE_URL}/movies/search?q=${encodeURIComponent(query)}`,
    {
      headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {}
    }
  );
  return await response.json();
}
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function MovieList() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchMovies();
  }, []);
  
  async function fetchMovies() {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/movies?limit=20', {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    const data = await response.json();
    setMovies(data.movies);
    setLoading(false);
  }
  
  async function handleRate(movieId, rating) {
    const token = localStorage.getItem('token');
    await fetch('http://localhost:8000/interactions/ratings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ movie_id: movieId, rating })
    });
    fetchMovies(); // Refresh to show updated rating
  }
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="movie-list">
      {movies.map(movie => (
        <div key={movie.id} className="movie-card">
          <img src={movie.poster_path} alt={movie.title} />
          <h3>{movie.title}</h3>
          <p>{movie.overview}</p>
          <div>
            <span>Your Rating: {movie.user_rating || 'Not rated'}</span>
            <button onClick={() => handleRate(movie.id, 5)}>⭐ Rate 5</button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Android/Kotlin Example

```kotlin
// API Service with Retrofit
interface MovieApiService {
    @POST("auth/login")
    @FormUrlEncoded
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): TokenResponse
    
    @GET("movies")
    suspend fun getMovies(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 20,
        @Header("Authorization") token: String? = null
    ): MoviesResponse
    
    @POST("interactions/ratings")
    suspend fun rateMovie(
        @Body rating: RatingRequest,
        @Header("Authorization") token: String
    ): RatingResponse
}

// Usage
class MovieRepository(private val api: MovieApiService) {
    private var authToken: String? = null
    
    suspend fun login(username: String, password: String) {
        val response = api.login(username, password)
        authToken = "Bearer ${response.access_token}"
    }
    
    suspend fun getMovies(): List<Movie> {
        val response = api.getMovies(token = authToken)
        return response.movies
    }
    
    suspend fun rateMovie(movieId: Int, rating: Float) {
        authToken?.let { token ->
            api.rateMovie(
                RatingRequest(movieId, rating),
                token
            )
        }
    }
}
```

---

## 🚢 Deployment

### Deploy to Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create your-movie-api
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
git push heroku main

# Load data
heroku run python load_data.py
```

### Deploy to Railway

1. Connect your GitHub repository to Railway
2. Add PostgreSQL database add-on
3. Set environment variables in Railway dashboard:
   - `SECRET_KEY`
   - `DATABASE_URL` (auto-set by Railway)
4. Deploy!

### Deploy to Render

1. Create new Web Service
2. Connect your repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🛠️ Development

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Formatting

```bash
pip install black isort
black .
isort .
```

### Type Checking

```bash
pip install mypy
mypy .
```

---

## 📊 Database Schema

```
Users
├── id (PK)
├── username (unique)
├── email (unique)
├── hashed_password
└── full_name

Movies
├── id (PK)
├── title
├── genre
├── overview
├── release_date
├── poster_path
├── revenue
├── runtime
└── original_language

Ratings
├── id (PK)
├── user_id (FK → Users)
├── movie_id (FK → Movies)
└── rating (0.5-5.0)
    └── UNIQUE(user_id, movie_id)

Favorites
├── id (PK)
├── user_id (FK → Users)
└── movie_id (FK → Movies)
    └── UNIQUE(user_id, movie_id)
```

---

## 🔧 Troubleshooting

### Issue: "Could not import module 'jose'"

```bash
pip install python-jose[cryptography]
```

### Issue: "No module named 'passlib'"

```bash
pip install passlib[bcrypt]
```

### Issue: Database connection error

- Check your `DATABASE_URL` in `.env`
- For PostgreSQL, ensure the database exists
- For SQLite, check file permissions

### Issue: CORS errors from frontend

Update `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 License

MIT License - feel free to use this project for learning or production!

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues or questions, please create an issue in the GitHub repository.

---

**Built with ❤️ using FastAPI**