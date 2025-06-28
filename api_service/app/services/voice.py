from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.services.clickhouse_client import insert_request
from app.services.rabbitmq import publish_voice_request


async def send_to_voice_service(audio_path: Path, request_id: str, user_id: str) -> None:
    """
    Сохраняем факт запроса в ClickHouse и отправляем мета-данные в RabbitMQ.
    """
    correlation_id = str(uuid4())

    insert_request(
        user_id=user_id,
        request_id=request_id,
        correlation_id=correlation_id,
        stt_file_path=str(audio_path),
    )

    metadata = {
        "request_id": request_id,
        "user_id": user_id,
        "correlation_id": correlation_id,
        "reply_to": settings.rabbitmq_response_queue,
        "incoming_voice_path": audio_path.name,
    }

    await publish_voice_request(metadata)
