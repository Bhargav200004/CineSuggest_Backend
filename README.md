# 🎬 Movie Recommendation API Reference

This is the official API documentation for the Movie Recommendation System backend.

The API provides endpoints for user management, movie management, processing user interactions (ratings and favorites), and generating personalized recommendations.

## 📍 Base URL

All API endpoints are relative to the base URL.

* **Local Development:** `http://127.0.0.1:8000`

---

## 👤 User Management

### POST /users

* **Use:** Creates a new user in the database.
* **Request Body:** `application/json`

    ```json
    {
      "username": "new_user_name"
    }
    ```

* **`curl` Example:**

    ```bash
    curl -X POST "[http://127.0.0.1:8000/users](http://127.0.0.1:8000/users)" \
         -H "Content-Type: application/json" \
         -d '{"username": "curl_user"}'
    ```

* **Success Response:** `200 OK`

    ```json
    {
      "username": "curl_user",
      "id": 611
    }
    ```

### GET /users

* **Use:** Retrieves a list of all registered users.
* **`curl` Example:**

    ```bash
    curl -X GET "[http://127.0.0.1:8000/users](http://127.0.0.1:8000/users)"
    ```

* **Success Response:** `200 OK` (Response is truncated for brevity)

    ```json
    [
      {
        "username": "user_1",
        "id": 1
      },
      {
        "username": "user_2",
        "id": 2
      },
      ...
    ]
    ```

---

## 🎬 Movie Management

### POST /movies

* **Use:** Adds a new movie to the database.
* **Request Body:** `application/json`

    ```json
    {
      "title": "My New Movie",
      "genre": "Action|Adventure|Sci-Fi"
    }
    ```

* **`curl` Example:**

    ```bash
    curl -X POST "[http://127.0.0.1:8000/movies](http://127.0.0.1:8000/movies)" \
         -H "Content-Type: application/json" \
         -d '{"title": "My Test Movie", "genre": "Sci-Fi|Test"}'
    ```

* **Success Response:** `200 OK`

    ```json
    {
      "title": "My Test Movie",
      "genre": "Sci-Fi|Test",
      "id": 9743
    }
    ```

### GET /movies

* **Use:** Retrieves a list of all movies in the database.
* **`curl` Example:**

    ```bash
    curl -X GET "[http://127.0.0.1:8000/movies](http://127.0.0.1:8000/movies)"
    ```

* **Success Response:** `200 OK` (Response is truncated for brevity)

    ```json
    [
      {
        "title": "Toy Story (1995)",
        "genre": "Adventure|Animation|Children|Comedy|Fantasy",
        "id": 1
      },
      {
        "title": "Jumanji (1995)",
        "genre": "Adventure|Children|Fantasy",
        "id": 2
      },
      ...
    ]
    ```

---

## ⭐ Interactions (Ratings & Favorites)

### POST /ratings

* **Use:** Adds or updates a user's rating for a movie. The rating must be an integer from 1 to 5. If a rating already exists for this user/movie pair, it will be updated (upsert).
* **Request Body:** `application/json`

    ```json
    {
      "user_id": 1,
      "movie_id": 1,
      "rating": 5
    }
    ```

* **`curl` Example:**

    ```bash
    curl -X POST "[http://127.0.0.1:8000/ratings](http://127.0.0.1:8000/ratings)" \
         -H "Content-Type: application/json" \
         -d '{"user_id": 1, "movie_id": 1, "rating": 5}'
    ```

* **Success Response:** `200 OK`

    ```json
    {
      "user_id": 1,
      "movie_id": 1,
      "rating": 5,
      "id": 100001
    }
    ```

### POST /favorites

* **Use:** Toggles a movie as a favorite for a user.
    * If the user has **not** favorited the movie, this request adds it.
    * If the user **has** favorited the movie, this *same* request removes it.
* **Request Body:** `application/json`

    ```json
    {
      "user_id": 1,
      "movie_id": 2
    }
    ```

* **`curl` Example:**

    ```bash
    curl -X POST "[http://127.0.0.1:8000/favorites](http://127.0.0.1:8000/favorites)" \
         -H "Content-Type: application/json" \
         -d '{"user_id": 1, "movie_id": 2}'
    ```

* **Success Response (When Adding):** `200 OK`

    ```json
    {
      "user_id": 1,
      "movie_id": 2,
      "id": 1
    }
    ```

* **Success Response (When Removing):** `200 OK`
    * *(Note: The API as written will return the object just before it was deleted. A more advanced API might return a `204 No Content` or a status message.)*

---

## 🧠 Recommendations

### GET /recommend/{user_id}

* **Use:** Generates a list of top 10 personalized movie recommendations for a specific user. The recommendation engine (SVD) is re-trained on every request, considering all ratings and favorites. Favorites are treated as implicit 5-star ratings to boost their importance.
* **URL Parameter:**
    * `user_id` (integer): The ID of the user to get recommendations for.
* **`curl` Example:**

    ```bash
    curl -X GET "[http://127.0.0.1:8000/recommend/1](http://127.0.0.1:8000/recommend/1)"
    ```

* **Success Response:** `200 OK` (Example recommendations will vary)

    ```json
    {
      "recommendations": [
        {
          "title": "Shawshank Redemption, The (1994)",
          "genre": "Crime|Drama",
          "id": 318
        },
        {
          "title": "Godfather, The (1972)",
          "genre": "Crime|Drama",
          "id": 858
        },
        {
          "title": "Forrest Gump (1994)",
          "genre": "Comedy|Drama|Romance|War",
          "id": 356
        },
        // ... 7 more movie objects
      ]
    }
    ```

* **Error Response (User Not Found):** `404 Not Found`
    ```json
    {
      "detail": "User not found"
    }
    ```