import json
import asyncio
import os
import time
from pathlib import Path

from aio_pika import connect_robust, Message, IncomingMessage
from aio_pika.abc import AbstractExchange

from core import config, logger
from core.custom_exceprions import SearchEngineError
from search_engine import VoiceSearchEngine


async def on_message(
    message: IncomingMessage,
    default_exchange: AbstractExchange,
) -> None:
    """
    Обработчик входящих сообщений от RMQ-rpc клиента.

    @type message: IncomingMessage
    @param message:
    @type default_exchange: AbstractExchange
    @param default_exchange:
    @rtype:
    @return:
    """
    async with message.process():
        if message.reply_to is None:
            logger.error("[!] No reply_to in message, cannot send response")
            return

        try:
            start_t = time.perf_counter()
            incoming_d = json.loads(message.body.decode())

            search_engine = VoiceSearchEngine(incoming_d=incoming_d)
            result = await search_engine.run()

        except SearchEngineError as ex:
            if file_name := incoming_d.get("incoming_voice_name"):
                path = Path(
                    str(os.path.join(config.incoming_file_path, file_name)),
                )
                if path.exists():
                    path.unlink()

            result = {
                "error": f"error_{config.service_name}",
                "message": ex.message, "code": ex.code,
            }
            logger.error(f"[!] SearchEngineError: {ex}")

        await default_exchange.publish(
            Message(
                body=json.dumps(result, ensure_ascii=False).encode(),
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
        )

        if not result.get("error"):
            logger.info(
                f"[*] Sent reply, file_path={result.get('output_voice_path')},"
                f" time_execution: {time.perf_counter() - start_t:.4f} sec."
            )


async def main() -> None:
    """
    Точка входа в запуск RMQ-rpc сервер.

    @rtype:
    @return:
    """
    connection = await connect_robust(config.get_rabbitmq_url())
    channel = await connection.channel()

    default_exchange: AbstractExchange = channel.default_exchange

    async def wrapped_on_message(message):
        await on_message(message, default_exchange)

    queue = await channel.declare_queue(config.declare_queue_name)
    await queue.consume(wrapped_on_message)

    logger.info("[*] Awaiting RPC requests...")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
