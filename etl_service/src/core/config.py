import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    project_name: str = Field(default="movies", alias="PROJECT_NAME")
    service_name: str = Field(default="etl_service", alias="ETL_SERVICE_NAME")

    env_type: str = Field(default="prod", alias="ENV_TYPE")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    redis_host: str = Field(default="127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_db_movies: int = Field(default=3, alias="REDIS_ETL_DB_MOVIES")
    redis_db_events: int = Field(default=4, alias="REDIS_ETL_DB_EVENTS")

    elastic_schema: str = Field(default="film_work", alias="ELASTIC_SCHEME")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_host: str = Field(default="127.0.0.1", alias="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, alias="ELASTIC_PORT")
    elastic_password: str = Field(default="123qwe", alias="ELASTIC_PASSWORD")

    postgres_driver_name: str = Field(
        default="postgresql+asyncpg", alias="PG_DRIVER_NAME"
    )
    postgres_db: str = Field(default="postgres", alias="PG_NAME")
    postgres_user: str = Field(default="user", alias="PG_USER")
    postgres_password: str = Field(default="password", alias="PG_PASSWORD")
    postgres_host: str = Field(default="127.0.0.1", alias="PG_HOST")
    postgres_port: int = Field(default=5432, alias="PG_PORT")

    etl_task_trigger: str = Field(default="interval", alias="ETL_TASK_TRIGGER")
    etl_movies_task_interval_sec: int = Field(
        default=1 * 60, alias="ETL_MOVIES_TASK_INTERVAL_SEC"
    )
    etl_movies_select_limit: int = Field(
        default=1 * 250, alias="ETL_MOVIES_SELECT_LIMIT"
    )


config = Settings()
