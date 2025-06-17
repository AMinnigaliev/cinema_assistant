import logging
from datetime import UTC, datetime

from redis.asyncio import Redis

from src.core.config import settings
from src.core.exceptions import RedisUnavailable
from src.core.security import verify_token

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def check_value(
        self, token_key: str, value: bytes, log_info: str = ""
    ) -> bool:
        """Проверяет, соответствует ли значение токена заданному."""
        logger.debug(
            "Проверка токена в Redis: token_key=%s, check_value=%s. %s",
            token_key, value, log_info
        )
        try:
            redis_value = await self.redis_client.get(token_key)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при проверке токена в Redis: "
                "token_key=%s, check_value=%s, error=%s. %s",
                token_key, value, e, log_info
            )
            raise RedisUnavailable()

        if redis_value == value:
            logger.info(
                "Токен найден в списке '%s': token_key=%s. %s",
                value.decode(), token_key, log_info
            )
            return True

        logger.info(
            "Токен отсутствует в списке '%s': token_key=%s. %s",
            value.decode(), token_key, log_info
        )
        return False

    async def set(
        self, token_key: str, value: bytes, expire: int, log_info: str = ""
    ) -> None:
        """Добавляет токен в Redis с временем жизни."""
        logger.debug(
            "Добавление токена в Redis: token_key=%s, value=%s, expire=%d сек."
            " %s",
            token_key, value, expire, log_info
        )
        try:
            await self.redis_client.set(token_key, value, ex=expire)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при добавлении токена в Redis: "
                "token_key=%s, error=%s. %s",
                token_key, e, log_info
            )
            raise RedisUnavailable()

        logger.info(
            "Токен добавлен в Redis: token_key=%s, expire=%d сек. %s",
            token_key, expire, log_info
        )

    async def delete(self, token: str, log_info: str = "") -> None:
        """Удаляет токен из Redis."""
        logger.debug("Удаление токена: token=%s. %s", token, log_info)
        try:
            await self.redis_client.delete(token)

        except settings.redis_exceptions as e:
            logger.error(
                "Ошибка при удалении токена: token=%s, error=%s. %s",
                token, e, log_info
            )
            raise RedisUnavailable()

        logger.info("Токен удалён: token=%s. %s", token, log_info)

    async def revoke_token(self, token: str, log_info: str = "") -> None:
        """
        Отзыв токена: помещает его в Redis с TTL, равным
        оставшемуся времени жизни токена.
        """
        payload = verify_token(token)

        if exp := payload.get("exp"):
            ttl = int(int(exp) - datetime.now(UTC).timestamp())

            if ttl > 0:
                await self.set(token, settings.token_revoke, ttl, log_info)

    async def close(self):
        """Закрывает соединение с Redis."""
        logger.info("Закрытие соединения с Redis (auth-токены)...")
        try:
            await self.redis_client.close()
            logger.info("Соединение с Redis (auth) успешно закрыто.")

        except (settings.redis_exceptions, RuntimeError) as e:
            logger.error(
                "Ошибка при закрытии соединения с Redis (auth): %s", e
            )
