import json
from datetime import datetime
from typing import Dict, Optional

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
    found_entities: Optional[Dict] = None,
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
