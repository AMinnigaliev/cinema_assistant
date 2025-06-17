import os
from typing import Any, ClassVar

from asyncpg.exceptions import \
    ConnectionDoesNotExistError as PGConnectionDoesNotExistError
from asyncpg.exceptions import PostgresError
from asyncpg.exceptions import SyntaxOrAccessError as PGSyntaxOrAccessError
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.exc import OperationalError as SQLOperationalError
from sqlalchemy.exc import SQLAlchemyError


class Settings(BaseSettings):
    project_name: str = Field(default="movies", alias="PROJECT_NAME")
    service_name: str = Field(
        default="auth_service", alias="AUTH_SERVICE_NAME"
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

    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_rate_limit_db: int = Field(default=2, alias="REDIS_RATE_LIMIT_DB")

    elastic_host: str = Field(default="elasticsearch", alias="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, alias="ELASTIC_PORT")
    elastic_scheme: str = Field(default="http", alias="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_password: str = Field(default="123qwe", alias="ES_PASSWORD")

    pg_user: str = Field(default="user", alias="PG_USER")
    pg_password: str = Field(default="password", alias="PG_PASSWORD")
    pg_host: str = Field(default="postgres", alias="PG_HOST")
    pg_port: int = Field(default=5432, alias="PG_PORT")
    pg_name: str = Field(default="name", alias="PG_NAME")

    # Exceptions
    redis_exceptions: Any = (RedisError,)
    pg_exceptions: Any = (
        PostgresError, PGConnectionDoesNotExistError, PGSyntaxOrAccessError
    )
    sql_exceptions: Any = (
        SQLAlchemyError, SQLIntegrityError, SQLOperationalError
    )

    # OAuth Yandex
    yandex_client_id: str = Field(..., alias="YANDEX_CLIENT_ID")
    yandex_client_secret: str = Field(..., alias="YANDEX_CLIENT_SECRET")
    yandex_redirect_uri: str = Field(..., alias="YANDEX_REDIRECT_URI")
    yandex_auth_url: str = "https://oauth.yandex.ru/authorize"

    # Безопасность
    login_url: str = "/api/v1/auth/users/login"
    token_revoke: ClassVar[bytes] = b"revoked"
    token_active: ClassVar[bytes] = b"active"
    secret_key: str = Field(default="practix", alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    rate_limit: int = Field(default=50, alias="RATE_LIMIT")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    @computed_field
    @property
    def redis_rate_limit_url(self) -> str:
        return (
            f"redis://:{self.redis_password}@{self.redis_host}:"
            f"{self.redis_port}/{self.redis_rate_limit_db}"
        )


settings = Settings()
