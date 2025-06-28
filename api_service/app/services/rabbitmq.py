import asyncio
import json
from pathlib import Path

from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings
from app.dependencies.rabbitmq_config import get_rabbitmq_url
from app.services.clickhouse_client import insert_response


async def publish_voice_request(metadata: dict) -> None:
    """
    Шлём сообщение в очередь «voice_assistant_request».
    """
    conn = await connect_robust(get_rabbitmq_url())
    async with conn.channel() as ch:
        await ch.default_exchange.publish(
            Message(
                json.dumps(metadata).encode(),
                content_type="application/json",
                correlation_id=metadata["correlation_id"],
                delivery_mode=2,
            ),
            routing_key=settings.rabbitmq_incoming_queue,
        )
    await conn.close()


async def _on_response(message: AbstractIncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body)

        insert_response(
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
    Держим persistent-соединение, потребляем очередь с распознанными ответами.
    """
    loop = asyncio.get_event_loop()
    conn = await connect_robust(get_rabbitmq_url(), loop=loop)
    ch = await conn.channel()
    await ch.set_qos(prefetch_count=10)

    q = await ch.declare_queue(settings.rabbitmq_response_queue, durable=True)
    await q.consume(_on_response)

    loop.create_task(_keep_alive(conn))


async def _keep_alive(conn):
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await conn.close()
