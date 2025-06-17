import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.core.config import settings
from src.db.elastic import get_elastic
from src.db.redis_client import get_redis_cache
from src.models.models import FilmBase, Person
from src.services.base_service import BaseService
from src.services.cache_service import CacheService
from src.services.elastic_service import ElasticService

logger = logging.getLogger(__name__)


class PersonService(BaseService):
    """
    Сервис для работы с персонами.

    Осуществляет взаимодействие с Redis (для кеширования)
    и Elasticsearch (для полнотекстового поиска).
    """

    async def get_person_by_id(self, person_id: UUID) -> list[Person] | None:
        """Получить фильм по его ID."""
        log_info = f"Получение персоны по ID {person_id}"

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "person"
        # Ключ для кеша
        cache_key = f"person:{person_id}"
        # Модель Pydantic для возврата
        model = Person

        # Формируем тело запроса для Elasticsearch
        body = {"query": {"term": {"id": person_id}}}

        return await self._base_get_with_cache(
            model, es_index, body, cache_key, log_info
        )

    async def get_person_films(
        self,
        person_id: UUID,
    ) -> list[FilmBase] | None:
        """
        Получить список фильмов в производстве которых участвовала персона.
        """
        log_info = (
            f"Запрос на получение фильмов с участием персоны: "
            f"id = {person_id}."
        )

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "film_work"
        # Ключ для кеша
        cache_key = f"person_films:{person_id}"
        # Модель Pydantic для возврата
        model = FilmBase

        # Формируем тело запроса для Elasticsearch
        body = {"query": {"bool": {
            "should": [
                {
                    "nested": {
                        "path": "actors",
                        "query": {
                            "term": {
                                "actors.id": person_id,
                            }
                        }
                    }
                },
                {
                    "nested": {
                        "path": "writers",
                        "query": {
                            "term": {
                                "writers.id": person_id,
                            }
                        }
                    }
                },
                {
                    "nested": {
                        "path": "directors",
                        "query": {
                            "term": {
                                "directors.id": person_id,
                            }
                        }
                    }
                },
            ],
            "minimum_should_match": 1,
        }}, "size": settings.elastic_response_size}

        return await self._base_get_with_cache(
            model, es_index, body, cache_key, log_info
        )

    async def search_persons(
        self,
        query: str | None = None,
        page_size: int = 10,
        page_number: int = 1,
    ) -> list[Person] | None:
        """
        Поиск персон по ключевым словам и пагинацией.
        """
        log_info = (
            f"Запрос на получение персон: (query={query}, "
            f"page_size={page_size}, page_number={page_number})."
        )

        logger.info(log_info)

        #  Индекс для Elasticsearch
        es_index = "person"
        # Модель Pydantic для возврата
        model = Person

        # Формируем тело запроса для Elasticsearch
        body = {"query": {}}

        #  Поиск, если есть
        if query:
            body["query"]["multi_match"] = {
                "query": query,
                "fields": ["full_name"],
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
def get_person_service(
    redis: Annotated[CacheService, Depends(get_redis_cache)],
    elastic: Annotated[ElasticService, Depends(get_elastic)]
) -> PersonService:
    """
    Провайдер для получения экземпляра PersonService.

    Функция создаёт синглтон экземпляр PersonService, используя Redis и
    Elasticsearch, которые передаются через Depends (зависимости FastAPI).

    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :param elastic: Экземпляр клиента Elasticsearch, предоставленный через
    Depends.
    :return: Экземпляр PersonService, который используется для работы с
    фильмами.
    """
    logger.info(
        "Создаётся экземпляр PersonService с использованием Redis и "
        "Elasticsearch."
    )
    return PersonService(redis, elastic)
