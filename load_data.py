import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models # This imports your models.py file
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# CSV file paths
MOVIES_CSV = "movies.csv"
RATINGS_CSV = "ratings.csv"

def load_data():
    # Re-create all tables (good for a fresh start)
    log.info("Dropping and re-creating database tables...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    # --- Mappings ---
    # To map MovieLens's IDs to our database's auto-incrementing IDs
    movielens_id_to_db_id = {}
    movielens_user_id_to_db_id = {}

    try:
        # --- 1. Load Movies ---
        log.info(f"Loading movies from {MOVIES_CSV}...")
        movies_df = pd.read_csv(MOVIES_CSV)
        
        for _, row in movies_df.iterrows():
            # Create a new Movie object
            new_movie = models.Movie(
                title=row['title'],
                genre=row['genres'] # Our model stores all genres as a single string
            )
            db.add(new_movie)
            db.commit() # Commit to get the new auto-incremented ID
            db.refresh(new_movie)
            
            # Store the mapping
            movielens_id_to_db_id[row['movieId']] = new_movie.id
            
        log.info(f"Successfully loaded {len(movielens_id_to_db_id)} movies.")

        # --- 2. Load Users ---
        log.info(f"Loading users and ratings from {RATINGS_CSV}...")
        ratings_df = pd.read_csv(RATINGS_CSV)
        
        # Get all unique user IDs from MovieLens
        unique_user_ids = ratings_df['userId'].unique()
        
        for user_id in unique_user_ids:
            # Create a new User object
            new_user = models.User(
                username=f"user_{int(user_id)}" # Create a simple username
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Store the mapping
            movielens_user_id_to_db_id[user_id] = new_user.id
            
        log.info(f"Successfully created {len(movielens_user_id_to_db_id)} users.")

        # --- 3. Load Ratings ---
        log.info("Loading ratings... (this may take a minute)")
        
        # Use a generator for efficiency (optional, but good practice)
        ratings_to_add = []
        for _, row in ratings_df.iterrows():
            db_user_id = movielens_user_id_to_db_id.get(row['userId'])
            db_movie_id = movielens_id_to_db_id.get(row['movieId'])
            
            # Only add if both user and movie were successfully mapped
            if db_user_id and db_movie_id:
                new_rating = models.Rating(
                    user_id=db_user_id,
                    movie_id=db_movie_id,
                    rating=int(row['rating'])
                )
                ratings_to_add.append(new_rating)

        # Add all ratings in bulk (much faster)
        db.bulk_save_objects(ratings_to_add)
        db.commit()
        log.info(f"Successfully loaded {len(ratings_to_add)} ratings.")

    except Exception as e:
        log.error(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
        log.info("Data loading complete. Database session closed.")

if __name__ == "__main__":
    load_data()