"""
Версия 1 рекомендательной системы фильмов.

Простейшая реализация на основе count-векторов
- тексты описаний переводятся в набор ключевых слов
- строятся частотные вектора (bag of words)
- сравнение идёт через косинусную близость.
Остальные признаки считаются проще - по индексу Жаккара или просто по среднему

"""

from films_model import Film
from math import sqrt
from data_loader import load_films_from_csv

films = load_films_from_csv("data/kinopoisk-top250.csv")

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


#Ниже - стоп-слова и стоп-символы для построения словаря
  
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


def extract_keywords(description: str) -> set[str]:    
    """
    Берет описание фильма, очищает от знаков и стоп-слов.
    На выходе — множество ключевых слов.
    """                                             
    description = description.lower()
    for symbol in stop_symbols:
        description = description.replace(symbol, "")
    
    words = description.split()

    keywords = [word for word in words if word not in stop_words]
    
    return set(keywords)


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


def build_vec_dict(film: Film, vocab: dict[str, int]) -> dict[int, int]:     
    """
    Для одного фильма считает, сколько раз каждое слово словаря встретилось в описании.
    Возвращет словарь {id_слова: количество}.
    """                                                           
    keywords = extract_keywords(film.description)
    vec_dict = {}
    for word in keywords:
        if word in vocab:
            word_id = vocab[word]
            if word_id in vec_dict:
                vec_dict[word_id] += 1
            else:
                vec_dict[word_id] = 1
    
    return vec_dict

   
def user_vect(user_liked_films: list[Film], vocab: dict[str, int]) -> dict[int, int]:
    """
    Строит суммарный вектор пользователя.
    Берет все фильмы пользователя и суммирует их вектора.
    """                                                      
    user_vec = {}
    for film in user_liked_films:
        film_vec_dict = build_vec_dict(film, vocab)
        for word_id, count in film_vec_dict.items(): 
            if word_id in user_vec:
                user_vec[word_id] += count
            else:
                user_vec[word_id] = count


    return user_vec


def vec_dict_to_list(vec_dict: dict[int, int], vocab_size: int) -> list[int]:
    """
    Превращает словарь {id: количество} в обычный список длины vocab_size.
    Если слово не встречалось — на его месте будет 0.
    """
    vector = [0]*vocab_size
    for key, value in vec_dict.items():
        vector[key]+=value
    return vector

def cosine_similarity(a: list[int], b: list[int]) -> float:
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


def compare_description(user_vec_dict: dict[int, int], film: Film, vocab: dict[str, int], vocab_size: int) -> float:
    """
    Считает похожесть по описанию фильма.
    Для этого переводит тексты в векторы и берет косинусное сходство.
    0 = совсем разные описания, 1 = максимально похожие.
    """

    user_vec = vec_dict_to_list(user_vec_dict, vocab_size)
    film_vec_dict = build_vec_dict(film, vocab)
    film_vec_list = vec_dict_to_list(film_vec_dict, vocab_size)

    cos_sim = cosine_similarity(user_vec, film_vec_list)

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
    user_vec_dict = user_vect(user_liked_films, vocab)
    films = [film for film in films if film.title not in user_titles]
    for film in films:
        director_score = compare_director(user_directors, film.director)
        actors_score = compare_actors(user_actors, film.actors)
        rating_score = compare_ratings(user_ratings, film.rating)
        years_score = compare_years(user_years, film.year)
        description_score = compare_description(user_vec_dict, film, vocab, vocab_size)

        score = round((director_score * 0.15 + actors_score * 0.25
                        + rating_score *0.1  + years_score * 0.1 + description_score * 0.4), 3)
        recommendations.append((film, score))
    sorted_recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    return sorted_recommendations








