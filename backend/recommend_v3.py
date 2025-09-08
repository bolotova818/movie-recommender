"""
Версия 3 рекомендательной системы фильмов.

Использована библиотека scikit-learn:
- TfidfVectorizer строит матрицу TF-IDF для всех описаний
- cosine_similarity быстро считает близость векторов
- результат намного быстрее и надёжнее, чем ручная реализация
Признаки кроме описания считаются как и в предыдущих версиях

+ добавлены умные веса и этапы перебора фильмов(сначала по описанию, после по остальным признакам)
"""

from films_model import Film
from data_loader import load_films_from_csv
from typing import List
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

films = load_films_from_csv("data/kinopoisk-top250.csv")
descriptions = [film.description for film in films]
russian_stop_words = [
     "и","в","во","не","что","он","на","я","с","со","как","а","то","все","она","так",
    "его","но","да","ты","к","у","же","вы","за","бы","по","только","ее","мне","было",
    "вот","от","меня","еще","нет","о","из","ему","теперь","когда","даже","ну","вдруг",
    "ли","если","уже","или","ни","быть","был","него","до","вас","нибудь","опять","уж",
    "вам","ведь","там","потом","себя","ничего","ей","может","они","тут","где","есть",
    "надо","ней","для","мы","тебя","их","чем","была","сам","чтоб","без","будто","чего",
    "раз","тоже","себе","под","будет","ж","тогда","кто","этот","того","потому","этого",
    "какой","совсем","ним","здесь","этом","один","почти","мой","тем","чтобы","нее",
    "кажется","сейчас","были","куда","зачем","всех","никогда","можно","при","наконец",
    "два","об","другой","хоть","после","над","больше","тот","через","эти","нас","про",
    "них","какая","много","разве","три","эту","моя","впрочем","хорошо","свою","этой",
    "перед","иногда","лучше","чуть","том","нельзя","такой","им","более","всегда",
    "конечно","всю","между"
]
vectorizer = TfidfVectorizer(stop_words=russian_stop_words)
tfidf_matrix = vectorizer.fit_transform(descriptions)



def compare_actors(user_actors: list[str], film_actors: list[str]) -> float:     
    """
    Считает долю совпавших актёров (индекс Жаккара).
    1.0 — если все совпали, 0.0 — если совсем разных нет.
    """
    intersection = len(set(user_actors)&set(film_actors))
    
    union = len(set(user_actors) | set(film_actors))

    score = intersection/union
    return score

def compare_director(user_directors: list[str], film_director: str) -> float:  
    """
    Проверяет: режиссёр фильма входит в список любимых или нет.
    Если совпал — ставит 1.0, если нет — 0.0.
    """      
    score = 1.0 if film_director in user_directors else 0.0
    return score


def compare_ratings(user_ratings: list[float], film_rating: float) -> float:   
    """
    Сравнивает средний рейтинг любимых фильмов с рейтингом этого фильма.
    Чем ближе цифры, тем больше балл (максимум = 1).
    Если разница больше 3 баллов — считает совпадение минимальным.
    """     
    MAX_DIFF = 3.0
    user_avg_rating = sum(user_ratings) / len(user_ratings)
    diff = abs(film_rating - user_avg_rating)
    score = 1.0 - min(diff, MAX_DIFF) / MAX_DIFF
    return score


def compare_years(user_years: list[int], film_year: int) -> float:                    
    """
    Сравнивает средний год любимых фильмов с годом выхода этого фильма.
    Чем ближе по времени, тем выше балл (от 0 до 1).
    """
    MAX_DIFF = 30
    user_avg_year = sum(user_years) / len(user_years)
    diff = abs(film_year - user_avg_year)
    score = 1.0 - min(diff, MAX_DIFF) / MAX_DIFF
    return score

def user_tfidf_vector(user_indices: List[int], tfidf_matrix: csr_matrix) -> csr_matrix:
    """
    Строит TF-IDF вектор пользователя.
    Берет строки tfidf_matrix по индексам любимых фильмов и усредняю.
    На выходе csr_matrix формы (1, vocab_size).
    .mean(axis=0) возвращает numpy.matrix, поэтому приводит к csr_matrix
"""
    user_vec = csr_matrix(tfidf_matrix[user_indices].mean(axis=0))
    return user_vec

def compare_description(user_vec: csr_matrix, tfidf_matrix: csr_matrix, film_index: int) -> float:
    """
    Считает похожесть по описанию.
    Сравнивает вектор пользователя с вектором одного фильма по индексу.
    Возвращает число от 0.0 до 1.0.
    user_vec и film_vec должны быть csr_matrix, возвращается float
"""

    film_vec = tfidf_matrix[film_index]
    cos_sim = cosine_similarity(user_vec, film_vec)  
    return round(float(cos_sim[0, 0]), 3)


TOP_K = 100          # Количество фильмов, отобранных по признаку описания

def top_k_by_description(user_indices: List[int], matrix: csr_matrix, k: int = TOP_K):
    """
    Выбирает кандидатов по описанию (TF-IDF).
    Берет средний вектор пользователя и считает косинус со всеми фильмами.
    Возвращает индексы топ-k и массив похожестей (чтобы потом не считать заново).
    """
    user_vec = user_tfidf_vector(user_indices, matrix)
    sims = cosine_similarity(user_vec, matrix).ravel()
    order = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
    top_idx = order[:min(k, len(order))]
    return top_idx, sims


def adapt_weights(base: dict[str, float],user_years: list[int],
                  user_ratings: list[float],user_actors: list[str],) -> dict[str, float]:
    """
    Функция умных весов
    Чуть подстраивает веса под профиль.
    - годы «рядом» - год важнее
    - рейтинги «рядом» - рейтинг важнее
    - актёры повторяются -актёры важнее
    Потом нормализует к сумме 1.0
    """
    import statistics

    w = base.copy()

    if len(user_years) >= 2:
        std_year = statistics.pstdev(user_years)
        if std_year <= 8:
            w["year"] += 0.05
        elif std_year >= 20:
            w["year"] -= 0.05

    if len(user_ratings) >= 2:
        std_rating = statistics.pstdev(user_ratings)
        if std_rating <= 0.4:
            w["rating"] += 0.05
        elif std_rating >= 1.0:
            w["rating"] -= 0.05

    repeats = len(user_actors) - len(set(user_actors))
    if repeats >= 2:
        w["actors"] += 0.05

    total = sum(max(0.0, v) for v in w.values()) or 1.0
    for key in list(w.keys()):
        w[key] = max(0.0, w[key]) / total
    return w


TITLE_TO_IDX = {f.title: i for i, f in enumerate(films)}

def recommend_films(user_liked_films: list[Film], films: list[Film]) -> list[tuple[Film, float]]:
    """
    Главная функция: собирает все признаки (жанры, актёры, описание и т.д.)
    и считает итоговый балл для каждого фильма.
    На выходе — список фильмов, отсортированный по убыванию похожести.
    """

    user_directors = [film.director for film in user_liked_films]
    user_actors = [actor for film in user_liked_films for actor in film.actors]
    user_ratings = [film.rating for film in user_liked_films]
    user_years = [film.year for film in user_liked_films]
    user_titles = {film.title for film in user_liked_films}


    user_indices = [TITLE_TO_IDX[t] for t in user_titles if t in TITLE_TO_IDX]


    base_w = {"desc": 0.40, "actors": 0.25, "director": 0.15, "year": 0.10, "rating": 0.10}
    w = adapt_weights(base_w, user_years, user_ratings, user_actors)

    top_idx, sims = top_k_by_description(user_indices, tfidf_matrix, k=TOP_K)

    recommendations = []
    for idx in top_idx:
        film = films[idx]
        if film.title in user_titles:
            continue  # не советуем то, что уже выбрано

        director_score = compare_director(user_directors, film.director)
        actors_score = compare_actors(user_actors, film.actors)
        rating_score = compare_ratings(user_ratings, film.rating)
        years_score = compare_years(user_years, film.year)
        description_score = float(sims[idx])  

        score = (
            w["director"] * director_score
            + w["actors"] * actors_score
            + w["rating"] * rating_score
            + w["year"] * years_score
            + w["desc"] * description_score
        )
        recommendations.append((film, round(float(score), 3)))

    sorted_recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    return sorted_recommendations


