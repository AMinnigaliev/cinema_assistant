import asyncio
import logging.config

from sqlalchemy import text

from src.core.logger import LOGGING
from src.db.postgres import engine

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def create_auth_schema() -> None:
    """Функция создания схемы auth в postgres."""
    logger.info("Начало работы скрипта по созданию схемы auth.")

    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth;"))

    logger.info("Схема создана.")


async def main():
    await create_auth_schema()


if __name__ == "__main__":
    asyncio.run(main())
