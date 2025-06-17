import logging
from typing import Any

from elastic_transport import ObjectApiResponse, TransportError
from elasticsearch import AsyncElasticsearch, NotFoundError

from src.core.config import settings
from src.core.exceptions import ElasticServiceError

logger = logging.getLogger(__name__)


class ElasticService:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    async def get(
        self, index: str, id: str, log_info: str = ""
    ) -> ObjectApiResponse[Any] | None:
        logger.debug(
            "Попытка выполнить запрос get в Elasticsearch: "
            "index=%s, id=%s. %s",
            index, id, log_info
        )
        try:
            response = await self.es_client.get(index=index, id=id)

            logger.info(
                "Запрос get успешно выполнен в Elasticsearch: index=%s. %s",
                index, log_info
            )
            return response

        except NotFoundError:
            logger.info(
                "Запись не найдена в Elasticsearch: index=%s. %s",
                index, log_info
            )
            raise

        except settings.elastic_exceptions as e:
            logger.error(
                "Ошибка при выполнении запроса get в Elasticsearch: "
                "index=%s, error=%s. %s",
                index, e, log_info
            )
            raise ElasticServiceError(e)

    async def search(
        self, index: str, query: dict, log_info: str = ""
    ) -> ObjectApiResponse[Any]:
        logger.debug(
            "Попытка выполнить запрос search в Elasticsearch: "
            "index=%s, query=%s. %s",
            index, query, log_info
        )
        try:
            response = await self.es_client.search(index=index, body=query)
            count_records = len(response.get("hits", {}).get("hits", []))

            logger.info(
                "Запрос search успешно выполнен в Elasticsearch: "
                "index=%s, hits=%d. %s",
                index, count_records, log_info
            )
            return response

        except NotFoundError:
            logger.info(
                "Не найдена ни одна запись в Elasticsearch: index=%s. %s",
                index, log_info
            )
            raise

        except settings.elastic_exceptions as e:
            logger.error(
                "Ошибка при выполнении запроса search в Elasticsearch: "
                "index=%s, error=%s. %s",
                index, e, log_info
            )
            raise ElasticServiceError(e)

    async def index(
        self, index: str, id: str, body: dict
    ) -> ObjectApiResponse[Any]:
        """Добавить или обновить документ в Elasticsearch."""
        logger.debug(
            "Попытка добавить документ в Elasticsearch: index=%s, id=%s",
            index, id
        )
        try:
            response = await self.es_client.index(
                index=index, id=id, body=body
            )
            logger.info(
                "Документ успешно добавлен в Elasticsearch: index=%s, id=%s",
                index, id
            )
            return response

        except settings.elastic_exceptions as e:
            logger.error(
                "Ошибка при добавлении документа в Elasticsearch: "
                "index=%s, id=%s, error=%s",
                index, id, e
            )
            raise ElasticServiceError(e)

    async def index_exists(self, index_name: str) -> bool:
        """
        Проверяет, существует ли индекс в Elasticsearch.
        """
        try:
            return await self.es_client.indices.exists(index=index_name)
        except settings.elastic_exceptions as e:
            logger.error(
                "Ошибка при проверке существования индекса %s: %s",
                index_name, e
            )
            raise

    async def close(self):
        logger.info("Закрытие подключения к Elasticsearch...")

        try:
            await self.es_client.close()
            logger.info("Подключение к Elasticsearch успешно закрыто.")

        except (TransportError, RuntimeError) as e:
            logger.error(
                "Ошибка при закрытии подключения с Elasticsearch: %s", e
            )
            raise ElasticServiceError(e)

    async def is_connected(self) -> bool:
        return await self.es_client.ping()
