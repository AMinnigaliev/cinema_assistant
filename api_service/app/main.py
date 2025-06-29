import logging.config

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logger import LOGGING
from app.db.clickhouse import init_clickhouse_client
from app.db.rebbitmq import (close_rabbit, init_publish_channel,
                             init_rabbit_conn)
from app.services.rabbitmq import start_response_consumer

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/movies/openapi',
    openapi_url='/api/v1/movies/openapi.json',
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    """
    Событие запуска приложения: устанавливаем соединение и канал RabbitMQ,
    запускаем consumer.
    """
    await init_clickhouse_client()
    await init_rabbit_conn()
    await init_publish_channel()
    await start_response_consumer()

    logger.info("Все RabbitMQ‐ресурсы инициализированы.")


@app.on_event('shutdown')
async def shutdown():
    """
    Событие остановки приложения: закрываем соединение с RabbitMQ.
    """
    await close_rabbit()

    logger.info("Соединение с RabbitMQ закрыто. Приложение завершает работу.")
