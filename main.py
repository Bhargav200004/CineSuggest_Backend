from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import user, movie, interaction, recommend, genre, auth


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
    return {"status": "healthy", "service": "movie-recommendation-api"}


