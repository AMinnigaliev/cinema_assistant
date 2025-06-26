import asyncio

from elasticsearch.exceptions import ConnectionError as ESConnectionError

from logger import logger
from settings import config
from utils.es_helpers import make_async_es_client


async def wait_for_es() -> None:
    client = make_async_es_client()
    attempt = 0

    while attempt < config.max_connection_attempt:
        try:
            if await client.ping():
                await client.close()
                logger.debug("Connection to Elasticsearch has been made")
                return

            await asyncio.sleep(config.break_time_sec)
            attempt += 1

        except (ESConnectionError, ConnectionError) as ex:
            logger.error(f"Elasticsearch is not yet available. Error: {ex}")
            attempt += 1
            await asyncio.sleep(config.break_time_sec)

    await client.close()
    raise ConnectionError("number of connection attempts exceeded")


if __name__ == "__main__":
    try:
        asyncio.run(wait_for_es())

    except Exception as e:
        logger.error(f"Failed waiting for ES: {e}")
        raise
