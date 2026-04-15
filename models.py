from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Float, BigInteger
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)

    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan") 
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    genre = Column(String)

    overview = Column(String)
    release_date = Column(String)
    poster_path = Column(String)  # Using backdrop_path from TMDb
    revenue = Column(BigInteger, nullable=True)  # BIGINT to handle large revenues like Avatar ($2.78B)
    runtime = Column(String)
    original_language = Column(String)

    ratings = relationship("Rating" , back_populates="movie")
    favorites = relationship("Favorite" , back_populates="movie")

class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    rating = Column(Float)  # Changed to Float to support 0.5 increments (1.0 to 5.0)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_fav_uc'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="favorites")
    movie = relationship("Movie", back_populates="favorites")