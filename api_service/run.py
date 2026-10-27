import asyncio
import logging.config

import uvicorn
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.logger import LOGGING
from app.db.redis_client import init_redis_cache

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


async def main() -> int:
    try:
        await init_redis_cache()
    except RedisConnectionError:
        logger.critical(
            "Запуск отменён: Redis недоступен. "
            "Проверь состояние сервиса и настройки подключения."
        )
        return 1

    config = uvicorn.Config("app.main:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except KeyboardInterrupt:
        exit_code = 0

    raise SystemExit(exit_code)
