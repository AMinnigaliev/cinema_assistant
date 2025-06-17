import logging

from src.core.config import settings
from src.db.postgres import Base, engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def create_database() -> None:
    logger.info("Инициализация базы данных PostgreSQL...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    except settings.pg_exceptions as e:
        logger.error("Ошибка при инициализации базы данных PostgreSQL: %s", e)

        raise ConnectionError(
            "Не удалось инициализировать базу данных PostgreSQL. "
            "Приложение завершает работу."
        )


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
