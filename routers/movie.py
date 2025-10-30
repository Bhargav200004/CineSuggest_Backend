from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from sqlalchemy.sql.expression import func

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
def get_all_movies(db : Session = Depends(get_db)):
    movies = db.query(models.Movie).all()
    return movies

@router.get("/trending" , response_model=List[schemas.Movie])
def get_trending_movies(db: Session = Depends(get_db)):
    trending_movies = db.query(models.Movie).order_by(func.random()).limit(10).all()