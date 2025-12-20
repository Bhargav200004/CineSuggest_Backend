from fastapi import APIRouter, Depends, HTTPException , Query
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from sqlalchemy.sql.expression import func
from typing import List, Optional

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

@router.post("/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db : Session = Depends(get_db)):
    new_movie = models.Movie(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@router.get("/", response_model=List[schemas.Movie])
def get_all_movies(db : Session = Depends(get_db) , skip: int = 0, limit : int  = 100):
    movies = db.query(models.Movie).offset(skip).limit(limit=limit).all()
    return movies

@router.get("/{movie_id}", response_model=schemas.Movie)
def get_movie_by_id(movie_id , user_id: Optional[int] = Query(None) ,    db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    user_rating = 0
    is_fav = False

    if user_id:
        # Check rating
        rating_obj = db.query(models.Rating).filter(
            models.Rating.user_id == user_id, 
            models.Rating.movie_id == movie_id
        ).first()
        if rating_obj:
            user_rating = rating_obj.rating
        
        # Check favorite
        fav_obj = db.query(models.Favorite).filter(
            models.Favorite.user_id == user_id, 
            models.Favorite.movie_id == movie_id
        ).first()
        is_fav = fav_obj is not None

    movie.user_rating = user_rating
    movie.is_favorite = is_fav

    return movie


@router.get("/random" , response_model=List[schemas.Movie])
def get_random_movies(db: Session = Depends(get_db)):
    random_movies = db.query(models.Movie).order_by(func.random()).limit(10).all()
    return random_movies

# uvicorn main:app --reload --host 0.0.0.0 --port 8000