from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import models, schemas
from database import get_db
from typing import List

router = APIRouter(
    prefix="/recommend",
    tags=["Recommendations"]
)

def get_recommendation_model(db: Session):
    all_ratings = db.query(models.Rating).all()
    all_favorites = db.query(models.Favorite).all()

    if not all_ratings and not all_favorites:
        return (None , None)
    
    master_ratings = {}

    for r in all_ratings:
        master_ratings[(r.user_id, r.movie_id)] = r.rating

    for f in all_favorites:
        master_ratings[(f.user_id , f.movie_id)] = 5.0

    data = pd.DataFrame(
        [
            {"user_id": user, "movie_id": movie, "rating" : rating}
            for (user, movie), rating in master_ratings.items()
        ]
    )

    reader = Reader(rating_scale=(1,5))
    dataset = Dataset.load_from_df(data[['user_id' , 'movie_id' , 'rating']], reader)

    trainset = dataset.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    return algo, trainset

@router.get("/{user_id}" , response_model=schemas.RecommendationResponse)
def get_recommendations_for_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, details="User not found")
    
    model, trainset = get_recommendation_model(db)

    if model is None:
        return {"recommendations" : []}
    
    all_movies = db.query(models.Movie).all()
    all_movies_ids = {movie.id for movie in all_movies}

    try:
        user_inner_id = trainset.to_inner_uid(user_id)
        seen_movie_inner_ids = [item_id for (item_id, _) in trainset.ur[user_inner_id]]
        seen_movie_raw_ids = {trainset.to_raw_iid(inner_id) for inner_id in seen_movie_inner_ids}
    except ValueError:
        seen_movie_raw_ids = set()


    movies_to_predict = all_movies_ids - seen_movie_raw_ids


    predictions = []
    for movie_id in movies_to_predict:
        pred = model.predict(uid = user_id, iid=movie_id)
        predictions.append((movie_id, pred.est))

    predictions.sort(key=lambda x: x[1], reverse=True)


    top_10_movie_ids = [movie_id for (movie_id, rating) in predictions[:10]]

    top_movies = db.query(models.Movie).filter(models.Movie.id.in_(top_10_movie_ids)).all()

    movie_map = {movie.id: movie for movie in top_movies}
    sorted_top_movies = [movie_map[movie_id] for movie_id in top_10_movie_ids if movie_id in movie_map]

    return {"recommendations" : sorted_top_movies}