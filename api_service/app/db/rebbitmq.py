import asyncio
import logging.config

from aio_pika import RobustChannel, RobustConnection, connect_robust
from aio_pika.exceptions import (AMQPConnectionError, ChannelInvalidStateError,
                                 ConnectionClosed)

from app.core.config import settings
from app.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

conn: RobustConnection | None = None
publish_channel: RobustChannel | None = None


async def init_rabbit_conn(retries: int = 3, delay: int = 5) -> None:
    global conn

    logger.info("Подключение к RabbitMQ...")

    for attempt in range(1, retries + 1):
        try:
            conn = await connect_robust(
                settings.rabbitmq_url(), reconnect_interval=delay
            )
            logger.info(
                "Соединение с RabbitMQ установленно после %d попытки", attempt
            )
            return

        except (AMQPConnectionError, OSError) as e:
            logger.error(
                "Не удалось подключиться к RabbitMQ (попытка %d): %s",
                attempt, e
            )
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                logger.critical(
                    "Исчерпаны попытки подключения к RabbitMQ. Приложение "
                    "завершает работу."
                )
                raise


async def init_publish_channel(retries: int = 3) -> None:
    global conn, publish_channel

    for attempt in range(1, retries + 1):
        try:
            publish_channel = await conn.channel()
            await publish_channel.set_qos(prefetch_count=10)

            logger.info("RabbitMQ publish_channel успешно инициализирован")
            return

        except (AMQPConnectionError, ChannelInvalidStateError,
                ConnectionClosed, OSError) as e:
            logger.error(
                "Ошибка при инициализации publish_channel RabbitMQ: %s", e)

            if conn and not conn.is_closed:
                await conn.close()
            conn = None
            publish_channel = None
            if attempt < retries:
                await init_rabbit_conn()
            else:
                logger.critical(
                    "Исчерпаны попытки инициализации publish_channel "
                    "RabbitMQ. Приложение завершает работу."
                )
                raise


async def get_rabbit_connect() -> RobustConnection:
    """
    Возвращает рабочее соединение.
    """
    if not conn or conn.is_closed:
        logger.warning(
            "Соединение RabbitMQ закрыто, выполняется повторная "
            "инициализация..."
        )
        await init_rabbit_conn()

    return conn


async def get_rabbit_publish_channel() -> RobustChannel:
    """Возвращает рабочий канал для публикации."""
    if not publish_channel or publish_channel.is_closed:
        logger.warning(
            "Канал RabbitMQ для публикации закрыт, канал "
            "переинициализируется..."
        )
        await init_publish_channel()

    return publish_channel


async def close_rabbit() -> None:
    """
    Закрывает соединение с RabbitMQ.
    """
    if conn and not conn.is_closed:
        await conn.close()
