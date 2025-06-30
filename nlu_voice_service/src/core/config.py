import os

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    project_name: str = Field(default="movies", alias="PROJECT_NAME")
    service_name: str = Field(default="nlu_voice_service")

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    incoming_file_path: str = Field(
        default=os.path.join(base_dir, "voice_files", "incoming"),
        alias="INCOMING_FILE_PATH",
    )
    outgoing_file_path: str = Field(
        default=os.path.join(base_dir, "voice_files", "outgoing"),
        alias="OUTGOING_FILE_PATH",
    )

    movie_label: str = "MOVIE"
    model_labels: list[str] = [movie_label, ]
    model_dir_path: str = os.path.join(base_dir, "movie_ner_model")

    language_recognize: str = Field(
        default="ru-RU",
        alias="LANGUAGE_RECOGNIZE",
    )
    language_tts: str = Field(
        default="ru",
        alias="LANGUAGE_TTS",
    )
    tts_response_template: str = Field(
        default="По Вашему запросу найдены следующие фильмы: {found_movies}",
        alias="TTS_RESPONSE_TEMPLATE",
    )
    tts_not_found_response: str = Field(
        default="По Вашему запросу ничего не найдено",
        alias="TTS_NOT_FOUND_RESPONSE",
    )
    not_found_voice_path: str = Field(
        default=os.path.join(
            base_dir,
            "voice_files",
            "system",
            "not_found_voice.wav",
        ),
        alias="NOT_FOUND_VOICE_PATH",
    )

    # RMQ
    rabbitmq_user: str = Field(default="user", alias="RABBITMQ_USER")
    rabbitmq_pass: str = Field(default="password", alias="RABBITMQ_PASS")
    rabbitmq_host: str = Field(default="rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_amqp_port: int = Field(default=5672, alias="RABBITMQ_AMQP_PORT")
    rabbitmq_web_interface_port: int = Field(
        default=15672,
        alias="RABBITMQ_WEB_INTERFACE_PORT",
    )

    def get_rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}@"
            f"{self.rabbitmq_host}/"
        )

    declare_queue_name: str = Field(
        default="voice_assistant_request",
        alias="RABBITMQ_INCOMING_QUEUE_NAME",
    )

    # Clickhouse
    clickhouse_db: str = Field(
        default="nlp_database",
        alias="NLP_CLICKHOUSE_DB",
    )
    clickhouse_user: str = Field(
        default="clickhouse",
        alias="NLP_CLICKHOUSE_USER",
    )
    clickhouse_password: str = Field(
        default="password",
        alias="NLP_CLICKHOUSE_PASSWORD",
    )
    clickhouse_host: str = Field(
        default="nlp_clickhouse",
        alias="NLP_CLICKHOUSE_HOST",
    )
    clickhouse_http_port: int = Field(
        default=8123,
        alias="NLP_CLICKHOUSE_HTTP_PORT",
    )
    clickhouse_tcp_port: int = Field(
        default=9000,
        alias="NLP_CLICKHOUSE_TCP_PORT",
    )

    # MovieService
    movies_service_host: str = Field(
        default="movies_service",
        alias="MOVIES_SERVICE_HOST",
    )
    movies_service_port: int = Field(
        default=8000,
        alias="MOVIES_SERVICE_PORT",
    )
    movies_service_schema: str = Field(
        default="http",
        alias="MOVIES_SERVICE_SCHEMA",
    )

    def get_movies_service_url(self) -> str:
        return (
            f"{self.movies_service_schema}://"
            f"{self.movies_service_host}:{self.movies_service_port}"
        )

    movies_service_uri: dict[str, str] = {
        "search_films_by_title": "api/v1/movies/films/search",
    }


config = Config()
