import asyncio
import logging.config

from clickhouse_driver import Client
from clickhouse_driver import errors as ch_errors

from app.core.config import settings
from app.core.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

clickhouse_client: Client | None = None


async def init_clickhouse_client(retries: int = 2, delay: float = 2) -> Client:
    global clickhouse_client

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                "Попытка %d/%d: подключаемся к ClickHouse...",
                attempt, retries
            )
            client = Client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                database=settings.clickhouse_database,
                user=settings.clickhouse_user,
                password=settings.clickhouse_password,
                connect_timeout=5,
                send_receive_timeout=10,
            )

            # Тестовый запрос
            client.execute("SELECT 1")
            clickhouse_client = client
            logger.info("Успешно подключились к ClickHouse.")
            return clickhouse_client

        except (ch_errors.Error, OSError) as e:
            logger.error(
                "Ошибка подключения к ClickHouse (попытка %d/%d): %s",
                attempt, retries, e
            )
            if attempt < retries:
                logger.info(
                    "Ждём %.1f сек. перед следующей попыткой...", delay
                )
                await asyncio.sleep(delay)
            else:
                logger.critical(
                    "Не удалось подключиться к ClickHouse после %d попыток.",
                    retries
                )
                raise

    raise RuntimeError("ClickHouse client не инициализирован")


async def get_clickhouse_client() -> Client:
    """
    Возвращает экземпляр Client для ClickHouse.
    При первом вызове или в случае падения соединения выполняет
    не более `retries` попыток подключения с задержкой `delay` секунд,
    проверяя его тестовым запросом SELECT 1.
    """
    global clickhouse_client

    if clickhouse_client is not None:
        try:
            # Проверяем живость существующего клиента
            clickhouse_client.execute("SELECT 1")
            return clickhouse_client
        except ch_errors.Error as e:
            logger.warning("Существующий ClickHouse client упал: %s", e)
            clickhouse_client = None

    # Попытка установить новое соединение
    return await init_clickhouse_client()
