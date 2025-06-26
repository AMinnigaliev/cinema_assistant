from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    skip_test: str = Field(default="true", alias="SKIP_TEST")

    auth_service_host: str = Field(
        default="localhost", alias="AUTH_SERVICE_HOST"
    )
    auth_service_port: int = Field(default=8000, alias="AUTH_SERVICE_PORT")

    movies_service_host: str = Field(
        default="localhost", alias="MOVIES_SERVICE_HOST"
    )
    movies_service_port: int = Field(default=8008, alias="MOVIES_SERVICE_PORT")

    redis_host: str = Field(default="127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="password", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    elastic_schema: str = Field(default="http", alias="ELASTIC_SCHEMA")
    elastic_name: str = Field(default="elastic", alias="ELASTIC_USERNAME")
    elastic_host: str = Field(default="127.0.0.1", alias="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, alias="ELASTIC_PORT")
    elastic_password: str = Field(default="123qwe", alias="ELASTIC_PASSWORD")

    postgres_db: str = Field(default="name", alias="PG_NAME")
    postgres_user: str = Field(default="user", alias="PG_USER")
    postgres_host: str = Field(default="127.0.0.1", alias="PG_HOST")
    postgres_port: int = Field(default=5432, alias="PG_PORT")
    postgres_password: str = Field(default="password", alias="PG_PASSWORD")

    secret_key: str = Field(default="practix", alias="SECRET_KEY")
    algorithm: str = "HS256"

    request_timeout: int = Field(default=1 * 30, alias="REQUEST_TIME_OUT")
    max_connection_attempt: int = Field(
        default=5, alias="MAX_CONNECTION_ATTEMPT"
    )
    break_time_sec: int = Field(default=5, alias="BREAK_TIME_SEC")

    @computed_field
    @property
    def auth_service_url(self) -> str:
        return f"http://{self.auth_service_host}:{self.auth_service_port}"

    @computed_field
    @property
    def movies_service_url(self) -> str:
        return f"http://{self.movies_service_host}:{self.movies_service_port}"


config = TestSettings()
