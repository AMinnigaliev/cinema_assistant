from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
from sqlalchemy import Engine

from utils.es_helpers import make_async_es_client
from utils.pg_helpers import make_pg_engine
from utils.redis_helpers import make_redis_client


@pytest_asyncio.fixture
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    """Создает экземпляр клиента Elasticsearch для тестов."""
    client = make_async_es_client()
    try:
        yield client

    finally:
        await client.close()


@pytest.fixture(scope="session")
def redis_client() -> Generator[Redis, None, None]:
    """
    Создаёт асинхронный клиент Redis для всего тестового сеанса
    и закрывает соединение по завершении сессии.
    """
    client = make_redis_client()
    try:
        yield client

    finally:
        client.close()


@pytest.fixture(autouse=True)
def clear_redis(redis_client: Redis) -> None:
    """
    Очищает все ключи перед каждым тестом (autouse=True).
    """
    redis_client.flushall()

    yield

    redis_client.flushall()


@pytest.fixture(scope="session")
def pg_engine() -> Generator[Engine, None, None]:
    """Создаёт синхронный движок для PostgreSQL."""
    engine = make_pg_engine()
    try:
        yield engine

    finally:
        engine.dispose()
