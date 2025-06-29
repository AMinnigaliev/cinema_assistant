import asyncio
import logging.config

from clickhouse_driver import errors as ch_errors

from app.core.logger import LOGGING
from app.db.clickhouse import get_clickhouse_client

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def create_voice_table() -> None:
    """
    Создаёт таблицу voice_assistant_request в ClickHouse, если её ещё нет.
    """
    logger.info("Начало работы скрипта по созданию таблицы в ClickHouse.")

    try:
        clickhouse_client = await get_clickhouse_client()

        await asyncio.to_thread(
            clickhouse_client.execute,
            """
            CREATE TABLE IF NOT EXISTS voice_assistant_request (
                user_id String,
                request_id String,
                correlation_id String,
                status String,
                transcription String,
                tts_file_path String,
                stt_file_path String,
                found_entities String,
                timestamp DateTime
            ) ENGINE = MergeTree()
            ORDER BY (user_id, request_id)
            TTL timestamp + INTERVAL 30 DAY
            """
        )

        logger.info(
            "Таблица voice_assistant_request успешно создана "
            "(или уже существует)."
        )

    except ch_errors.Error as e:
        logger.error("Ошибка при выполнении DDL в ClickHouse: %s", e)
        raise

    except Exception as e:
        logger.critical(
            "Непредвиденная ошибка при инициализации ClickHouse: %s", e
        )
        raise


async def main() -> None:
    await create_voice_table()


if __name__ == "__main__":
    asyncio.run(main())
