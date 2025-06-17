import logging
from contextlib import asynccontextmanager

from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from src.core.config import settings
from src.core.exceptions import RedisUnavailable
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)

redis_auth: AuthService | None = None


async def get_redis_auth() -> AuthService:
    """
    Возвращает экземпляр AuthService, обеспечивающий работу с Redis для
    аутентификации.
    """
    global redis_auth

    try:
        if not redis_auth or not await redis_auth.redis_client.ping():
            logger.info("Создание клиента Redis для auth...")

            redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=0,
            )
            if not await redis_client.ping():
                raise ConnectionError("Redis недоступен!")

            redis_auth = AuthService(redis_client)

            logger.info("Клиент Redis для auth успешно создан.")

    except settings.redis_exceptions as e:
        logger.error(f"Ошибка при создании клиента Redis для auth: {e}")
        raise RedisUnavailable()

    return redis_auth


@asynccontextmanager
async def redis_client_by_rate_limit():
    """
    Асинхронный контекстный менеджер Redis для RateLimit.

    @rtype: AsyncGenerator[Redis | None | Redis[bytes], Any]
    @return: redis_client
    """
    redis_client = Redis.from_url(url=settings.redis_rate_limit_url)

    try:
        if not await redis_client.ping():
            raise ConnectionError("Redis недоступен!")

        yield redis_client

    finally:
        await redis_client.close()
