from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router =  APIRouter(
    tags=["Interactions"]
)

@router.post("/ratings", response_model=schemas.Rating)
def add_or_update_rating(rating: schemas.RatingCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == rating.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_movie = db.query(models.Movie).filter(models.Movie.id == rating.movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    if not (1 <= rating.rating <= 5):
        raise HTTPException(status_code=404, detail="Rating must be between 1 and 5")
    
    db_rating = db.query(models.Rating).filter(
        models.Rating.user_id == rating.user_id,
        models.Rating.movie_id == rating.movie_id
    ).first()

    if db_rating:
        db_rating.rating = rating.rating
    else:
        db_rating = models.Rating(**rating.model_dump())
        db.add(db_rating)

    db.commit()
    db.refresh(db_rating)
    return db_rating

@router.post("/favorites", response_model=schemas.Favorite)
def toggle_favorite(favorite: schemas.FavoriteCreate, db : Session = Depends(get_db)):
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == favorite.user_id,
        models.Favorite.movie_id == favorite.movie_id
    ).first()

    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return db_favorite
    else:
        db_user = db.query(models.User).filter(models.User.id == favorite.user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_movie = db.query(models.Movie).filter(models.Movie.id == favorite.movie_id).first()
        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        new_favorite = models.Favorite(**favorite.model_dump())
        db.add(new_favorite)
        db.commit()
        db.refresh(new_favorite)
        return new_favorite