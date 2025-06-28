import json
from datetime import datetime
from typing import Optional, Dict

from clickhouse_driver import Client
from app.core.config import settings

# создаём синхронный клиент (дальше переведём на aiochclient)
client = Client(
    host=settings.clickhouse_host,
    port=settings.clickhouse_port,
    database=settings.clickhouse_database,
    user=settings.clickhouse_user,
    password=settings.clickhouse_password,
)

# таблица под запросы пользователя
client.execute(
    """
    CREATE TABLE IF NOT EXISTS voice_assistant_request (
        user_id String,
        request_id String,
        correlation_id String,
        status String,
        transcription String,
        tts_file_path String,
        stt_file_path String,
        found_entities String,
        timestamp DateTime
    ) ENGINE = MergeTree()
    ORDER BY (user_id, request_id)
    TTL timestamp + INTERVAL 30 DAY
"""
)


def insert_request(
    user_id: str,
    request_id: str,
    correlation_id: str,
    stt_file_path: str,
) -> None:
    client.execute(
        "INSERT INTO voice_assistant_request VALUES",
        [
            (
                user_id,
                request_id,
                correlation_id,
                "queued",
                "",
                "",
                stt_file_path,
                "{}",
                datetime.utcnow(),
            )
        ],
    )


def insert_response(
    user_id: str,
    request_id: str,
    correlation_id: str,
    transcription: str,
    tts_file_path: str,
    found_entities: Optional[Dict] = None,
) -> None:
    client.execute(
        "INSERT INTO voice_assistant_request VALUES",
        [
            (
                user_id,
                request_id,
                correlation_id,
                "done",
                transcription,
                tts_file_path,
                "",
                json.dumps(found_entities or {}, ensure_ascii=False),
                datetime.utcnow(),
            )
        ],
    )
