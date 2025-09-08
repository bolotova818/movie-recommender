class Film:
    def __init__(
        self,
        title: str,
        year: int,
        country: list[str],
        actors: list[str],
        rating: float,
        director: str,
        description: str
    ):
        self.title = title
        self.year = year
        self.country = country
        self.actors = actors
        self.rating = rating
        self.director = director
        self.description = description


