import asyncio
import logging.config

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logger import LOGGING
from app.db.clickhouse import get_clickhouse_client, init_clickhouse_client
from app.db.rebbitmq import (close_rabbit, init_publish_channel,
                             init_rabbit_conn)
from app.db.redis_client import get_redis_cache, init_redis_cache
from app.services.rabbitmq import start_response_consumer

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/openapi',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    """
    Событие запуска приложения: устанавливаем соединение и канал RabbitMQ,
    запускаем consumer.
    """
    await init_redis_cache()
    logger.info("Клиент Redis инициализирован.")

    await init_clickhouse_client()
    logger.info("Клиент Clickhouse инициализирован.")

    await init_rabbit_conn()
    await init_publish_channel()
    asyncio.create_task(start_response_consumer())

    logger.info("Все RabbitMQ‐ресурсы инициализированы.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие остановки приложения: закрываем соединение с RabbitMQ.
    """
    await close_rabbit()
    logger.info("Соединение с RabbitMQ закрыто.")

    client = await get_clickhouse_client()
    client.disconnect()
    logger.info("Клиент Clickhouse закрыт.")

    redis_cache = await get_redis_cache()
    await redis_cache.close()

    logger.info("Приложение завершает работу.")
