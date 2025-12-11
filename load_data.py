import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import logging
import re
import asyncio
import aiohttp
from datetime import datetime

# --- Configuration ---
METADATA_CSV = "movies_metadata.csv"
RATINGS_CSV = "ratings_small.csv"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_API_KEY = "0248e4a7336b921b867f98eb4ffc39cd"  # your TMDb API key
TMDB_FIND_URL = "https://api.themoviedb.org/3/find/{}?api_key={}&external_source=imdb_id"

# --- Logging ---
logging.basicConfig(level=logging.INFO)
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

        imdb_ids = movies_df["imdb_id"].dropna().unique().tolist()
        log.info(f"Fetching posters for {len(imdb_ids)} movies asynchronously...")

        # Fetch all posters concurrently
        posters =  asyncio.run(fetch_all_posters(imdb_ids))
        log.info("Poster fetching complete.")

        movies_to_add = []

        for i, row in movies_df.iterrows():
            kaggle_id = clean_movie_id(row["id"])
            if not kaggle_id:
                continue

            imdb_id = row.get("imdb_id")
            poster_url = posters.get(imdb_id)

            # Fallback to dataset poster_path if TMDb API fails
            if not poster_url and pd.notna(row.get("poster_path")):
                poster_url = (
                    f"{POSTER_BASE_URL}{row['poster_path']}"
                    if not row["poster_path"].startswith("http")
                    else row["poster_path"]
                )

            # Extract genres
            genres_list = []
            if pd.notna(row["genres"]):
                matches_genre = re.findall(r"'name': '([^']+)'", row["genres"])
                if matches_genre:
                    genres_list = matches_genre
            genre_string = "|".join(genres_list)

            movie_dict = {
                "title": row.get("title"),
                "genre": genre_string,
                "overview": row.get("overview"),
                "release_date": row.get("release_date"),
                "revenue" : row.get("revenue"),
                "runtime" : row.get("runtime"),
                "original_language" : row.get("original_language"),
                "poster_path": poster_url,
                "_kaggle_id": kaggle_id,
            }
            movies_to_add.append(movie_dict)

            if (i + 1) % 100 == 0:
                log.info(f"Processed {i + 1} movies so far...")

        log.info(f"Inserting {len(movies_to_add)} movies...")
        db.bulk_insert_mappings(models.Movie, movies_to_add, return_defaults=True)
        db.commit()
        log.info("Movies inserted successfully.")

        for movie_dict in movies_to_add:
            kaggle_movie_id_to_db_id[movie_dict["_kaggle_id"]] = movie_dict["id"]

        total_movies = len(kaggle_movie_id_to_db_id)
        log.info(f"✅ Total Movies: {total_movies}")

        # --- Load Users ---
        log.info(f"Preparing users from {RATINGS_CSV}...")
        ratings_df = pd.read_csv(RATINGS_CSV)
        unique_user_ids = ratings_df["userId"].unique()
        users_to_add = [
            {"username": f"user_{int(uid)}", "_kaggle_id": uid} for uid in unique_user_ids
        ]

        db.bulk_insert_mappings(models.User, users_to_add, return_defaults=True)
        db.commit()

        for user_dict in users_to_add:
            kaggle_user_id_to_db_id[user_dict["_kaggle_id"]] = user_dict["id"]

        total_users = len(kaggle_user_id_to_db_id)
        log.info(f"✅ Total Users: {total_users}")

        # --- Load Ratings ---
        log.info("Preparing ratings...")
        ratings_to_add = []
        for _, row in ratings_df.iterrows():
            db_user_id = kaggle_user_id_to_db_id.get(row["userId"])
            db_movie_id = kaggle_movie_id_to_db_id.get(row["movieId"])
            if db_user_id and db_movie_id:
                ratings_to_add.append(
                    models.Rating(
                        user_id=db_user_id,
                        movie_id=db_movie_id,
                        rating=int(row["rating"]),
                    )
                )

        db.bulk_save_objects(ratings_to_add)
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
