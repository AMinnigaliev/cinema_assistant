import json
import logging.config

from aio_pika import DeliveryMode, IncomingMessage, Message

from app.core.config import settings
from app.core.logger import LOGGING
from app.db.rebbitmq import get_rabbit_connect, get_rabbit_publish_channel

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def publish_voice_request(metadata: dict) -> None:
    """Шлём сообщение в очередь «voice_assistant_request»."""
    ch = await get_rabbit_publish_channel()
    queue = await ch.declare_queue(
        settings.rabbitmq_request_queue, durable=True
    )
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

    conn = await get_rabbit_connect()
    ch = await conn.channel()
    queue = await ch.declare_queue(
        settings.rabbitmq_response_queue, durable=True
    )

    async def _handler(payload):
        await insert_response(
            user_id=payload["user_id"],
            request_id=payload["request_id"],
            correlation_id=payload["correlation_id"],
            transcription=payload.get("transcription", ""),
            tts_file_path=payload["tts_file_path"],
            found_entities=payload.get("found_entities"),
        )
        wav = settings.incoming_file_path / payload.get(
            "incoming_voice_path", ""
        )
        if wav.is_file(): wav.unlink(missing_ok=True)

    handler = on_response or _handler

    async def _process(msg: IncomingMessage):
        async with msg.process():
            payload = json.loads(msg.body)
            await handler(payload)

    await queue.consume(_process, no_ack=False)
    while True: await asyncio.sleep(3600)
