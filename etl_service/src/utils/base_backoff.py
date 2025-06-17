import asyncio
import functools

from core.logger import logger


def backoff_by_connection(
    exceptions: tuple, start_sleep_time=2, factor=2, border_sleep_time=20
):
    def wrapper_es(func):
        @functools.wraps(func)
        async def wrapped_es(*args, **kwargs):
            execute_result, n, t = False, 1, start_sleep_time

            while not execute_result:
                try:
                    if asyncio.iscoroutinefunction(func):
                        result_ = await func(*args, **kwargs)

                    else:
                        result_ = func(*args, **kwargs)

                    execute_result = True

                    return result_
                except exceptions as ex:
                    if t < border_sleep_time:
                        t = t * (factor ^ n)
                    else:
                        border_sleep_time
                    logger.error(f"Error connect({t}): {ex}")
                    await asyncio.sleep(start_sleep_time)

        return wrapped_es

    return wrapper_es
