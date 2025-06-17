import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.core.config import settings
from src.core.exceptions import TokenRevokedException
from src.core.security import verify_token
from src.db.redis_client import get_redis_auth
from src.schemas.payload import PayloadResponse
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ValidateService:
    """Сервис для валидации токена."""
    def __init__(self, redis_client: AuthService):
        self.redis_client = redis_client

    async def validate_token(self, token: str) -> PayloadResponse:
        """Проверить валидность токена."""
        if await self.redis_client.check_value(
            token, settings.token_revoke
        ):
            raise TokenRevokedException()

        payload = verify_token(token)
        return PayloadResponse(**payload)


@lru_cache()
def get_validate_service(
    redis: Annotated[AuthService, Depends(get_redis_auth)],
) -> ValidateService:
    """
    Провайдер для получения экземпляра ValidateService.

    Функция создаёт синглтон экземпляр ValidateService, используя Redis,
    который передаётся через Depends (зависимости FastAPI).

    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :return: Экземпляр ValidateService, который используется для
    валидации токена.
    """
    logger.info(
        "Создаётся экземпляр ValidateService с использованием Redis."
    )
    return ValidateService(redis)
