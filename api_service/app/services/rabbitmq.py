import json
import aio_pika
from aio_pika import Message, DeliveryMode

from app.core.config import settings

# теперь используем settings.rabbitmq_url
_RABBIT_URL = settings.rabbitmq_url

_channel: aio_pika.Channel | None = None


async def _get_channel() -> aio_pika.Channel:
    global _channel
    if _channel and not _channel.is_closed:
        return _channel
    conn = await aio_pika.connect_robust(_RABBIT_URL)
    _channel = await conn.channel()
    return _channel


async def publish_voice_request(metadata: dict) -> None:
    ch = await _get_channel()
    queue = await ch.declare_queue(settings.rabbitmq_request_queue, durable=True)
    await ch.default_exchange.publish(
        Message(
            body=json.dumps(metadata, ensure_ascii=False).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        ),
        routing_key=queue.name,
    )


async def start_response_consumer(on_response=None) -> None:
    import asyncio, json
    from app.services.clickhouse_client import insert_response

    conn = await aio_pika.connect_robust(_RABBIT_URL)
    ch = await conn.channel()
    q = await ch.declare_queue(settings.rabbitmq_response_queue, durable=True)

    async def _handler(payload):
        await insert_response(
            user_id=payload["user_id"],
            request_id=payload["request_id"],
            correlation_id=payload["correlation_id"],
            transcription=payload.get("transcription", ""),
            tts_file_path=payload["tts_file_path"],
            found_entities=payload.get("found_entities"),
        )
        wav = settings.incoming_file_path / payload.get("incoming_voice_path", "")
        if wav.is_file(): wav.unlink(missing_ok=True)

    handler = on_response or _handler

    async def _process(msg: aio_pika.IncomingMessage):
        async with msg.process():
            payload = json.loads(msg.body)
            await handler(payload)

    await q.consume(_process, no_ack=False)
    while True: await asyncio.sleep(3600)
