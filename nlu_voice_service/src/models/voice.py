import os
from typing import Any

from pydantic import BaseModel

from core import config, SearchEngineError


class BaseVoiceData(BaseModel):
    """Базовый класс данных для аудио-файлов."""

    request_id: str
    user_id: str


class IncomingVoiceData(BaseVoiceData):
    """Класс данных для входящих аудио-файлов."""

    incoming_voice_name: str
    incoming_voice_path: str | None = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.incoming_voice_path = os.path.join(
            config.incoming_file_path,
            self.incoming_voice_name,
        )

        if not os.path.exists(self.incoming_voice_path):
            raise SearchEngineError(
                message=f"not found incoming file({self.incoming_voice_path})",
            )


class OutgoingVoiceData(BaseVoiceData):
    """Класс данных для исходящих аудио-файлов."""

    output_voice_path: str
    out_text: str
