import json
from datetime import datetime
from typing import Any, Dict, Optional

from app.db.clickhouse import get_clickhouse_client


async def insert_request(
    user_id: str,
    request_id: str,
    correlation_id: str,
    stt_file_path: str,
) -> None:
    client = await get_clickhouse_client()
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


async def insert_response(
    user_id: str,
    request_id: str,
    correlation_id: str,
    transcription: str,
    tts_file_path: str,
    found_entities: Optional[Dict[str, Any]] = None,
) -> None:
    client = await get_clickhouse_client()
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


async def get_voice_request(request_id: str) -> Optional[Any]:
    """
    Забирает из ClickHouse самую свежую запись по request_id.
    Возвращает dict с полями таблицы или None, если ничего не найдено.
    """
    client = await get_clickhouse_client()
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
