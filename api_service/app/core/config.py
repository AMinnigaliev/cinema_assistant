from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    VOICE_SERVICE_URL: str
    MEDIA_ROOT: Path = Path("./app/media")

    class Config:
        env_file = ".env"

settings = Settings()
