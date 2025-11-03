import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite database URL.
# This will create a file named 'movies.db' in the same directory.

SQLALCHEMY_DATABASE_URL =  os.environ.get(
    "DATABASE_URL",
    "sqlite:///./movies.db"
    )

if SQLALCHEMY_DATABASE_URL.startswith("postgres"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread" : False}
    )

SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()