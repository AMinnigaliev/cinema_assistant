import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.db.elastic import get_elastic, settings
from src.db.redis_client import get_redis_cache
from src.models.models import GenreBase
from src.services.base_service import BaseService
from src.services.cache_service import CacheService
from src.services.elastic_service import ElasticService

logger = logging.getLogger(__name__)


class GenreService(BaseService):
    """
    Сервис для работы с жанрами.

    Осуществляет взаимодействие с Redis (для кеширования)
    и Elasticsearch (для полнотекстового поиска).
    """

    async def get_genre_by_id(self, genre_id: UUID) -> list[GenreBase] | None:
        """Получить фильм по его ID."""
        log_info = f"Получение жанра по ID {genre_id}"

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "genre"
        # Ключ для кеша
        cache_key = f"genre:{genre_id}"
        # Модель Pydantic для возврата
        model = GenreBase

        # Формируем тело запроса для Elasticsearch
        body = {"query": {"term": {"id": genre_id}}}

        return await self._base_get_with_cache(
            model, es_index, body, cache_key, log_info
        )

    async def get_genres(self) -> list[GenreBase] | None:
        """Получить список жанров."""
        log_info = "Запрос на получение списка жанров."

        logger.info(log_info)

        # Индекс для Elasticsearch
        es_index = "genre"
        # Ключ для кеша
        cache_key = "genres"
        # Модель Pydantic для возврата
        model = GenreBase

        # Формируем тело запроса для Elasticsearch
        body = {
            "query": {"match_all": {}}, "size": settings.elastic_response_size
        }

        return await self._base_get_with_cache(
            model, es_index, body, cache_key, log_info
        )

    async def search_genres(
        self, query: str | None = None
    ) -> list[GenreBase] | None:
        """Поиск жанров по ключевым словам."""
        log_info = f"Запрос на получение жанров: (query={query})."

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "genre"
        # Модель Pydantic для возврата
        model = GenreBase

        # Формируем тело запроса для Elasticsearch
        body = {"query": {}, "size": settings.elastic_response_size}

        #  Поиск, если есть
        if query:
            body["query"]["multi_match"] = {
                "query": query,
                "fields": ["name"],
                "fuzziness": "AUTO"
            }

        else:
            body["query"]["match_all"] = {}

        return await self._base_get_no_cache(
            model, es_index, body, log_info
        )


@lru_cache()
def get_genre_service(
    redis: Annotated[CacheService, Depends(get_redis_cache)],
    elastic: Annotated[ElasticService, Depends(get_elastic)]
) -> GenreService:
    """
    Провайдер для получения экземпляра GenreService.

    Функция создаёт синглтон экземпляр GenreService, используя Redis и
    Elasticsearch, которые передаются через Depends (зависимости FastAPI).

    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :param elastic: Экземпляр клиента Elasticsearch, предоставленный через
    Depends.
    :return: Экземпляр GenreService, который используется для работы с
    фильмами.
    """
    logger.info(
        "Создаётся экземпляр GenreService с использованием Redis и "
        "Elasticsearch."
    )
    return GenreService(redis, elastic)
