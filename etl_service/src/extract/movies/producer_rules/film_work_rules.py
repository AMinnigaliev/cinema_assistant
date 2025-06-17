import socket
from datetime import datetime

from sqlalchemy import select

from core import config
from models.movies.pg_models import FilmWork
from schemas.movies_schemas.film_work_models import FilmWorkModel
from utils import backoff_by_connection


class FilmWorkRules:

    @classmethod
    @backoff_by_connection(
        exceptions=(ConnectionRefusedError, socket.gaierror)
    )
    async def film_work_selection_data_rule(
        cls, pg_session, date_modified: datetime
    ) -> list[FilmWork]:
        limit = config.etl_movies_select_limit

        query_ = await pg_session.scalars(
            select(FilmWork)
            .where(FilmWork.modified >= date_modified)
            .order_by(FilmWork.modified)
            .limit(limit)
        )
        film_works = query_.all()

        return film_works

    @classmethod
    def film_work_normalize_data_rule(
        cls, selection_data: list[FilmWork]
    ) -> list[FilmWorkModel]:
        normalized_data = [
            FilmWorkModel(
                id=film_work.id,
                imdb_rating=film_work.rating if film_work.rating else 0.0,
                title=film_work.title if film_work.title else "",
                description=film_work.description or "",
            )
            for film_work in selection_data
        ]

        return normalized_data
