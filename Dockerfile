FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV DATABASE_URL=postgresql://postgres.tjzdfqqiwtzldkytthgk:HnuwTvMuWx23TMM3@aws-1-ap-south-1.pooler.supabase.com:6543/postgres


# JWT Authentication
ENV SECRET_KEY=development-secret-key-change-in-production-9876543210
ENV ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV REFRESH_TOKEN_EXPIRE_DAYS=7

# TMDb API Key (for loading movie data)
ENV TMDB_API_KEY=438d4def824a39389f045cf20db32ab0

WORKDIR /movie_recommendation

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /movie_recommendation/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /movie_recommendation/requirements.txt

COPY . /movie_recommendation

EXPOSE 80

RUN useradd -m myappuser

USER myappuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]