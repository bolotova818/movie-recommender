import pandas as pd
from films_model import Film

def load_films_from_csv(path: str) -> list[Film]:
    df = pd.read_csv(path)

    films: list[Film] = []
    for _, row in df.iterrows():
        title = str(row["movie"]).strip()
        year = int(row["year"]) if not pd.isna(row["year"]) else 0
        country = [c.strip() for c in str(row["country"]).split(";")] if not pd.isna(row["country"]) else []
        actors = [a.strip() for a in str(row["actors"]).split(";")] if not pd.isna(row["actors"]) else []
        rating = float(row["rating_ball"]) if not pd.isna(row["rating_ball"]) else 0.0
        director = str(row["director"]).strip() if not pd.isna(row["director"]) else ""
        description = str(row["overview"]).strip() if not pd.isna(row["overview"]) else ""

        film = Film(
            title=title,
            year=year,
            country=country,
            actors=actors,
            rating=rating,
            director=director,
            description=description
        )
        films.append(film)

    return films
