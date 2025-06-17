from schemas.base import Base

__all__ = [
    "GenreModel",
]


class GenreModel(Base):
    name: str
    description: str

    was_enrich: bool = True
    was_convert: bool = False
