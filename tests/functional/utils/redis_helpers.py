from redis import Redis

from settings import config


def make_redis_client() -> Redis:
    """
    Клиент Redis для тестов и утилит.
    """
    return Redis(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
        db=config.redis_db,
    )
