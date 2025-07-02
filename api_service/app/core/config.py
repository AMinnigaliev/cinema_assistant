from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings
from redis.exceptions import RedisError


class Settings(BaseSettings):
    """Конфигурация Voice-API."""
    project_name: str = Field(default="movies", alias="PROJECT_NAME")

    # Безопасность
    login_url: str = "/api/v1/auth/users/login"
    secret_key: str = Field(default="practix", alias="SECRET_KEY")
    algorithm: str = "HS256"

    # Файловая система
    incoming_file_path: Path = Field(
        default=Path("/voice_files/incoming"), alias="INCOMING_FILE_PATH"
    )
    outgoing_file_path: Path = Field(
        default=Path("/voice_files/outgoing"), alias="OUTGOING_FILE_PATH"
    )

    # RabbitMQ
    rabbitmq_connection_url: str | None = Field(
        default=None, alias="RABBITMQ_CONNECTION_URL"
    )
    rabbitmq_user: str = Field(default="user", alias="RABBITMQ_USER")
    rabbitmq_password: str = Field(
        default="password", alias="RABBITMQ_PASS"
    )
    rabbitmq_host: str = Field(default="rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: int = 5672
    rabbitmq_request_queue: str = Field(
        default="voice_assistant_request", alias="RABBITMQ_INCOMING_QUEUE_NAME"
    )
    rabbitmq_response_queue: str = "voice_assistant_response"
    redis_db: int = Field(default=5, alias="REDIS_API_SERVICE")

    # ClickHouse
    clickhouse_host: str = Field(
        default="nlp_clickhouse", alias="NLP_CLICKHOUSE_HOST"
    )
    clickhouse_port: int = 9000
    clickhouse_database: str = Field(
        default="nlp_database", alias="NLP_CLICKHOUSE_DB"
    )
    clickhouse_user: str = Field(
        default="clickhouse", alias="NLP_CLICKHOUSE_USER"
    )
    clickhouse_password: str = Field(
        default="password", alias="NLP_CLICKHOUSE_PASSWORD"
    )

    # Auth_service
    auth_service_url: str | None = Field(
        default=None, alias="AUTH_SERVICE_URL"
    )
    auth_service_host: str = Field(
        default="localhost", alias="AUTH_SERVICE_HOST"
    )
    auth_service_port: int = Field(default=8000, alias="AUTH_SERVICE_PORT")

    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_exceptions: Any = (RedisError,)

    cache_expire_in_seconds: int = 300

    @property
    def auth_service_validate_url(self) -> str:
        """Собирает готовый URL auth-сервиса."""
        if self.auth_service_url:
            return self.auth_service_url
        return (
            f"http://{self.auth_service_host}:{self.auth_service_port}"
            f"/api/v1/auth/validate"
        )

    @property
    def rabbitmq_url(self) -> str:
        """Собирает готовый URL подключения к RabbitMQ."""
        if self.rabbitmq_connection_url:
            return self.rabbitmq_connection_url
        return (
            f"amqp://{self.rabbitmq_user}:"
            f"{self.rabbitmq_password}@"
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
