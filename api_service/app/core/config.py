from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Конфигурация Voice-API (переменные окружения и .env)."""

    # Файловая система
    incoming_file_path: Path = Field(default=Path("/voice_files/incoming"), alias="INCOMING_FILE_PATH")
    outgoing_file_path: Path = Field(default=Path("/voice_files/outgoing"), alias="OUTGOING_FILE_PATH")

    # RabbitMQ
    rabbitmq_connection_url: str | None = Field(default=None, alias="RABBITMQ_CONNECTION_URL")
    rabbitmq_user: str = Field(alias="RABBITMQ_USER")
    rabbitmq_password: str = Field(alias="RABBITMQ_PASS")
    rabbitmq_host: str = Field(alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(alias="RABBITMQ_AMQP_PORT")
    rabbitmq_request_queue: str = Field(alias="RABBITMQ_INCOMING_QUEUE")
    rabbitmq_response_queue: str = Field(alias="RABBITMQ_RESPONSE_QUEUE")

    # ClickHouse
    clickhouse_host: str = Field(alias="NLP_CLICKHOUSE_HOST")
    clickhouse_port: int = Field(alias="NLP_CLICKHOUSE_TCP_PORT")
    clickhouse_database: str = Field(alias="NLP_CLICKHOUSE_DB")
    clickhouse_user: str = Field(alias="NLP_CLICKHOUSE_USER")
    clickhouse_password: str = Field(alias="NLP_CLICKHOUSE_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

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


# Выводим переменные для отладки
print("==== ENVIRONMENT ====")
for k, v in os.environ.items():
    if "CLICKHOUSE" in k or "RABBIT" in k:
        print(f"{k} = {v}")
print("=====================")

# Создание экземпляра
settings = Settings()
