"""
Authentication router for user registration and login.
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import models
import schemas
from database import get_db
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    get_current_user
)
from exceptions import ConflictException, UnauthorizedException, NotFoundException

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - **username**: Unique username (required)
    - **email**: User email (optional)
    - **password**: Password (minimum 6 characters)
    - **full_name**: User's full name (optional)
    """
    # Check if username already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise ConflictException(resource="Username", message="Username already registered")
    
    # Check if email already exists (if provided)
    if user.email:
        db_email = db.query(models.User).filter(models.User.email == user.email).first()
        if db_email:
            raise ConflictException(resource="Email", message="Email already registered")
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login to get access and refresh tokens.
    
    - **username**: Your username
    - **password**: Your password
    
    Returns both access token (30 min expiry) and refresh token (7 days expiry).
    Use the refresh token to get a new access token without re-entering credentials.
    """
    # Find user by username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedException(message="Incorrect username or password")
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=schemas.UserProfile)
def get_my_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get the current authenticated user's profile.
    
    Requires authentication token in header:
    `Authorization: Bearer <token>`
    """
    # Count user's ratings and favorites
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


@router.post("/refresh", response_model=schemas.Token)
def refresh_access_token(token_data: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """
    Get a new access token using a refresh token.
    
    - **refresh_token**: Your refresh token from login
    
    Returns a new access token and refresh token pair.
    This allows users to stay logged in without re-entering credentials.
    """
    # Verify refresh token
    username = verify_refresh_token(token_data.refresh_token)
    
    if username is None:
        raise UnauthorizedException(message="Invalid or expired refresh token")
    
    # Verify user still exists
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise NotFoundException(resource="User")
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
