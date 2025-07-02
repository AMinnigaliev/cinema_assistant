import asyncio
import logging.config

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import settings
from app.core.logger import LOGGING
from app.services.cache_service import CacheService

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

redis_cache: CacheService | None = None


async def init_redis_cache(
    retries: int = 3, delay: float = 2.0
) -> CacheService:
    """
    Создаёт и возвращает CacheService с внутренним Redis-клиентом.
    Выполняет до `retries` попыток подключения с интервалом `delay` секунд.
    """
    global redis_cache

    for attempt in range(1, retries + 1):
        try:
            logger.info(
                "Попытка %d/%d: подключаемся к Redis на %s:%d …",
                attempt, retries, settings.redis_host, settings.redis_port
            )
            client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
            )

            if not await client.ping():
                raise RedisConnectionError("Ping вернул False")

            redis_cache = CacheService(client)
            logger.info("Успешно подключились к Redis.")

            return redis_cache

        except (RedisConnectionError, OSError) as e:
            logger.error(
                "Ошибка подключения к Redis (попытка %d/%d): %s",
                attempt, retries, e
            )
            if attempt < retries:
                logger.info("Ждём %.1f с перед повторной попыткой…", delay)
                await asyncio.sleep(delay)

            else:
                logger.critical(
                    "Не удалось подключиться к Redis после %d попыток.",
                    retries
                )
                raise

    raise RuntimeError("Redis cache client не инициализирован")


async def get_redis_cache() -> CacheService:
    """
    Возвращает готовый CacheService. Если клиент ещё не создан или
    «умер» (ping упал), пересоздаёт его через init_redis_cache.
    """
    global redis_cache

    if redis_cache is not None:
        try:
            if await redis_cache.redis_client.ping():
                return redis_cache

            else:
                raise RedisConnectionError("Ping вернул False")

        except (RedisConnectionError, OSError) as e:
            logger.warning("Существующий Redis client упал: %s", e)
            redis_cache = None

    # Попытка установить новое соединение
    return await init_redis_cache()
