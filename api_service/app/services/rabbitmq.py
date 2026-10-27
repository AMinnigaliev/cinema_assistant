import asyncio
import json
import logging.config

from aio_pika import DeliveryMode, IncomingMessage, Message

from app.core.config import settings
from app.core.logger import LOGGING
from app.db.rebbitmq import get_rabbit_connect, get_rabbit_publish_channel
from app.services.clickhouse_client import insert_response

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def publish_voice_request(metadata: dict) -> None:
    """Шлём сообщение в очередь «voice_assistant_request»."""
    ch = await get_rabbit_publish_channel()
    queue = await ch.declare_queue(settings.rabbitmq_request_queue)

    correlation_id = metadata["correlation_id"]
    reply_to = metadata["reply_to"]

    body_data = {
        key: value
        for key, value in metadata.items()
        if key not in ("correlation_id", "reply_to")
    }

    await ch.default_exchange.publish(
        Message(
            body=json.dumps(body_data, ensure_ascii=False).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            correlation_id=correlation_id,
            reply_to=reply_to,
        ),
        routing_key=queue.name,
    )


async def start_response_consumer(on_response=None) -> None:
    """Получаем ответы от голосового сервиса."""
    conn = await get_rabbit_connect()
    ch = await conn.channel()
    queue = await ch.declare_queue(settings.rabbitmq_response_queue)

    async def _handler(payload, correlation_id):
        if "error" in payload:
            logger.error("Voice service returned an error: %s", payload)
            return

        required_fields = {
            "request_id",
            "user_id",
            "output_voice_path",
            "out_text",
        }
        missing_fields = required_fields - payload.keys()

        if missing_fields:
            logger.error(
                "Invalid voice response: missing fields %s; payload=%s",
                sorted(missing_fields),
                payload,
            )
            return

        await insert_response(
            user_id=payload["user_id"],
            request_id=payload["request_id"],
            correlation_id=correlation_id,
            transcription=payload["out_text"],
            tts_file_path=payload["output_voice_path"],
            found_entities=None,
        )

    async def _process(msg: IncomingMessage):
        async with msg.process():
            payload = json.loads(msg.body)

            logger.info("Received voice response: %s", payload)
            logger.info("AMQP correlation_id: %s", msg.correlation_id)

            if on_response:
                await on_response(payload)
            else:
                await _handler(payload, msg.correlation_id)

    await queue.consume(_process, no_ack=False)

    while True:
        await asyncio.sleep(3600)
