from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Конфигурация Voice-API (читается из переменных окружения)."""

    # Файловая система
    incoming_file_path: Path = Path("/voice_files/incoming")
    outgoing_file_path: Path = Path("/voice_files/outgoing")

    # RabbitMQ
    rabbitmq_user: str = "user"
    rabbitmq_password: str = "password"
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_incoming_queue: str = "voice_assistant_request"
    rabbitmq_response_queue: str = "voice_assistant_response"

    # ClickHouse
    clickhouse_host: str = "nlp_clickhouse"
    clickhouse_port: int = 9000
    clickhouse_database: str = "nlp_database"
    clickhouse_user: str = "clickhouse"
    clickhouse_password: str = "password"

    class Config:
        env_file = ".env"
        env_prefix = "VOICE_API_"
        case_sensitive = False


settings = Settings() 
