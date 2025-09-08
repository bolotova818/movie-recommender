"""
Версия 2 рекомендательной системы фильмов.

Реализация TF-IDF "вручную"
- считаются частоты слов (TF)
- вычисляется обратная частота документов (IDF)
- тексты фильмов сравниваются по косинусной близости TF-IDF векторов

 Остальные признаки аналогичны 1 версии
"""

from math import sqrt, log
from collections import Counter
from films_model import Film
from data_loader import load_films_from_csv

films = load_films_from_csv("data/kinopoisk-top250.csv")


def compare_genres(user_genres: list[str], film_genres: list[str]) -> float:      
    """
    Смотрит, сколько жанров у фильма совпадает с теми, что нравятся пользователю.
    Использует индекс Жаккара: общие жанры делим на все жанры вместе.
    Возвращает число от 0.0 до 1.0.
    """
    intersection = len(set(user_genres)&set(film_genres))
    
    union = len(set(user_genres) | set(film_genres))

    score = round((intersection/union), 2)
    return score

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

stop_words = [
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а",
    "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же",
    "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот",
    "от", "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда",
    "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть",
    "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь",
    "там", "потом", "себя", "ничего", "ей", "может", "они", "тут",
    "где", "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем",
    "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже",
    "себе", "под", "будет", "ж", "тогда", "кто", "этот"
]
stop_symbols = [                                                                                    
    ".", ",", "!", "?", ":", ";", "-", "—", "(", ")", "[", "]", "{", "}",                    
    "\"", "'", "«", "»", "…", "/", "\\", "|", "@", "#", "$", "%", "^", "&", 
    "*", "_", "+", "=", "<", ">", "~", "`"
]

def extract_keywords(description: str) -> list[str]:
    """
    Берет описание фильма, очищаю от знаков и стоп-слов.
    На выходе список слов  - не множество, как в 1 версии проекта - (сохраняются повторы, чтобы можно было считать TF).
    """
    description = description.lower()
    for symbol in stop_symbols:
        description = description.replace(symbol, "")
    
    words = description.split()
    keywords = [word for word in words if word not in stop_words]
    
    return keywords


def build_vocab(films: list[Film]) -> dict[str, int]:    
    """
    Собирает словарь из всех уникальных слов в описаниях фильмов.
    Каждому слову присваивает свой индекс.
    """                                                                         
    my_dict = set()
    for f in films:
        key_words = extract_keywords(f.description)
        my_dict = my_dict | set(key_words)
    my_dict = {value: index for index, value in enumerate(my_dict)}
    return my_dict

def compute_idf(vocab: dict[str, int], films: list[Film]) -> dict[int, float]:
    """
    Считает IDF для всех слов словаря.
    Формула: idf = log((N+1) / (df+1)) + 1,
    где N — количество фильмов,
    df — количество фильмов, где встретилось слово.
"""

    n = len(films)
    idf_dict = {}
    for key, value in vocab.items():
        word_count = 0
        for film in films:
            ex_w = set(extract_keywords(film.description))
            if key in ex_w:
                word_count+=1
        idf_dict[value] = log((n + 1) / (word_count + 1)) + 1
    return idf_dict


def film_tfidf_vector(film: Film, vocab: dict[str, int], idf_dict: dict[int, float]) -> dict[int, float]:
    """
    Строит TF–IDF вектор для фильма.
    На выходе словарь {id_слова: tf-idf вес}.
    """
    words_list = extract_keywords(film.description)  
    counts = Counter(words_list)
    total_words = sum(counts.values())

    tf_idf_dict = {}
    for word, count in counts.items():
        if word in vocab:  
            word_id = vocab[word]
            tf = count / total_words
            idf = idf_dict[word_id]  
            tf_idf_dict[word_id] = tf * idf

    return tf_idf_dict

def user_tfidf_vector(user_liked_films: list[Film], vocab: dict[str, int], idf_dict: dict[int, float])-> dict[int, float]:
    """
Строит TF-IDF вектор пользователя.
Складывает TF-IDF вектора всех любимых фильмов.
На выходе словарь {id_слова: суммарный вес}.
"""
    user_tfidf = {}
    for film in user_liked_films:
        tfidf_vec = film_tfidf_vector(film, vocab, idf_dict)
        for word_id, weight in tfidf_vec.items():
            if word_id in user_tfidf:  
                user_tfidf[word_id] += weight
            else:
                user_tfidf[word_id] = weight 
    return user_tfidf

def vec_dict_to_list(vec_dict: dict[int, float], vocab_size: int) -> list[float]:
    """
    Превращает словарь {id: количество} в обычный список длины vocab_size.
    Если слово не встречалось — на его месте будет 0.
    """
    vector = [0]*vocab_size
    for key, value in vec_dict.items():
        vector[key]+=value
    return vector

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Считает косинусное сходство между двумя векторами.
    1.0 — если векторы направлены одинаково (очень похожи),
    0.0 — если один из них пустой или они совсем разные.
    """
    dot_product = 0
    norm_a = 0
    norm_b = 0
    for ai, bi in zip(a, b):
        dot_product += ai * bi
        norm_a += ai ** 2  
        norm_b += bi ** 2 

    norm_a = sqrt(norm_a)
    norm_b = sqrt(norm_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0  # чтобы не было деления на 0 (если оба вектора нулевые)

    cos = dot_product / (norm_a * norm_b)
    return cos

def compare_description(user_vec_dict: dict[int, float], film: Film, idf_dict: dict[int, float], vocab: dict[str, int], vocab_size: int) -> float:
    """
    Считает похожесть по описанию фильма.
    Для этого переводит тексты в векторы и считает косинусное сходство.
    0 = совсем разные описания, 1 = максимально похожие.
    """
    
    user_vec_list = vec_dict_to_list(user_vec_dict, vocab_size)
    film_vec_dict = film_tfidf_vector(film, vocab, idf_dict)
    film_vec_list = vec_dict_to_list(film_vec_dict, vocab_size)

    cos_sim = cosine_similarity(user_vec_list, film_vec_list)

    return round((cos_sim), 3)



def recommend_films(user_liked_films: list[Film], films: list[Film]) -> list[tuple[Film, float]]:
    """
    Главная функция: собирает все признаки (жанры, актёры, описание и т.д.)
    и считает итоговый балл для каждого фильма.
    На выходе — список фильмов, отсортированный по убыванию похожести.
    """
    vocab = build_vocab(films)
    vocab_size = len(vocab)

    user_directors = [film.director for film in user_liked_films]
    user_actors = [actor for film in user_liked_films for actor in film.actors]
    user_ratings = [film.rating for film in user_liked_films]
    user_years = [film.year for film in user_liked_films]
    user_titles = [film.title for film in user_liked_films]
    

    recommendations = []
    idf_dict = compute_idf(vocab, films)
    user_vec_dict = user_tfidf_vector(user_liked_films, vocab, idf_dict)
    films = [film for film in films if film.title not in user_titles]
    for film in films:
        director_score = compare_director(user_directors, film.director)
        actors_score = compare_actors(user_actors, film.actors)
        rating_score = compare_ratings(user_ratings, film.rating)
        years_score = compare_years(user_years, film.year)
        description_score = compare_description(user_vec_dict, film, idf_dict, vocab, vocab_size)

        score = round((director_score * 0.15 + actors_score * 0.25
                        + rating_score *0.1  + years_score * 0.1 + description_score * 0.4), 3)
        recommendations.append((film, score))
    sorted_recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    return sorted_recommendations


