from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    # Fixed typo: 'rating' -> 'ratings'
    ratings = relationship("Rating", back_populates="user") 
    favorites = relationship("Favorite" , back_populates="user")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String)

    overview = Column(String)
    release_date = Column(String)
    poster_path = Column(String) 

    ratings = relationship("Rating" , back_populates="movie")
    favorites = relationship("Favorite" , back_populates="movie")

class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint('user_id' , 'movie_id' , name='_user_movie_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating = Column(Integer)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint('user_id' , 'movie_id', name='_user_movie_fav_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("User" , back_populates="favorites")
    movie = relationship("Movie" , back_populates="favorites")