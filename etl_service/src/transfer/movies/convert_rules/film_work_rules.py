from schemas.movies_schemas.film_work_models import (FilmWorkESModel,
                                                     FilmWorkModel)
from utils.movies_utils.etl_enum import PersonRoles


class FilmWorkRules:

    @classmethod
    async def film_work_transformation_data_rule(cls, obj_data: dict):
        film_work_model = FilmWorkModel(**obj_data)

        film_work_es_model = FilmWorkESModel(
            id=film_work_model.id,
            imdb_rating=(
                film_work_model.imdb_rating
                if film_work_model.imdb_rating is not None
                else 0.0
            ),
            genres=[
                {
                    "id": genre.id,
                    "name": genre.name if genre.name else "",
                }
                for genre in film_work_model.genres
            ],
            title=film_work_model.title if film_work_model.title else "",
            description=film_work_model.description or "",
            directors_names=[
                person.full_name
                for person in film_work_model.persons
                if person.role == PersonRoles.DIRECTOR.value
            ],
            actors_names=[
                person.full_name
                for person in film_work_model.persons
                if person.role == PersonRoles.ACTOR.value
            ],
            writers_names=[
                person.full_name
                for person in film_work_model.persons
                if person.role == PersonRoles.WRITER.value
            ],
            directors=[
                {
                    "id": person.id,
                    "full_name": person.full_name if person.full_name else "",
                }
                for person in film_work_model.persons
                if person.role == PersonRoles.DIRECTOR.value
            ],
            actors=[
                {
                    "id": person.id,
                    "full_name": person.full_name if person.full_name else "",
                }
                for person in film_work_model.persons
                if person.role == PersonRoles.ACTOR.value
            ],
            writers=[
                {
                    "id": person.id,
                    "full_name": person.full_name if person.full_name else "",
                }
                for person in film_work_model.persons
                if person.role == PersonRoles.WRITER.value
            ],
        )

        film_work_es_model.was_enrich = True
        film_work_es_model.was_convert = True

        return film_work_es_model
