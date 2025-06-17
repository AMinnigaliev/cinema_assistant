from typing import TypeVar

from aiohttp import ClientConnectorError
from elasticsearch import AsyncElasticsearch
from elasticsearch import ConnectionError as ConnectionErrorES
from elasticsearch import NotFoundError

from core import config
from utils import backoff_by_connection

ESClient_T = TypeVar("ESClient_T", bound="AsyncESClient")


class AsyncESClient:
    """Async-клиент Elasticsearch."""

    def __init__(self):
        self.__host = config.elastic_host
        self.__port = config.elastic_port
        self._client = AsyncElasticsearch(
            "http://{}:{}/".format(self.__host, self.__port),
            basic_auth=(config.elastic_name, config.elastic_password),
            max_retries=0,
            retry_on_timeout=False,
        )

    async def close_(self) -> None:
        await self._client.close()

    @backoff_by_connection(
        exceptions=(ConnectionErrorES, ClientConnectorError)
    )
    async def create_index_with_ignore(self, index_: str, body: dict = None):
        if body:
            try:
                await self._client.search(index=index_)

            except NotFoundError:
                await self._client.indices.create(index=index_, body=body)

    @backoff_by_connection(
        exceptions=(ConnectionErrorES, ClientConnectorError)
    )
    async def insert_document(
        self, index_: str, document: dict, id_: int = None
    ) -> dict:
        result = {"status": True}
        response_ = await self._client.index(
            index=index_, document=document, id=id_
        )

        if body := response_.get("body"):
            if error := body.get("error"):
                result["status"], result["message"] = False, error

        return result


class ESContextManager:
    """Контекстный менеджер по работе с RedisStorage."""

    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        return self._client

    async def __aenter__(self) -> ESClient_T:
        self._client = AsyncESClient()

        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._client.close_()


es_context_manager = ESContextManager()
