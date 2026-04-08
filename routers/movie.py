from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import get_db
from sqlalchemy.sql.expression import func
from auth import get_current_user

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get("/", response_model=schemas.MoviesResponse)
def get_all_movies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    genre: Optional[str] = None,
    current_user: Optional[models.User] = Depends(lambda: None)  # Optional auth
):
    """
    Get all movies with optional filtering.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **genre**: Filter by genre (optional)
    """
    query = db.query(models.Movie)
    
    if genre:
        query = query.filter(models.Movie.genre.contains(genre))
    
    movies = query.offset(skip).limit(limit).all()
    
    # Add user-specific data if authenticated
    if current_user:
        for movie in movies:
            rating_obj = db.query(models.Rating).filter(
                models.Rating.user_id == current_user.id,
                models.Rating.movie_id == movie.id
            ).first()
            if rating_obj:
                movie.user_rating = rating_obj.rating
            
            fav_obj = db.query(models.Favorite).filter(
                models.Favorite.user_id == current_user.id,
                models.Favorite.movie_id == movie.id
            ).first()
            movie.is_favorite = fav_obj is not None
    
    return {"movies": movies}


@router.get("/random", response_model=List[schemas.Movie])
def get_random_movies(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user: Optional[models.User] = Depends(lambda: None)
):
    """
    Get random movies for discovery.
    
    - **limit**: Number of random movies to return (default: 10)
    """
    random_movies = db.query(models.Movie).order_by(func.random()).limit(limit).all()
    
    # Add user-specific data if authenticated
    if current_user:
        for movie in random_movies:
            rating_obj = db.query(models.Rating).filter(
                models.Rating.user_id == current_user.id,
                models.Rating.movie_id == movie.id
            ).first()
            if rating_obj:
                movie.user_rating = rating_obj.rating
            
            fav_obj = db.query(models.Favorite).filter(
                models.Favorite.user_id == current_user.id,
                models.Favorite.movie_id == movie.id
            ).first()
            movie.is_favorite = fav_obj is not None
    
    return random_movies


@router.get("/search", response_model=schemas.MoviesResponse)
def search_movies(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: Optional[models.User] = Depends(lambda: None)
):
    """
    Search movies by title.
    
    - **q**: Search query string
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    movies = db.query(models.Movie).filter(
        models.Movie.title.contains(q)
    ).offset(skip).limit(limit).all()
    
    # Add user-specific data if authenticated
    if current_user:
        for movie in movies:
            rating_obj = db.query(models.Rating).filter(
                models.Rating.user_id == current_user.id,
                models.Rating.movie_id == movie.id
            ).first()
            if rating_obj:
                movie.user_rating = rating_obj.rating
            
            fav_obj = db.query(models.Favorite).filter(
                models.Favorite.user_id == current_user.id,
                models.Favorite.movie_id == movie.id
            ).first()
            movie.is_favorite = fav_obj is not None
    
    return {"movies": movies}


@router.get("/{movie_id}", response_model=schemas.Movie)
def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(lambda: None)
):
    """
    Get a specific movie by ID with user-specific data (if authenticated).
    
    - **movie_id**: ID of the movie
    """
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    user_rating = 0
    is_fav = False

    if current_user:
        # Check rating
        rating_obj = db.query(models.Rating).filter(
            models.Rating.user_id == current_user.id,
            models.Rating.movie_id == movie_id
        ).first()
        if rating_obj:
            user_rating = rating_obj.rating
        
        # Check favorite
        fav_obj = db.query(models.Favorite).filter(
            models.Favorite.user_id == current_user.id,
            models.Favorite.movie_id == movie_id
        ).first()
        is_fav = fav_obj is not None

    movie.user_rating = user_rating
    movie.is_favorite = is_fav

    return movie