from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from limits import parse
from limits.storage import RedisStorage
from limits.strategies import FixedWindowRateLimiter
from redis.asyncio.client import Pipeline
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)

from src.core.config import settings
from src.db.redis_client import redis_client_by_rate_limit

__all__ = ["RateLimitMiddleware", "AsyncRateLimitMiddleware"]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    RateLimit с использованием limits. Синхронный, реализует стратегию
    ограничения с фиксированным окном.
    """

    def __init__(self, app) -> None:
        super().__init__(app=app)
        self._rate_limit = parse(settings.rate_limit)
        self._strategy = FixedWindowRateLimiter(
            storage=RedisStorage(uri=settings.redis_rate_limit_url)
        )

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | None:
        client_id = request.client.host

        if not self._strategy.test(self._rate_limit, client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "TOO MANY REQUESTS"}
            )

        self._strategy.hit(self._rate_limit, client_id)

        return await call_next(request)


class AsyncRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Кастомный RateLimit. Асинхронный, реализует стратегию ограничения с
    фиксированным окном.
    """

    def __init__(self, app) -> None:
        super().__init__(app=app)
        self._limit = settings.rate_limit
        self._window_sec = settings.rate_limit_window
        self._key_template = "ratelimit:{client_id}"

        self.__def_counter = 0

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | None:
        client_id = request.headers.get("X-Forwarded-For", request.client.host)
        key_ = self._key_template.format(client_id=client_id)

        async with redis_client_by_rate_limit() as rm_redis_client:
            current_count = await rm_redis_client.get(name=key_)
            current_count = int(
                current_count
            ) if current_count else self.__def_counter

            if current_count > self._limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "TOO MANY REQUESTS"}
                )

            pipe: Pipeline = await rm_redis_client.pipeline()
            pipe.incr(name=key_)
            pipe.expire(name=key_, time=self._window_sec)
            await pipe.execute()

        return await call_next(request)
