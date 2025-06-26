import time

from redis.exceptions import ConnectionError as RedisConnectionError

from logger import logger
from settings import config
from utils.redis_helpers import make_redis_client


def wait_for_redis() -> None:
    """
    Ожидает доступности Redis, выполняя ping() и повторяя попытки
    пока не исчерпает max_connection_attempt. При успехе закрывает клиент,
    при провале кидает ConnectionError.
    """
    client = make_redis_client()
    attempt = 0

    while attempt < config.max_connection_attempt:
        try:
            if client.ping():
                client.close()
                logger.debug("Connection to Redis has been made")
                return

            # ждем перед следующей попыткой
            time.sleep(config.break_time_sec)
            attempt += 1

        except (RedisConnectionError, ConnectionError) as ex:
            logger.error(f"Redis is not yet available. Error: {ex}")
            attempt += 1
            time.sleep(config.break_time_sec)

    # если вышли из цикла без успеха
    client.close()
    raise ConnectionError("number of connection attempts exceeded")


if __name__ == "__main__":
    try:
        wait_for_redis()

    except Exception as e:
        logger.error(f"Failed waiting for Redis: {e}")
        raise
