import logging

from redis.asyncio import Redis

from src.core.config import settings
from src.core.exceptions import CacheServiceError

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get(self, key: str, log_info: str = "") -> bytes | None:
        logger.debug(
            "Попытка получить значение из кеша: key=%s. %s", key, log_info
        )
        try:
            value = await self.redis_client.get(key)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при получении значения из кеша: key=%s, error=%s. %s",
                key, e, log_info
            )
            raise CacheServiceError(e)

        else:
            if value is not None:
                logger.info(
                    "Ключ найден в кеше: key=%s. %s",
                    key, log_info
                )
                return value

            logger.info("Ключ отсутствует в кеше: key=%s. %s", key, log_info)

            return None

    async def set(
            self,
            key: str,
            value: bytes,
            expire: int = settings.cache_expire_in_seconds,
            log_info: str = "",
    ) -> None:
        logger.debug(
            "Попытка сохранить значение в кеш: "
            "key=%s, value=%s, expire=%d. %s",
            key, value, expire, log_info
        )
        try:
            await self.redis_client.set(key, value, ex=expire)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при сохранении значения в кеш:"
                " key=%s, expire=%s, error=%s. %s",
                key, expire, e, log_info
            )
            raise CacheServiceError(e)

        else:
            logger.info(
                "Значение успешно сохранено в кеше: key=%s, expire=%d. %s",
                key, expire, log_info
            )

    async def close(self) -> None:
        logger.info("Закрытие соединения с Redis по работе с кешом...")

        try:
            await self.redis_client.close()
            logger.info(
                "Соединение с Redis по работе с кешом успешно закрыто."
            )

        except (settings.redis_exceptions, RuntimeError) as e:
            logger.error(
                "Ошибка при закрытии соединения с Redis по работе с кешом: "
                "%s", e
            )
            raise CacheServiceError(e)
