from contextlib import contextmanager

from infi.clickhouse_orm import Database

from core import nlp_config, logger
from database.meta_ import SingletonMeta


class ClickhouseSession(metaclass=SingletonMeta):
    """Класс - сессия с DB Clickhouse."""

    ERROR_EXC_TYPES = [Exception,]

    def __init__(self):
        self._db = Database(
            db_name=nlp_config.clickhouse_db,
            db_url=(
                f"http://{nlp_config.clickhouse_host}:"
                f"{nlp_config.clickhouse_http_port}"
            ),
            username=nlp_config.clickhouse_user,
            password=nlp_config.clickhouse_password,
            readonly=False,
        )

    @property
    def session(self) -> Database:
        return self._db

    @contextmanager
    def context_session(self):
        try:
            yield self._db

        except tuple(self.ERROR_EXC_TYPES) as ex:
            logger.error(f"ClickHouse ORM error: {ex}")
            raise

        finally:
            pass


clickhouse_session = ClickhouseSession()
