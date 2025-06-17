import asyncio
import functools
from typing import TypeVar

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from core import config
from core.logger import logger
from interface.storage.base import BaseStorage

__all__ = [
    "RedisStorage_T",
    "RedisStorage",
    "backoff_async_storage",
    "check_free_size_storage",
]

RedisStorage_T = TypeVar("RedisStorage_T", bound="RedisStorage")


def backoff_async_storage(start_sleep_time=2, factor=2, border_sleep_time=20):
    def wrapper_storage(func):
        @functools.wraps(func)
        async def wrapped_storage(*args, **kwargs):
            execute_result, n, t = False, 1, start_sleep_time

            while not execute_result:
                try:
                    if asyncio.iscoroutinefunction(func):
                        result_ = await func(*args, **kwargs)

                    else:
                        result_ = func(*args, **kwargs)

                    execute_result = True

                    return result_
                except (RedisConnectionError, ConnectionError) as ex:
                    t = (
                        t * (factor ^ n)
                        if t < border_sleep_time else border_sleep_time
                    )
                    logger.error(f"Error connect to RedisStorage({t}): {ex}")
                    await asyncio.sleep(t)

        return wrapped_storage

    return wrapper_storage


def check_free_size_storage(
        start_sleep_time=2, factor=2, border_sleep_time=20, select_limit=100
):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            producer_, model_ = next(iter(args)), kwargs.get("model_")
            key_rule = producer_.get_key_of_rule(model_=model_)

            need_timeout, n, t = True, 1, start_sleep_time
            while need_timeout:
                gen_scan_iter_ = await producer_.redis_storage.scan_iter(
                    f"{key_rule}_*"
                )
                num_obj_in_stor = len(gen_scan_iter_)

                if num_obj_in_stor >= select_limit:
                    t = (
                        t * (factor ^ n)
                        if t < border_sleep_time else border_sleep_time
                    )
                    msg = (
                        f"Store contains the maximum of unfinished proc "
                        f"({num_obj_in_stor}), recheck after {t} sec."
                    )
                    logger.warning(msg)
                    await asyncio.sleep(t)

                else:
                    need_timeout = False

            return await func(*args, **kwargs)

        return wrapped

    return wrapper


class RedisStorage(BaseStorage):
    """Storage с использованием Redis."""

    def __init__(self, redis_: Redis):
        self._redis = redis_

    @backoff_async_storage()
    async def save_state(self, key_: str, value: str) -> None:
        await self._redis.set(name=key_, value=value)

    @backoff_async_storage()
    async def retrieve_state(self, key_: str) -> str:
        return await self._redis.get(key_)

    @backoff_async_storage()
    async def get_(self, name: str) -> str:
        res_ = await self._redis.get(name=name)
        return res_

    @backoff_async_storage()
    async def set_(self, name: str, value: str | float) -> None:
        await self._redis.set(name=name, value=value)

    @backoff_async_storage()
    async def scan_iter(self, match) -> list:
        return [i async for i in self._redis.scan_iter(match)]

    @backoff_async_storage()
    async def delete_(self, name: str = None, names: list[str] = None) -> None:
        if name:
            await self._redis.delete(name)

        if names:
            await self._redis.delete(*names)

    async def close_(self) -> None:
        await self._redis.close()
