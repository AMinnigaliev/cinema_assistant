import json
from datetime import datetime
from typing import Optional, Dict, Any
from clickhouse_driver import Client
from app.core.config import settings

# синхронный клиент ClickHouse
client = Client(
    host=settings.clickhouse_host,
    port=settings.clickhouse_port,
    database=settings.clickhouse_database,
    user=settings.clickhouse_user,
    password=settings.clickhouse_password,
)

# создаём таблицу, если ещё нет
client.execute("""
CREATE TABLE IF NOT EXISTS voice_assistant_request (
    user_id         String,
    request_id      String,
    correlation_id  String,
    status          String,
    transcription   String,
    tts_file_path   String,
    stt_file_path   String,
    found_entities  String,
    timestamp       DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, request_id)
TTL timestamp + INTERVAL 30 DAY
""")

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
    found_entities: Optional[Dict[str, Any]] = None,
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

def get_voice_request(request_id: str) -> Optional[Any]:
    """
    Забирает из ClickHouse самую свежую запись по request_id.
    Возвращает dict с полями таблицы или None, если ничего не найдено.
    """
    rows = client.execute(
        """
        SELECT
            user_id,
            request_id,
            correlation_id,
            status,
            transcription,
            tts_file_path,
            stt_file_path,
            found_entities,
            timestamp
        FROM voice_assistant_request
        WHERE request_id = %(rid)s
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        {"rid": request_id},
    )
    if not rows:
        return None

    (
        user_id,
        req_id,
        corr_id,
        status,
        transcription,
        tts_path,
        stt_path,
        found_json,
        ts,
    ) = rows[0]

    return {
        "user_id": user_id,
        "request_id": req_id,
        "correlation_id": corr_id,
        "status": status,
        "transcription": transcription,
        "tts_file_path": tts_path,
        "stt_file_path": stt_path,
        "found_entities": json.loads(found_json),
        "timestamp": ts,
    }
