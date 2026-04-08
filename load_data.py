import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import logging
import re
import asyncio
import aiohttp
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
METADATA_CSV = "movies_metadata.csv"
RATINGS_CSV = "ratings_small.csv"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "438d4def824a39389f045cf20db32ab0")
TMDB_FIND_URL = "https://api.themoviedb.org/3/find/{}?api_key={}&external_source=imdb_id"

# Batch size for bulk inserts (optimized for Supabase)
BATCH_SIZE = 1000  # Process and commit in batches

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def clean_movie_id(id_str):
    try:
        return int(id_str)
    except ValueError:
        return None


# ---------- ASYNC POSTER FETCHING ----------
async def fetch_poster(session, imdb_id):
    """Fetch poster URL asynchronously using aiohttp."""
    if not imdb_id or imdb_id.strip() == "":
        return None

    url = TMDB_FIND_URL.format(imdb_id, TMDB_API_KEY)
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("movie_results"):
                    poster_path = data["movie_results"][0].get("poster_path")
                    if poster_path:
                        return f"{POSTER_BASE_URL}{poster_path}"
    except Exception as e:
        log.warning(f"Poster fetch failed for {imdb_id}: {e}")
    return None


async def fetch_all_posters(imdb_ids):
    """Fetch all posters concurrently."""
    results = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_poster(session, imdb_id) for imdb_id in imdb_ids]
        posters = await asyncio.gather(*tasks)
        for imdb_id, poster in zip(imdb_ids, posters):
            results[imdb_id] = poster
    return results


# ---------- MAIN LOAD FUNCTION ----------
def load_data():
    start_time = datetime.now()
    log.info("Dropping and re-creating database tables...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    kaggle_movie_id_to_db_id = {}
    kaggle_user_id_to_db_id = {}

    try:
        # --- Load Movies ---
        log.info(f"Preparing movies from {METADATA_CSV}...")
        movies_df = pd.read_csv(METADATA_CSV, dtype="object")

        # Fetch poster & backdrop from TMDb API
        movie_ids = []
        for i, row in movies_df.iterrows():
            kaggle_id = clean_movie_id(row["id"])
            if kaggle_id:
                movie_ids.append(kaggle_id)
        
        log.info(f"Fetching backdrop images for {len(movie_ids)} movies from TMDb API...")
        
        # Fetch movie details asynchronously
        async def fetch_movie_backdrop(session, movie_id):
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Use backdrop_path from API response
                        if data.get("backdrop_path"):
                            return f"{POSTER_BASE_URL}{data['backdrop_path']}"
                        
                        # Fallback to poster_path if no backdrop
                        if data.get("poster_path"):
                            return f"{POSTER_BASE_URL}{data['poster_path']}"
            except Exception as e:
                pass
            return None
        
        async def fetch_all_backdrops(movie_ids):
            results = {}
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_movie_backdrop(session, mid) for mid in movie_ids]
                backdrops = await asyncio.gather(*tasks)
                for movie_id, backdrop in zip(movie_ids, backdrops):
                    results[movie_id] = backdrop
            return results
        
        movie_backdrops = asyncio.run(fetch_all_backdrops(movie_ids))
        log.info(f"Fetched backdrop images for {len(movie_backdrops)} movies.")

        movies_to_add = []

        for i, row in movies_df.iterrows():
            kaggle_id = clean_movie_id(row["id"])
            if not kaggle_id:
                continue

            # Get backdrop from TMDb API results (stored in poster_path)
            poster_url = movie_backdrops.get(kaggle_id)
            
            # Fallback to CSV poster_path if TMDb API didn't return anything
            if not poster_url and pd.notna(row.get("poster_path")):
                poster_path = row["poster_path"]
                poster_url = (
                    f"{POSTER_BASE_URL}{poster_path}"
                    if not poster_path.startswith("http")
                    else poster_path
                )

            # Extract genres
            genres_list = []
            if pd.notna(row["genres"]):
                matches_genre = re.findall(r"'name': '([^']+)'", row["genres"])
                if matches_genre:
                    genres_list = matches_genre
            genre_string = "|".join(genres_list)

            # Convert revenue to integer, handle invalid values
            revenue_value = None
            try:
                rev = row.get("revenue")
                if pd.notna(rev) and str(rev).strip():
                    revenue_value = int(float(str(rev)))
            except (ValueError, TypeError):
                pass  # Keep as None if conversion fails
            
            movie_dict = {
                "title": row.get("title"),
                "genre": genre_string,
                "overview": row.get("overview"),
                "release_date": row.get("release_date"),
                "poster_path": poster_url,  # This contains backdrop_path from TMDb
                "revenue": revenue_value,
                "runtime": row.get("runtime"),
                "original_language": row.get("original_language"),
            }
            # Store kaggle_id separately for mapping
            movie_dict["_kaggle_id"] = kaggle_id
            movies_to_add.append(movie_dict)

            if (i + 1) % 100 == 0:
                log.info(f"Processed {i + 1} movies so far...")

        # Insert movies using raw SQL with batch commits to avoid timeout
        log.info(f"Inserting {len(movies_to_add)} movies...")
        
        from sqlalchemy import text
        insert_sql = text("""
            INSERT INTO movies (title, genre, overview, release_date, poster_path, revenue, runtime, original_language)
            VALUES (:title, :genre, :overview, :release_date, :poster_path, :revenue, :runtime, :original_language)
            RETURNING id
        """)
        
        BATCH_COMMIT_SIZE = 5000  # Commit every 5000 to avoid Supabase timeout
        inserted_movies = []
        
        for batch_start in range(0, len(movies_to_add), BATCH_COMMIT_SIZE):
            batch_end = min(batch_start + BATCH_COMMIT_SIZE, len(movies_to_add))
            batch_movies = movies_to_add[batch_start:batch_end]
            
            with engine.begin() as conn:
                for idx, movie_dict in enumerate(batch_movies):
                    result = conn.execute(insert_sql, {
                        'title': movie_dict.get("title"),
                        'genre': movie_dict.get("genre"),
                        'overview': movie_dict.get("overview"),
                        'release_date': movie_dict.get("release_date"),
                        'poster_path': movie_dict.get("poster_path"),
                        'revenue': movie_dict.get("revenue"),
                        'runtime': movie_dict.get("runtime"),
                        'original_language': movie_dict.get("original_language"),
                    })
                    movie_id = result.scalar()
                    
                    # Create a minimal object for mapping
                    class MovieRef:
                        def __init__(self, movie_id):
                            self.id = movie_id
                    
                    inserted_movies.append((movie_dict, MovieRef(movie_id)))
                    
                    if (batch_start + idx + 1) % 1000 == 0:
                        log.info(f"  {batch_start + idx + 1}/{len(movies_to_add)} movies inserted")
            
            log.info(f"  ✅ Batch {batch_start}-{batch_end} committed ({batch_end}/{len(movies_to_add)})")
        
        log.info("Movies inserted successfully.")

        # Map Kaggle IDs to database IDs
        for movie_dict, movie_obj in inserted_movies:
            if "_kaggle_id" in movie_dict:
                kaggle_movie_id_to_db_id[movie_dict["_kaggle_id"]] = movie_obj.id

        total_movies = len(kaggle_movie_id_to_db_id)
        log.info(f"✅ Total Movies: {total_movies}")

        # --- Load Users ---
        log.info(f"Preparing users from {RATINGS_CSV}...")
        ratings_df = pd.read_csv(RATINGS_CSV)
        unique_user_ids = ratings_df["userId"].unique()
        
        # Create default users with hashed password
        from auth import get_password_hash
        default_password = get_password_hash("password123")  # Default password for all users
        
        users_to_add = [
            {
                "username": f"user_{int(uid)}",
                "hashed_password": default_password,
                "email": f"user_{int(uid)}@example.com",
                "_kaggle_id": uid
            }
            for uid in unique_user_ids
        ]

        # Insert users with small batch commits
        log.info(f"Inserting {len(users_to_add)} users...")
        
        COMMIT_BATCH_SIZE = 50
        inserted_users = []
        
        for idx, user_dict in enumerate(users_to_add):
            user_obj = models.User(
                username=user_dict.get("username"),
                hashed_password=user_dict.get("hashed_password"),
                email=user_dict.get("email"),
            )
            db.add(user_obj)
            inserted_users.append((user_dict, user_obj))
            
            # Commit every COMMIT_BATCH_SIZE records
            if (idx + 1) % COMMIT_BATCH_SIZE == 0:
                db.commit()
                log.info(f"  {idx + 1}/{len(users_to_add)} users inserted")
        
        # Final commit
        db.commit()
        log.info("Users inserted successfully.")

        for user_dict, user_obj in inserted_users:
            if "_kaggle_id" in user_dict:
                kaggle_user_id_to_db_id[user_dict["_kaggle_id"]] = user_obj.id

        total_users = len(kaggle_user_id_to_db_id)
        log.info(f"✅ Total Users: {total_users}")

        # --- Load Ratings ---
        log.info("Preparing ratings...")
        ratings_to_add = []
        skipped_ratings = 0
        
        for idx, row in ratings_df.iterrows():
            db_user_id = kaggle_user_id_to_db_id.get(row["userId"])
            db_movie_id = kaggle_movie_id_to_db_id.get(row["movieId"])
            if db_user_id and db_movie_id:
                ratings_to_add.append({
                    "user_id": db_user_id,
                    "movie_id": db_movie_id,
                    "rating": float(row["rating"]),
                })
            else:
                skipped_ratings += 1
            
            if (idx + 1) % 10000 == 0:
                log.info(f"Processed {idx + 1} ratings...")

        log.info(f"Skipped {skipped_ratings} ratings due to missing user/movie mappings")
        
        # Insert ratings with small batch commits
        log.info(f"Inserting {len(ratings_to_add)} ratings...")
        
        COMMIT_BATCH_SIZE = 1000  # Ratings can handle larger batches
        
        for idx, rating_dict in enumerate(ratings_to_add):
            rating_obj = models.Rating(
                user_id=rating_dict["user_id"],
                movie_id=rating_dict["movie_id"],
                rating=rating_dict["rating"],
            )
            db.add(rating_obj)
            
            # Commit every COMMIT_BATCH_SIZE records
            if (idx + 1) % COMMIT_BATCH_SIZE == 0:
                db.commit()
                log.info(f"  {idx + 1}/{len(ratings_to_add)} ratings inserted")
        
        # Final commit
        db.commit()
        total_ratings = len(ratings_to_add)
        log.info(f"✅ Total Ratings: {total_ratings}")

        # --- Summary ---
        log.info("---" * 10)
        log.info("✅ DATA LOAD SUMMARY")
        log.info(f"Movies:  {total_movies}")
        log.info(f"Users:   {total_users}")
        log.info(f"Ratings: {total_ratings}")
        log.info("---" * 10)

        time_taken = datetime.now() - start_time

        log.info(f"Time taken == {time_taken}")

    except Exception as e:
        log.error(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()
        log.info("Database session closed.")


if __name__ == "__main__":
    load_data()
