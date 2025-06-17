import socket
from collections import defaultdict

from sqlalchemy import select

from models.movies.pg_models import PersonFilmWork
from schemas.movies_schemas.person_models import FilmWorkModel, PersonModel
from utils import backoff_by_connection


class PersonRules:

    @classmethod
    @backoff_by_connection(
        exceptions=(ConnectionRefusedError, socket.gaierror)
    )
    async def person_selection_data_rule(
        cls, pg_session, obj_id: int
    ) -> dict:
        query_person_film_work = await pg_session.execute(
            select(
                PersonFilmWork.film_work_id.label("film_work_id"),
                PersonFilmWork.role.label("person_role"),
            ).where(
                PersonFilmWork.person_id == obj_id,
            )
        )

        persons_data = {
            PersonFilmWork.model_name(): query_person_film_work.all(),
        }

        return persons_data

    @classmethod
    async def person_normalized_enrich_data_rule(
        cls, obj_data: dict, selection_data: dict
    ) -> PersonModel:
        person_data = PersonModel(**obj_data)
        person_data.was_enrich = True

        if person_film_work_data := selection_data.get(
                PersonFilmWork.model_name()
        ):
            person_roles_by_film_work_id = defaultdict(list)

            for person_film_work in person_film_work_data:
                person_roles_by_film_work_id[
                    person_film_work.film_work_id
                ].append(
                    person_film_work.person_role
                )

            person_data.films = [
                FilmWorkModel(
                    id=film_work_id,
                    roles=person_roles,
                )
                for (
                    film_work_id, person_roles
                ) in person_roles_by_film_work_id.items()
            ]

        return person_data
