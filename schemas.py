from pydantic import BaseModel
from typing import List

class MovieBase(BaseModel):
    title: str
    genre: str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    user_id: int
    movie_id: int
    rating: int # Should be between 1 and 5

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int

    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    user_id: int
    movie_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendations: List[Movie]