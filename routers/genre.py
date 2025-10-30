from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db
from typing import List

router = APIRouter(
    prefix="/genres",
    tags=["Genres"]
)

@router.get("/", response_model=List[str])
def get_all_genres(db : Session = Depends(get_db)):
    all_movies = db.query(models.Movie.genre).all()

    unique_genres = set()

    for(genre_string,) in all_movies:
        genres = genre_string.split('|')
        for genre in genres:
            if genre and genre != "(no genres listed)":
                unique_genres.add(genre)

    return sorted(list(unique_genres))