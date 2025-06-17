import asyncio
import logging.config
import os

from dotenv import load_dotenv
from sqlalchemy import select

from src.core.config import settings
from src.core.logger import LOGGING
from src.db.postgres import async_session
from src.models.user import User, UserRoleEnum

load_dotenv()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def create_superuser() -> None:
    """Функция для создания суперпользователя."""
    logger.info("Начало работы скрипта по созданию суперпользователя.")

    async with async_session() as db:
        existing_user = await db.execute(
            select(User).where(User.login == os.getenv("SUPERUSER_NAME"))
        )
        if existing_user.scalars().first():
            logger.info("Суперпользователь уже существует.")
            return

        superuser = User(
            login=os.getenv("SUPERUSER_NAME"),
            password=os.getenv("SUPERUSER_PASSWORD"),
            role=UserRoleEnum.SUPERUSER,
            country="unknown",
            partition_country="unknown",
        )

        try:
            db.add(superuser)
            await db.commit()

        except settings.sql_exceptions as e:
            logger.error("Ошибка при добавлении суперпользователя: %s", e)
            await db.rollback()
            raise

    logger.info("Суперпользователь создан.")


async def main():
    await create_superuser()


if __name__ == "__main__":
    asyncio.run(main())
