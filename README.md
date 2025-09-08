<a id="readme-top"></a>

<!-- ПРОЕКТ -->

<div align="center">
  <h3 align="center">🎬 Movie Recommender</h3>

  <p align="center">
    Pet-проект рекомендательной системы фильмов на Python (FastAPI) и React
    <br />
    <a href="https://github.com/bolotova818/movie-recommender"><strong>Документация »</strong></a>
    <br />
    <br />
    <a href="https://github.com/bolotova818/movie-recommender/issues">Сообщить о баге</a>
    ·
    <a href="https://github.com/bolotova818/movie-recommender/issues">Предложить фичу</a>
  </p>
</div>

---

## 📑 Содержание
- [О проекте](#о-проекте)
  - [Стек](#стек)
- [Начало работы](#начало-работы)
  - [Необходимое ПО](#необходимое-по)
  - [Установка](#установка)
- [Использование](#использование)
- [Дорожная карта](#дорожная-карта)
- [Как помочь](#как-помочь)
- [Лицензия](#лицензия)
- [Контакты](#контакты)
- [Благодарности](#благодарности)

---

## О проекте

 Цель проекта — создать простую рекомендательную систему фильмов.  
Есть три версии алгоритмов:
- Bag of Words (v1)
- TF-IDF (собственная реализация, v2)
- TF-IDF на базе `scikit-learn` с «умными» весами (v3)

Бэкенд реализован на **FastAPI**, фронтенд — на **React (Vite)**.  
Есть API для получения случайных фильмов и рекомендаций.

---

### Стек
- Python 3.11+
- FastAPI
- Pandas
- scikit-learn, SciPy
- JavaScript (React, Vite, axios)

---

## Начало работы

### Необходимое ПО
- Python ≥ 3.11
- Node.js ≥ 18
- npm

### Установка

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/bolotova818/movie-recommender.git
   cd movie-recommender
2. Установить зависимости для backend:
  ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app:app --reload
3. Установить зависимости для frontend:
  ```bash
   cd movie-frontend
   npm install
   npm run dev




<!-- USAGE EXAMPLES -->
## Использование

После запуска backend (`uvicorn app:app --reload`) и frontend (`npm run dev`) можно работать с API и интерфейсом.

### Случайные фильмы
```http
GET /films/random?limit=5
Пример ответа:
[
  {
    "title": "Зеленая миля",
    "year": 1999,
    "description": "...",
    "director": "Фрэнк Дарабонт",
    "actors": ["Том Хэнкс", "Майкл Кларк Дункан"],
    "country": ["США"],
    "rating": 9.1
  }
]
Рекомендации
POST /recommend
Content-Type: application/json

{
  "liked_titles": ["Матрица", "Интерстеллар"],
  "top_n": 5
}

Пример ответа:
{
  "recommendations": [
    {
      "title": "Начало",
      "year": 2010,
      "description": "...",
      "director": "Кристофер Нолан",
      "actors": ["Леонардо ДиКаприо", "Джозеф Гордон-Левитт"],
      "country": ["США", "Великобритания"],
      "rating": 8.7
    }
  ]
}
Дорожная карта

 Bag-of-Words

 TF-IDF (ручная реализация)

 TF-IDF (sklearn)

 Добавить жанры

 Подключить базу данных (SQLite/PostgreSQL)

 Реализовать UI для фронтенда

 Добавить коллаборативную фильтрацию

Смотри issues
 для полного списка задач и предложений.




<!-- CONTACT -->
## Contact

bolotova818@gmail.com
телеграм - @ban_any


<p align="right">(<a href="#readme-top">back to top</a>)</p>





