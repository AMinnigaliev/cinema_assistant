import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from logger import logger
from settings import config
from utils.pg_helpers import make_pg_engine


def wait_for_postgres() -> None:
    """
    Пингуем PostgreSQL через создание соединения.
    Если не удаётся подключиться, повторяем попытки
    до config.max_connection_attempt с паузой config.break_time_sec.
    """
    engine = make_pg_engine()
    attempt = 0

    while attempt < config.max_connection_attempt:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            engine.dispose()
            logger.debug("Connection to PostgreSQL has been made")
            return

        except (OperationalError, ConnectionError) as ex:
            logger.error(f"PostgreSQL is not yet available. Error: {ex}")
            attempt += 1
            time.sleep(config.break_time_sec)

    engine.dispose()
    raise ConnectionError("number of connection attempts exceeded")


if __name__ == "__main__":
    try:
        wait_for_postgres()

    except Exception as e:
        logger.error(f"Failed waiting for PostgreSQL: {e}")
        raise
