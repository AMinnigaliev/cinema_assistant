from typing import Optional
from uuid import UUID

from schemas.base import Base

__all__ = ["FilmWorkModel", "PersonModel", "GenreModel", "FilmWorkESModel"]


class PersonModel(Base):
    film_work_id: UUID
    full_name: str
    role: str


class GenreModel(Base):
    film_work_id: UUID
    name: str
    description: str


class FilmWorkModel(Base):
    imdb_rating: float
    title: str
    description: str

    genres: Optional[list[GenreModel]] = []
    persons: Optional[list[PersonModel]] = []

    was_enrich: bool = False
    was_convert: bool = False


class FilmWorkESModel(Base):
    imdb_rating: float
    genres: list[dict[str, str | UUID]]
    title: str
    description: str
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]

    directors: list[dict[str, str | UUID]]
    actors: list[dict[str, str | UUID]]
    writers: list[dict[str, str | UUID]]

    was_enrich: bool = False
    was_convert: bool = False
