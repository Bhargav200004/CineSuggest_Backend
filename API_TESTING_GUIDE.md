# Quick API Testing Guide

Test your Movie Recommendation API with these curl commands!

## Server Status

```bash
# Check if server is running
curl http://localhost:8000/health

# View API docs
# Open in browser: http://localhost:8000/docs
```

---

## 1️⃣ User Registration & Authentication

### Register a New User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"testuser\", \"password\": \"password123\", \"email\": \"test@example.com\"}"
```

### Login and Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

**Save the `access_token` from the response!**

### Get Your Profile
```bash
# Replace YOUR_TOKEN with the token from login
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 2️⃣ Browse Movies

### Get All Movies (First 10)
```bash
curl "http://localhost:8000/movies?skip=0&limit=10"
```

### Get Random Movies
```bash
curl "http://localhost:8000/movies/random?limit=5"
```

### Search Movies
```bash
curl "http://localhost:8000/movies/search?q=Matrix&limit=5"
```

### Get Specific Movie
```bash
curl "http://localhost:8000/movies/1"
```

---

## 3️⃣ Rate & Favorite Movies (Requires Auth)

### Rate a Movie
```bash
curl -X POST "http://localhost:8000/interactions/ratings" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"movie_id\": 1, \"rating\": 4.5}"
```

### Get Your Ratings
```bash
curl -X GET "http://localhost:8000/interactions/ratings" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Add to Favorites
```bash
curl -X POST "http://localhost:8000/interactions/favorites" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"movie_id\": 1}"
```

### Get Your Favorites
```bash
curl -X GET "http://localhost:8000/interactions/favorites" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Remove from Favorites
```bash
curl -X DELETE "http://localhost:8000/interactions/favorites/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 4️⃣ Get Recommendations

```bash
curl -X GET "http://localhost:8000/recommendations?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Complete Test Workflow

### Step 1: Register
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"alice\", \"password\": \"alice123\", \"email\": \"alice@example.com\"}"
```

### Step 2: Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=alice123"
```

**Copy the access_token from response**

### Step 3: Set Token as Variable (PowerShell)
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
```

### Step 4: Browse Movies
```powershell
curl "http://localhost:8000/movies?limit=5"
```

### Step 5: Rate Some Movies
```powershell
curl -X POST "http://localhost:8000/interactions/ratings" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{\"movie_id\": 1, \"rating\": 5.0}"

curl -X POST "http://localhost:8000/interactions/ratings" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{\"movie_id\": 2, \"rating\": 4.0}"
```

### Step 6: Add Favorites
```powershell
curl -X POST "http://localhost:8000/interactions/favorites" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{\"movie_id\": 1}"
```

### Step 7: Get Recommendations
```powershell
curl "http://localhost:8000/recommendations?limit=10" `
  -H "Authorization: Bearer $token"
```

### Step 8: View Your Profile
```powershell
curl "http://localhost:8000/auth/me" `
  -H "Authorization: Bearer $token"
```

---

## 📱 Testing with Postman

1. **Import Collection**: Use the Swagger docs at http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. For auth endpoints, use the "Authorize" button (🔒) to add your token
4. Execute requests directly from the browser!

---

## 🐛 Common Issues

### "Unauthorized" Error
- Make sure you're including the token in the header
- Format: `Authorization: Bearer YOUR_TOKEN`
- Check that the token hasn't expired (default: 30 minutes)

### "Movie not found"
- Make sure you've loaded the data with `python load_data.py`
- Check that the movie_id exists in your database

### Server Not Running
- Start with: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Check if port 8000 is already in use

---

## 💡 Tips

- Use the **interactive docs** at http://localhost:8000/docs for easier testing
- Token expires in 30 minutes (configurable in `.env`)
- Rating must be between 0.5 and 5.0 (increments of 0.5)
- All timestamps are in UTC

---

**Happy Testing! 🚀**
