from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as UUID_SQLALCHEMY
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

__all__ = [
    "Base",
    "Genre",
    "Person",
    "FilmWork",
    "GenreFilmWork",
    "PersonFilmWork",
    "BaseWithTimeStampedType",
]


class SchemaContent:
    __table_args__ = {"schema": "content"}


class Base(AsyncAttrs, DeclarativeBase):

    @classmethod
    def model_name(cls) -> str:
        return cls.__tablename__


class TimeStampedMixin:
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(UUID_SQLALCHEMY, primary_key=True)


class BaseWithTimeStampedType(AsyncAttrs, DeclarativeBase, TimeStampedMixin):
    @classmethod
    def model_name(cls) -> str:
        return cls.__tablename__


class Genre(Base, SchemaContent, UUIDMixin, TimeStampedMixin):
    __tablename__ = "genre"

    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"Genre_UID={self.id}"


class Person(Base, SchemaContent, UUIDMixin, TimeStampedMixin):
    __tablename__ = "person"

    full_name: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Person_UID={self.id}"


class FilmWork(Base, SchemaContent, UUIDMixin, TimeStampedMixin):
    __tablename__ = "film_work"

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    rating: Mapped[Float] = mapped_column(Float)
    type: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"FilmWork_UID={self.id}"


class GenreFilmWork(Base, SchemaContent, UUIDMixin):
    __tablename__ = "genre_film_work"

    genre_id: Mapped[UUID] = mapped_column(
        UUID_SQLALCHEMY, ForeignKey("content.genre.id"), primary_key=True
    )
    film_work_id: Mapped[UUID] = mapped_column(
        UUID_SQLALCHEMY, ForeignKey("content.film_work.id"), primary_key=True
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    genre_: Mapped["Genre"] = relationship(
        Genre,
        foreign_keys=[
            genre_id,
        ],
        backref="genre_film_works",
    )
    film_work_: Mapped["FilmWork"] = relationship(
        FilmWork,
        foreign_keys=[
            film_work_id,
        ],
        backref="genre_film_works",
    )

    def __repr__(self) -> str:
        return f"Genre_UID={self.genre_id}/FilmWork_UID={self.film_work_id}"


class PersonFilmWork(Base, SchemaContent, UUIDMixin):
    __tablename__ = "person_film_work"

    person_id: Mapped[UUID] = mapped_column(
        UUID_SQLALCHEMY, ForeignKey("content.person.id"), primary_key=True
    )
    film_work_id: Mapped[UUID] = mapped_column(
        UUID_SQLALCHEMY, ForeignKey("content.film_work.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    person_: Mapped["Person"] = relationship(
        Person,
        foreign_keys=[
            person_id,
        ],
        backref="person_film_works",
    )
    film_work_: Mapped["FilmWork"] = relationship(
        FilmWork,
        foreign_keys=[
            film_work_id,
        ],
        backref="person_film_works",
    )

    def __repr__(self) -> str:
        return f"Person_UID={self.person_id}/FilmWork_UID={self.film_work_id}"
