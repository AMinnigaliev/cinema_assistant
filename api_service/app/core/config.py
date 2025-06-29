from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация Voice-API (читается из переменных окружения)."""
    project_name: str = Field(default="movies", alias="PROJECT_NAME")

    # Файловая система
    incoming_file_path: Path = Path("/voice_files/incoming")
    outgoing_file_path: Path = Path("/voice_files/outgoing")

    # RabbitMQ
    rabbitmq_user: str = Field(default="user", alias="RABBITMQ_USER")
    rabbitmq_password: str = Field(
        default="password", alias="RABBITMQ_PASS"
    )
    rabbitmq_host: str = Field(default="rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: int = 5672
    rabbitmq_incoming_queue: str = "voice_assistant_request"
    rabbitmq_response_queue: str = "voice_assistant_response"

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

    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )

    class Config:
        env_file = ".env"
        env_prefix = "VOICE_API_"
        case_sensitive = False


settings = Settings()
