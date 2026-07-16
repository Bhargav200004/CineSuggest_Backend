import os

# 1. Redirect surprise's dataset folder to the writable /tmp directory
os.environ['SURPRISE_DATA_FOLDER'] = '/tmp/surprise_data'

# 2. Suppress the joblib shared memory warning (forces serial mode)
os.environ['JOBLIB_MULTIPROCESSING'] = '0'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import user, movie, interaction, recommend, genre, auth
from error_handlers import register_error_handlers
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Recommendation API",
    description="A movie recommendation backend with authentication, ratings, and personalized recommendations.",
    version="2.0.0",
    contact={
        "name": "API Support",
        "email": "support@movieapi.com",
    },
    license_info={
        "name": "MIT",
    }
)

# Register global error handlers
register_error_handlers(app)
logger.info("Global error handlers registered")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(movie.router)
app.include_router(interaction.router)
app.include_router(recommend.router)
app.include_router(genre.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint with API information.
    """
    return {
        "success": True,
        "message": "Welcome to the Movie Recommendation API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "success": True,
        "status": "healthy",
        "service": "movie-recommendation-api"
    }


