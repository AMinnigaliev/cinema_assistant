import json
import logging.config
from pathlib import Path

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings
from app.core.logger import LOGGING
from app.db.rebbitmq import get_rabbit_connect, get_rabbit_publish_channel
from app.services.clickhouse_client import insert_response

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def publish_voice_request(metadata: dict) -> None:
    """Шлём сообщение в очередь «voice_assistant_request»."""
    ch = await get_rabbit_publish_channel()
    await ch.default_exchange.publish(
        Message(
            json.dumps(metadata).encode(),
            content_type="application/json",
            correlation_id=metadata["correlation_id"],
            delivery_mode=2,
        ),
        routing_key=settings.rabbitmq_incoming_queue,
    )


async def _on_response(message: AbstractIncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body)

        await insert_response(
            user_id=payload["user_id"],
            request_id=payload["request_id"],
            correlation_id=payload.get("correlation_id"),
            transcription=payload.get("out_text", ""),
            tts_file_path=payload.get("output_voice_path", ""),
            found_entities=payload.get("found_entities"),
        )

        # убираем tts-файл, если он был сохранён на диске ASR-сервиса
        if p := payload.get("output_voice_path"):
            f = Path(p)
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass


async def start_response_consumer() -> None:
    """
    Инициализирует Robust‑consumer для очереди ответов.
    Подписка сохраняется и автоматически восстанавливается при разрывах
    соединения.
    """
    conn = await get_rabbit_connect()
    ch = await conn.channel()
    await ch.set_qos(prefetch_count=10)
    queue = await ch.declare_queue(
        settings.rabbitmq_response_queue,
        durable=True,
    )
    await queue.consume(_on_response, no_ack=False)
    logger.info("Robust consumer для очереди '%s' инициализирован", queue.name)
