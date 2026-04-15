from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from auth import get_current_user
from exceptions import NotFoundException, ConflictException

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)


@router.post("/ratings", response_model=schemas.Rating)
def add_or_update_rating(
    rating: schemas.RatingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add or update a movie rating for the authenticated user.
    
    - **movie_id**: ID of the movie to rate
    - **rating**: Rating value (0.5 to 5.0)
    """
    # Check if movie exists
    db_movie = db.query(models.Movie).filter(models.Movie.id == rating.movie_id).first()
    if not db_movie:
        raise NotFoundException(resource="Movie", identifier=str(rating.movie_id))
    
    # Check for existing rating
    db_rating = db.query(models.Rating).filter(
        models.Rating.user_id == current_user.id,
        models.Rating.movie_id == rating.movie_id
    ).first()

    if db_rating:
        # Update existing rating
        db_rating.rating = rating.rating
    else:
        # Create new rating
        db_rating = models.Rating(
            user_id=current_user.id,
            movie_id=rating.movie_id,
            rating=rating.rating
        )
        db.add(db_rating)

    db.commit()
    db.refresh(db_rating)
    return db_rating


@router.delete("/ratings/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    movie_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a rating for a specific movie.
    """
    db_rating = db.query(models.Rating).filter(
        models.Rating.user_id == current_user.id,
        models.Rating.movie_id == movie_id
    ).first()
    
    if not db_rating:
        raise NotFoundException(resource="Rating")
    
    db.delete(db_rating)
    db.commit()
    return None


@router.post("/favorites", response_model=schemas.Favorite, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite: schemas.FavoriteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a movie to favorites for the authenticated user.
    
    - **movie_id**: ID of the movie to favorite
    """
    # Check if movie exists
    db_movie = db.query(models.Movie).filter(models.Movie.id == favorite.movie_id).first()
    if not db_movie:
        raise NotFoundException(resource="Movie", identifier=str(favorite.movie_id))
    
    # Check if already favorited
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.movie_id == favorite.movie_id
    ).first()

    if db_favorite:
        raise ConflictException(resource="Favorite", message="Movie already in favorites")
    
    # Add to favorites
    new_favorite = models.Favorite(
        user_id=current_user.id,
        movie_id=favorite.movie_id
    )
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite


@router.delete("/favorites/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    movie_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a movie from favorites for the authenticated user.
    """
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.movie_id == movie_id
    ).first()

    if not db_favorite:
        raise NotFoundException(resource="Favorite")
    
    db.delete(db_favorite)
    db.commit()
    return None


@router.get("/favorites", response_model=schemas.MoviesResponse)
def get_my_favorites(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all favorited movies for the authenticated user.
    """
    favorites = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    movie_ids = [fav.movie_id for fav in favorites]
    movies = db.query(models.Movie).filter(models.Movie.id.in_(movie_ids)).all()
    
    # Mark all as favorites and add ratings
    for movie in movies:
        movie.is_favorite = True
        rating_obj = db.query(models.Rating).filter(
            models.Rating.user_id == current_user.id,
            models.Rating.movie_id == movie.id
        ).first()
        if rating_obj:
            movie.user_rating = rating_obj.rating
    
    return {"movies": movies}


@router.get("/ratings", response_model=list[schemas.Rating])
def get_my_ratings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all ratings by the authenticated user.
    """
    ratings = db.query(models.Rating).filter(
        models.Rating.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return ratings