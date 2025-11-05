import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import logging
import re

# Set up basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- Configuration ---
METADATA_CSV = "movies_metadata.csv"
RATINGS_CSV = "ratings_small.csv" # <-- Use the SMALL file
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

def clean_movie_id(id_str):
    """Cleans the movie ID from the metadata file."""
    try:
        return int(id_str)
    except ValueError:
        return None

def load_data():
    log.info("Dropping and re-creating database tables...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    kaggle_movie_id_to_db_id = {}
    kaggle_user_id_to_db_id = {}
    
    total_movies = 0
    total_users = 0
    total_ratings = 0

    try:
        # --- 1. Load Movies (BATCHED) ---
        log.info(f"Preparing movies from {METADATA_CSV}...")
        movies_df = pd.read_csv(METADATA_CSV, dtype='object')
        
        movies_to_add = [] # List to hold all movie dictionaries
        
        for _, row in movies_df.iterrows():
            kaggle_id = clean_movie_id(row['id'])
            if not kaggle_id:
                continue

            poster_url = None
            if pd.notna(row['poster_path']):
                poster_url = f"{POSTER_BASE_URL}{row['poster_path']}"

            genres_list = []
            if pd.notna(row['genres']):
                matches = re.findall(r"'name': '([^']+)'", row['genres'])
                if matches:
                    genres_list = matches
            
            genre_string = "|".join(genres_list)

            # Create a dictionary, not an object
            movie_dict = {
                "title": row['title'],
                "genre": genre_string,
                "overview": row['overview'],
                "release_date": row['release_date'],
                "poster_path": poster_url,
                "_kaggle_id": kaggle_id # Temporary key to build map
            }
            movies_to_add.append(movie_dict)
        
        log.info(f"Inserting {len(movies_to_add)} movies in a single batch...")
        # Use bulk_insert_mappings to insert all at once
        # return_defaults=True fetches the new primary keys
        db.bulk_insert_mappings(models.Movie, movies_to_add, return_defaults=True)
        db.commit()
        log.info("Movie batch insert complete.")

        # Now, build the map from the updated dictionaries
        for movie_dict in movies_to_add:
            kaggle_movie_id_to_db_id[movie_dict['_kaggle_id']] = movie_dict['id']
            
        total_movies = len(kaggle_movie_id_to_db_id)
        log.info(f"Successfully mapped {total_movies} movies.")


        # --- 2. Load Users (BATCHED) ---
        log.info(f"Preparing users from {RATINGS_CSV}...")
        ratings_df = pd.read_csv(RATINGS_CSV)
        
        unique_user_ids = ratings_df['userId'].unique()
        users_to_add = [] # List to hold all user dictionaries
        
        for user_id in unique_user_ids:
            user_dict = {
                "username": f"user_{int(user_id)}",
                "_kaggle_id": user_id # Temporary key
            }
            users_to_add.append(user_dict)
            
        log.info(f"Inserting {len(users_to_add)} users in a single batch...")
        db.bulk_insert_mappings(models.User, users_to_add, return_defaults=True)
        db.commit()
        log.info("User batch insert complete.")

        # Build the user map
        for user_dict in users_to_add:
            kaggle_user_id_to_db_id[user_dict['_kaggle_id']] = user_dict['id']
            
        total_users = len(kaggle_user_id_to_db_id)
        log.info(f"Successfully mapped {total_users} users.")


        # --- 3. Load Ratings (Already Batched) ---
        log.info("Preparing ratings...")
        
        ratings_to_add = []
        for _, row in ratings_df.iterrows():
            db_user_id = kaggle_user_id_to_db_id.get(row['userId'])
            db_movie_id = kaggle_movie_id_to_db_id.get(row['movieId'])
            
            if db_user_id and db_movie_id:
                # We create objects here, which is fine for bulk_save_objects
                new_rating = models.Rating(
                    user_id=db_user_id,
                    movie_id=db_movie_id,
                    rating=int(row['rating'])
                )
                ratings_to_add.append(new_rating)

        log.info(f"Inserting {len(ratings_to_add)} ratings in a single batch...")
        db.bulk_save_objects(ratings_to_add) # This is also a batch operation
        db.commit()
        total_ratings = len(ratings_to_add)
        log.info("Rating batch insert complete.")


        # --- 4. FINAL SUMMARY ---
        log.info("---" * 10)
        log.info("✅ DATA LOAD SUMMARY")
        log.info(f"Total Movies:   {total_movies}")
        log.info(f"Total Users:    {total_users}")
        log.info(f"Total Ratings:  {total_ratings}")
        log.info("---" * 10)


    except Exception as e:
        log.error(f"An error occurred: {e}")
        log.error("Rolling back changes...")
        db.rollback()
    finally:
        db.close()
        log.info("Database session closed.")

if __name__ == "__main__":
    load_data()