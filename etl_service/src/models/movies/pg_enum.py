import abc
import enum

from sqlalchemy import Enum as DataBaseEnum


class BaseEnum(enum.Enum):

    @classmethod
    @abc.abstractmethod
    def get_enum_name(cls) -> str:
        pass

    @classmethod
    def get_enum(cls) -> DataBaseEnum:
        return DataBaseEnum(
            *(value for value in cls), name=cls.get_enum_name()
        )


class FilmTypesEnum(BaseEnum):
    MOVIE = "movie"
    TV_SHOW = "tv show"

    @classmethod
    def get_enum_name(cls) -> str:
        return "film_type_enum"


class RolesEnum(BaseEnum):
    ACTOR = "actor"
    DIRECTOR = "director"
    WRITER = "writer"

    @classmethod
    def get_enum_name(cls) -> str:
        return "role_enum"
