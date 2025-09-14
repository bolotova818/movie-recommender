from films_model import Film
from recommend_v3 import recommend_films, films
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Movie Recommender API", version="0.1")

# разрешаем фронту стучаться к бэку (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Схемы данных для валидации
class RecommendRequest(BaseModel):
    liked_titles: list[str]
    top_n: int = 10

class FilmResponse(BaseModel):
    title: str
    year: int | None
    description: str
    director: str
    actors: list[str]
    country: list[str]
    rating: float | None 

class RecommendResponse(BaseModel):
    recommendations: list[FilmResponse]


def normalize_title(s: str) -> str:
    return s.strip().lower()

# мапа для быстрого поиска фильмов по названию
title2film: dict[str, Film] = {
    normalize_title(film.title): film
    for film in films
}

# превращаем список названий в список объектов Film
def select_films_by_titles(titles: list[str]) -> list[Film]:
    not_found = [t for t in titles if normalize_title(t) not in title2film]
    if not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Фильмы не найдены: {', '.join(not_found)}"
        )
    return [title2film[normalize_title(title)] for title in titles]

# Эндпоинты 
@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    # берём фильмы по названиям и прогоняем через recommend_films
    liked_films = select_films_by_titles(req.liked_titles)
    recommendations = recommend_films(liked_films, films)

    # топ-N фильмов
    top_films = [film for film, _ in recommendations[:req.top_n]]

    response = [
        FilmResponse(
            title=film.title,
            year=film.year,
            description=film.description,
            director=film.director,
            actors=film.actors,
            country=film.country,
            rating=film.rating
        )
        for film in top_films
    ]

    return RecommendResponse(recommendations=response)


@app.get("/films/random", response_model=List[FilmResponse])
def get_random_films(limit: int = 30):
    # отдаём случайные фильмы для фронта
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be positive")

    n = min(limit, len(films))
    sample_films = random.sample(films, n)

    return [
        FilmResponse(
            title=f.title,
            year=f.year,
            description=f.description,
            director=f.director,
            actors=f.actors,
            country=f.country,
            rating=f.rating
        )
        for f in sample_films
    ]
