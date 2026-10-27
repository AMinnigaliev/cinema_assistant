import asyncio
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logger import LOGGING
from app.db.clickhouse import init_clickhouse_client
from app.db.rebbitmq import (close_rabbit, init_publish_channel,
                             init_rabbit_conn)
from app.db.redis_client import init_redis_cache
from app.services.audio_cleanup import run_audio_cleanup
from app.services.rabbitmq import start_response_consumer

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cache = None
    clickhouse_client = None
    rabbit_initialized = False

    consumer_task = None
    cleanup_task = None

    try:
        # Инициализация Redis
        redis_cache = await init_redis_cache()
        logger.info("Клиент Redis инициализирован.")

        # Инициализация ClickHouse
        clickhouse_client = await init_clickhouse_client()
        logger.info("Клиент ClickHouse инициализирован.")

        # Инициализация RabbitMQ
        await init_rabbit_conn()
        rabbit_initialized = True

        await init_publish_channel()
        logger.info("Ресурсы RabbitMQ инициализированы.")

        # Запуск фоновых задач
        consumer_task = asyncio.create_task(
            start_response_consumer(),
            name="rabbitmq-response-consumer",
        )

        cleanup_task = asyncio.create_task(
            run_audio_cleanup(settings.outgoing_file_path),
            name="audio-cleanup",
        )

        logger.info("Приложение успешно запущено.")

        yield

    finally:
        # Останавливаем фоновые задачи
        tasks = [
            task
            for task in (consumer_task, cleanup_task)
            if task is not None
        ]

        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Фоновые задачи остановлены.")

        # Закрываем только инициализированные ресурсы.
        if rabbit_initialized:
            try:
                await close_rabbit()
                logger.info("Соединение с RabbitMQ закрыто.")
            except Exception:
                logger.exception("Ошибка закрытия RabbitMQ")

        if clickhouse_client is not None:
            try:
                clickhouse_client.disconnect()
                logger.info("Клиент ClickHouse закрыт.")
            except Exception:
                logger.exception("Ошибка закрытия ClickHouse")

        if redis_cache is not None:
            try:
                await redis_cache.close()
                logger.info("Клиент Redis закрыт.")
            except Exception:
                logger.exception("Ошибка закрытия Redis")


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/v1/openapi",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")
