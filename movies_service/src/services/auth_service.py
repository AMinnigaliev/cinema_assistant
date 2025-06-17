import asyncio
import json
import logging
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from src.core.config import settings
from src.core.exceptions import CacheServiceError
from src.db.redis_client import get_redis_cache
from src.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, redis_client: CacheService):
        self.redis_client = redis_client

    @staticmethod
    async def verify_token_through_auth(token: str, request_id: str) -> dict:
        """Проверяет токен через auth-сервис."""
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Request-Id": request_id,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.auth_service_url}/validate",
                    headers=headers,
                    timeout=1.0,
                )
                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Ошибка при проверки токена через auth-сервис: %s "
                    "token=%s ",
                    e, token
                )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail="Unauthorized or invalid token"
                )

            except httpx.RequestError:
                logger.error(
                    "Auth-сервис недоступен для проверки токена %s ", token
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth service unavailable"
                )

        payload = response.json()
        return payload

    @staticmethod
    async def varify_token_locally(token: str) -> dict:
        """Проверяет токен локально, без обращения к другим сервисам."""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            # Список обязательных полей, которые должен содержать токен
            required_fields = ["user_id", "role", "exp"]

            for field in required_fields:
                if field not in payload:
                    raise JWTError

            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    async def varify_token_with_cache(
            self, token: str, request_id: str
    ) -> dict:
        """
        Проверяет токен с использованием кеша через auth-сервис или локально
        (если не получается через auth-сервис).
        """
        cache_key = f"token:{token}"

        message = f"Проверяем наличие токена в кеше: key={cache_key}"
        logger.info(message)

        try:
            if cached := await self.redis_client.get(cache_key, message):
                logger.info(
                    "Токен найден в кеше: key=%s value=%s", cache_key, cached
                )
                try:
                    return json.loads(cached)

                except json.JSONDecodeError as e:
                    logger.error(
                        "Ошибка декодирования значения из кеша для токена: %s "
                        "key=%s value=%s",
                        e, cache_key, cached
                    )
        except CacheServiceError:
            pass

        try:
            payload = await self.verify_token_through_auth(token, request_id)

        except HTTPException:
            payload = await self.varify_token_locally(token)
            expire = settings.cache_expire_in_seconds

        else:
            exp = payload.get("exp")
            ttl = int(int(exp) - datetime.now(UTC).timestamp())
            expire = ttl if ttl > 1 else None

        if expire:
            asyncio.create_task(self.redis_client.set(
                cache_key, json.dumps(payload),
                expire=expire,
            ))
        return payload


@lru_cache()
def get_auth_service(
    redis: Annotated[CacheService, Depends(get_redis_cache)],
) -> AuthService:
    """
    Провайдер для получения экземпляра AuthService.

    Функция создаёт синглтон экземпляр AuthService, используя Redis,
    который передаётся через Depends (зависимости FastAPI).

    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :return: Экземпляр AuthService, который используется для
    проверки токена.
    """
    logger.info(
        "Создаётся экземпляр AuthService с использованием Redis."
    )
    return AuthService(redis)
