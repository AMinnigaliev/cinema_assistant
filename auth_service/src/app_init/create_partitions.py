import asyncio
import logging.config

from sqlalchemy import text

from src.core.logger import LOGGING
from src.db.postgres import engine

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

PARTITION_SQL = [
    """
    CREATE TABLE IF NOT EXISTS auth.users_sign_in_smart PARTITION OF
    auth.login_history FOR VALUES IN ('smart')
    """,
    """
    CREATE TABLE IF NOT EXISTS auth.users_sign_in_mobile PARTITION OF
    auth.login_history FOR VALUES IN ('mobile')
    """,
    """
    CREATE TABLE IF NOT EXISTS auth.users_sign_in_web PARTITION OF
    auth.login_history FOR VALUES IN ('web')
    """,
    """
    CREATE TABLE IF NOT EXISTS auth.users_sign_in_unknown PARTITION OF
    auth.login_history FOR VALUES IN ('unknown')
    """,
    """
    CREATE TABLE IF NOT EXISTS auth.users_from_russia PARTITION OF
    auth.users FOR VALUES IN ('RUS')
    """,
    """
    CREATE TABLE IF NOT EXISTS auth.users_from_abroad PARTITION OF
    auth.users FOR VALUES IN ('Abroad')
    """,
    """
    CREATE TABLE IF NOT EXISTS auth.users_from_unknown PARTITION OF
    auth.users FOR VALUES IN ('unknown')
    """
]


async def create_partitions() -> None:
    """Функция для создания партиций."""
    logger.info("Начало работы скрипта по созданию партиций.")

    async with engine.begin() as conn:
        for stmt in PARTITION_SQL:
            logger.info(f"Выполнение: {stmt.strip()}")
            await conn.execute(text(stmt))

    logger.info("Партиции созданы.")


async def main():
    await create_partitions()


if __name__ == "__main__":
    asyncio.run(main())
