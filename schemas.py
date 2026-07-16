from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# ============ Authentication Schemas ============
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ============ Movie Schemas ============
class MovieBase(BaseModel):
    title: str
    genre: str
    overview: Optional[str] = None
    revenue: Optional[int] = 0
    runtime: str
    original_language: str
    release_date: Optional[str] = None
    poster_path: Optional[str] = None

    user_rating: float = 0
    is_favorite: bool = False

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        from_attributes = True

class MoviesResponse(BaseModel):
    movies: List[Movie]

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    total_ratings: int = 0
    total_favorites: int = 0

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=0.5, le=5.0)  # Rating between 0.5 and 5.0

class RatingCreate(RatingBase):
    pass

class Rating(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float

    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    movie_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(BaseModel):
    id: int
    user_id: int
    movie_id: int

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendations: List[Movie]