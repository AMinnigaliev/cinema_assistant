from schemas.base import Base

__all__ = ["PersonModel", "FilmWorkModel"]


class FilmWorkModel(Base):
    roles: list[str]


class PersonModel(Base):
    full_name: str
    films: list[FilmWorkModel] = []

    was_enrich: bool = False
    was_convert: bool = False
