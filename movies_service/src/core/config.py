import os
from functools import cached_property
from typing import Any

from asyncpg.exceptions import \
    ConnectionDoesNotExistError as PGConnectionDoesNotExistError
from asyncpg.exceptions import PostgresError
from asyncpg.exceptions import SyntaxOrAccessError as PGSyntaxOrAccessError
from elastic_transport import TransportError as ESTransportError
from elasticsearch import ApiError as ESApiError
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError


class Settings(BaseSettings):
    project_name: str = Field(default="movies", alias="PROJECT_NAME")
    service_name: str = Field(
        default="movies_service", alias="MOVIES_SERVICE_NAME"
    )
    env_type: str = Field(default="prod", alias="ENV_TYPE")
    base_dir: str = Field(
        default_factory=lambda: os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    @computed_field
    @property
    def is_prod_env(self) -> bool:
        """
        Флаг, указывает какое используется окружение.
        - prod:
        - develop: устанавливается при разработке.

        @rtype: bool
        @return:
        """
        return self.env_type == "prod"

    auth_service_host: str = Field(
        default="localhost", alias="AUTH_SERVICE_HOST"
    )
    auth_service_port: int = Field(default=8000, alias="AUTH_SERVICE_PORT")

    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_rate_limit_db: int = Field(default=1, alias="REDIS_RATE_LIMIT_DB")

    elastic_host: str = Field(default="elasticsearch", alias="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, alias="ELASTIC_PORT")
    elastic_scheme: str = Field(default="http", alias="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_password: str = Field(default="password", alias="ELASTIC_PASSWORD")

    pg_user: str = Field(default="user", alias="PG_USER")
    pg_password: str = Field(default="password", alias="PG_PASSWORD")
    pg_host: str = Field(default="postgres", alias="PG_HOST")
    pg_port: int = Field(default=5432, alias="PG_PORT")
    pg_name: str = Field(default="name", alias="PG_NAME")

    elastic_exceptions: Any = (ESApiError, ESTransportError)
    redis_exceptions: Any = (RedisError,)
    pg_exceptions: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )

    # Безопасность
    login_url: str = "/api/v1/auth/users/login"
    secret_key: str = Field(default="practix", alias="SECRET_KEY")
    algorithm: str = "HS256"

    elastic_response_size: int = 1000
    cache_expire_in_seconds: int = 300

    rate_limit: int = Field(default=30, alias="RATE_LIMIT")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    @computed_field
    @property
    def redis_rate_limit_url(self) -> str:
        return (
            f"redis://:{self.redis_password}@{self.redis_host}:"
            f"{self.redis_port}/{self.redis_rate_limit_db}"
        )

    @cached_property
    def auth_service_url(self) -> str:
        return (
            f"http://{self.auth_service_host}:{self.auth_service_port}"
            f"/api/v1/auth"
        )


settings = Settings()
