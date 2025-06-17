import socket

from sqlalchemy import select

from models.movies.pg_models import (FilmWork, Genre, GenreFilmWork, Person,
                                     PersonFilmWork)
from schemas.movies_schemas.film_work_models import (FilmWorkModel, GenreModel,
                                                     PersonModel)
from utils import backoff_by_connection


class FilmWorkRules:

    @classmethod
    @backoff_by_connection(
        exceptions=(ConnectionRefusedError, socket.gaierror)
    )
    async def film_work_selection_data_rule(
        cls, pg_session, obj_id: int
    ) -> dict:
        query_person = await pg_session.execute(
            select(
                FilmWork.id.label("film_work_id"),
                PersonFilmWork.role.label("person_role"),
                Person.id.label("person_id"),
                Person.full_name.label("person_full_name"),
            )
            .join(
                PersonFilmWork,
                FilmWork.id == PersonFilmWork.film_work_id,
            )
            .join(
                Person,
                PersonFilmWork.person_id == Person.id,
            )
            .where(
                FilmWork.id == obj_id,
            )
        )

        query_genre = await pg_session.execute(
            select(
                FilmWork.id.label("film_work_id"),
                Genre.id.label("genre_id"),
                Genre.name.label("genre_name"),
                Genre.description.label("genre_description"),
            )
            .join(
                GenreFilmWork,
                FilmWork.id == GenreFilmWork.film_work_id,
            )
            .join(
                Genre,
                GenreFilmWork.genre_id == Genre.id,
            )
            .where(
                FilmWork.id == obj_id,
            )
        )

        film_works_data = {
            Person.model_name(): query_person.all(),
            Genre.model_name(): query_genre.all(),
        }

        return film_works_data

    @classmethod
    async def film_work_normalized_enrich_data_rule(
        cls, obj_data: dict, selection_data: dict
    ) -> FilmWorkModel:
        film_work_data = FilmWorkModel(**obj_data)
        film_work_data.was_enrich = True

        if persons_data := selection_data.get(Person.model_name()):
            film_work_data.persons = [
                PersonModel(
                    id=person_data.person_id,
                    film_work_id=person_data.film_work_id,
                    full_name=(
                        person_data.person_full_name
                        if person_data.person_full_name
                        else ""
                    ),
                    role=person_data.person_role,
                )
                for person_data in persons_data
            ]

        if genres_data := selection_data.get(Genre.model_name()):
            film_work_data.genres = [
                GenreModel(
                    id=genre_data.genre_id,
                    film_work_id=genre_data.film_work_id,
                    name=genre_data.genre_name,
                    description=(
                        genre_data.genre_description
                        if genre_data.genre_description
                        else ""
                    ),
                )
                for genre_data in genres_data
            ]

        return film_work_data
