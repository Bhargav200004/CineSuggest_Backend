import os

# 1. Redirect surprise's dataset folder to the writable /tmp directory
os.environ['SURPRISE_DATA_FOLDER'] = '/tmp/surprise_data'

# 2. Suppress the joblib shared memory warning (forces serial mode)
os.environ['JOBLIB_MULTIPROCESSING'] = '0'

from fastapi import FastAPI
from database import engine
import models
from routers import user, movie, interaction, recommend , genre


models.Base.metadata.create_all(bind = engine)

app = FastAPI(
    title="Movie Recommendation API",
    description="A simple backend for an Android movie recommendation app.",
    version="1.0.0"
)

app.include_router(user.router)
app.include_router(movie.router)
app.include_router(interaction.router)
app.include_router(recommend.router)
app.include_router(genre.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Recommendation API"}

