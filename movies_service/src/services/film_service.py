import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis_client import get_redis_cache
from src.models.models import Film, FilmBase
from src.services.base_service import BaseService
from src.services.cache_service import CacheService
from src.services.elastic_service import ElasticService

logger = logging.getLogger(__name__)


class FilmService(BaseService):
    """
    Сервис для работы с фильмами.

    Осуществляет взаимодействие с Redis (для кеширования)
    и Elasticsearch (для полнотекстового поиска).
    """

    async def get_film_by_id(self, film_id: UUID) -> list[Film] | None:
        """Получить фильм по его ID."""
        log_info = f"Получение фильма по ID {film_id}"

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "film_work"
        # Ключ для кеша
        cache_key = f"film:{film_id}"
        # Модель Pydantic для возврата
        model = Film

        # Формируем тело запроса для Elasticsearch
        body = {"query": {"term": {"id": film_id}}}

        return await self._base_get_with_cache(
            model, es_index, body, cache_key, log_info
        )

    async def get_films(
            self,
            genre: UUID | None = None,
            sort: str = "-imdb_rating",
            page_size: int = 10,
            page_number: int = 1,
    ) -> list[FilmBase] | None:
        """
        Получить список фильмов с поддержкой сортировки по рейтингу,
        фильтрации по жанру и пагинацией.
        """
        log_info = (
            f"Запрос на получение фильмов: (sort={sort}, genre={genre}, "
            f"page_size={page_size}, page_number={page_number})."
        )

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "film_work"
        # Ключ для кеша
        cache_key = f"films:{genre}:{sort}:{page_size}:{page_number}"
        # Модель Pydantic для возврата
        model = FilmBase

        # Формируем тело запроса для Elasticsearch
        body = {"query": {}}

        # Фильтр по жанру, если есть
        if genre:
            filter_by_genre = [
                {"nested": {
                    "path": "genres",
                    "query": {"term": {"genres.id": genre}},
                }}
            ]
            body["query"]["bool"] = {
                "must": [],
                "filter": filter_by_genre,
            }

        else:
            body["query"]["match_all"] = {}

        # Сортировка
        sort_field = sort.lstrip("-")
        sort_order = "desc" if sort.startswith("-") else "asc"

        body["sort"] = [{sort_field: {
            "order": sort_order, "missing": "_last"
        }}]

        #  Вычисляем начальную запись для выдачи
        from_value = (page_number - 1) * page_size

        body["from"] = from_value
        body["size"] = page_size

        return await self._base_get_with_cache(
            model, es_index, body, cache_key, log_info
        )

    async def search_films(
        self,
        query: str | None = None,
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[FilmBase] | None:
        """
        Поиск фильмов по ключевым словам и пагинацией.
        """
        log_info = (
            f"Запрос на получение фильмов: (query={query}, "
            f"page_size={page_size}, page_number={page_number})."
        )

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "film_work"
        # Модель Pydantic для возврата
        model = FilmBase

        # Формируем тело запроса для Elasticsearch
        body = {"query": {}}

        #  Поиск, если есть
        if query:
            body["query"]["multi_match"] = {
                "query": query,
                "fields": ["title"],
                "fuzziness": "AUTO"
            }

        else:
            body["query"]["match_all"] = {}

        #  Вычисляем начальную запись для выдачи
        from_value = (page_number - 1) * page_size

        body["from"] = from_value
        body["size"] = page_size

        return await self._base_get_no_cache(
            model, es_index, body, log_info
        )


@lru_cache()
def get_film_service(
    redis: Annotated[CacheService, Depends(get_redis_cache)],
    elastic: Annotated[ElasticService, Depends(get_elastic)]
) -> FilmService:
    """
    Провайдер для получения экземпляра FilmService.

    Функция создаёт синглтон экземпляр FilmService, используя Redis и
    Elasticsearch, которые передаются через Depends (зависимости FastAPI).

    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :param elastic: Экземпляр клиента Elasticsearch, предоставленный через
    Depends.
    :return: Экземпляр FilmService, который используется для работы с фильмами.
    """
    logger.info(
        "Создаётся экземпляр FilmService с использованием Redis и "
        "Elasticsearch."
    )
    return FilmService(redis, elastic)
