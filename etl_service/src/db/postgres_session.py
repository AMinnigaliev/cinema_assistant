from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy.engine import URL
from sqlalchemy.exc import InterfaceError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (AsyncEngine, async_scoped_session,
                                    async_sessionmaker, create_async_engine)

from core import config
from core.logger import logger
from utils.abstract import SingletonMeta

URL_ = URL.create(
    drivername=config.postgres_driver_name,
    database=config.postgres_db,
    username=config.postgres_user,
    password=config.postgres_password,
    host=config.postgres_host,
    port=config.postgres_port,
)


class BaseAsyncSession(metaclass=SingletonMeta):
    ERROR_EXC_TYPES = (SQLAlchemyError, InterfaceError)

    def __init__(self, async_engine: AsyncEngine) -> None:
        self._async_engine = async_engine
        self._async_session_factory = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
        )


class AsyncScopedSession(BaseAsyncSession):

    def __init__(self, *args, task=current_task, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._task = task
        self._scoped_session = None

    @property
    def scoped_session(self):
        if not self._scoped_session:
            self._scoped_session = async_scoped_session(
                session_factory=self._async_session_factory,
                scopefunc=self._task,
            )

        return self._scoped_session

    @asynccontextmanager
    async def context_session(self):
        session = self.scoped_session()

        try:
            if not session:
                raise RuntimeError("Session factory not initialized")

            yield session

        except self.ERROR_EXC_TYPES as ex:
            logger.error(f"SQLAlchemy(Postgres) error: {ex}")
            if session:
                await session.rollback()

        except Exception as ex:
            logger.error(f"Not correct SQLAlchemy(Postgres) error: {ex}")

            if session:
                await session.rollback()

        finally:
            if session:
                await session.close()


def get_async_engine(url_: str | URL) -> AsyncEngine:
    return create_async_engine(
        url=url_,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
    )


pg_scoped_session = AsyncScopedSession(
    async_engine=get_async_engine(url_=URL_)
)
