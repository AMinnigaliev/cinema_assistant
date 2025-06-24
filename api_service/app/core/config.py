from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    INCOMING_FILE_PATH: Path = Field(default=Path("/voice_files/incoming"))
    OUTGOING_FILE_PATH: Path = Field(default=Path("/voice_files/outgoing"))

    RABBITMQ_USER: str = Field(default="user")
    RABBITMQ_PASSWORD: str = Field(default="password")
    RABBITMQ_HOST: str = Field(default="rabbitmq")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_INCOMING_QUEUE: str = Field(default="voice_assistant_request")
    RABBITMQ_RESPONSE_QUEUE: str = Field(default="voice_assistant_response")

    CLICKHOUSE_HOST: str = Field(default="nlp_clickhouse")
    CLICKHOUSE_PORT: int = Field(default=9000)
    CLICKHOUSE_DATABASE: str = Field(default="nlp_database")
    CLICKHOUSE_USER: str = Field(default="clickhouse")
    CLICKHOUSE_PASSWORD: str = Field(default="password")

    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
        )

    class Config:
        env_file = ".env"


settings = Settings()
