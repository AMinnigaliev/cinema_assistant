import logging

from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1 import films, genres, healthcheck, persons
from src.core.config import settings
from src.db.elastic import get_elastic
from src.db.redis_client import get_redis_cache
from src.middleware import AsyncRateLimitMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/movies/openapi',
    openapi_url='/api/v1/movies/openapi.json',
    default_response_class=ORJSONResponse,
)

# Route-внешние (используются пользователями)
api_router = APIRouter(prefix="/api/v1")

# Route-внутренние (используются для взаимодействия с внутренними сервисами)
internal_api_router = APIRouter(prefix="/api/v1/internal")


@app.on_event('startup')
async def startup():
    """
    Событие запуска приложения: инициализация базы данных PostgreSQL и
    подключений к Redis и Elasticsearch.
    """
    # Инициализация подключения к Redis
    logger.info("Инициализация подключения к Redis...")
    try:
        redis_cache = await get_redis_cache()

        # Проверяем доступность Redis-кеш
        if not await redis_cache.redis_client.ping():
            raise ConnectionError("Redis-кеш не отвечает на запросы.")

    except settings.redis_exceptions as e:
        logger.error("Ошибка подключения к Redis: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Redis. Приложение завершает работу."
        )

    else:
        logger.info("Подключение к Redis успешно установлено.")

    # Инициализация подключения к Elasticsearch
    logger.info("Инициализация подключения к Elasticsearch...")
    try:
        es = await get_elastic()

        # Проверяем доступность Elasticsearch
        if not await es.es_client.ping():
            raise ConnectionError("Elasticsearch не отвечает на запросы.")

    except settings.elastic_exceptions as e:
        logger.error("Ошибка подключения к Elasticsearch: %s", e)

        raise ConnectionError(
            "Не удалось подключиться к Elasticsearch. Приложение завершает "
            "работу."
        )

    else:
        logger.info("Подключение к Elasticsearch успешно установлено.")

    logger.info("Все подключения успешно установлены.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие завершения работы приложения: закрытие подключений к Redis и
    Elasticsearch.
    """
    # Закрытие подключения к Redis
    redis_cache = await get_redis_cache()
    if redis_cache:
        await redis_cache.close()

    # Закрытие подключения к Elasticsearch
    es = await get_elastic()
    if es:
        await es.close()


# Подключение Route - внешних
api_router.include_router(
    films.router, prefix="/movies/films", tags=["films"]
)
api_router.include_router(
    persons.router, prefix="/movies/persons", tags=["persons"]
)
api_router.include_router(
    genres.router, prefix="/movies/genres", tags=["genres"]
)
api_router.include_router(
    healthcheck.router, prefix="/movies", tags=["healthcheck"]
)

app.include_router(api_router)

# Middleware:
app.add_middleware(AsyncRateLimitMiddleware)
