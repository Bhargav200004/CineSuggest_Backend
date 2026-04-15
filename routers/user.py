from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from auth import get_current_user
from exceptions import NotFoundException

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=schemas.UserProfile)
def get_my_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get the current authenticated user's profile with statistics.
    """
    total_ratings = db.query(models.Rating).filter(models.Rating.user_id == current_user.id).count()
    total_favorites = db.query(models.Favorite).filter(models.Favorite.user_id == current_user.id).count()
    
    return schemas.UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        total_ratings=total_ratings,
        total_favorites=total_favorites
    )


@router.get("/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise NotFoundException(resource="User", identifier=str(user_id))
    return user


@router.get("/", response_model=List[schemas.User])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users (paginated).
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users