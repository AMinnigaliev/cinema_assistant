from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.dependencies.request_id import get_request_id
from src.services.auth_service import AuthService, get_auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


def role_dependency(required_roles: tuple[str]):
    """
    Создаёт зависимость для проверки роли пользователя.

    Эта зависимость выполняет следующие проверки:
    1. Проверяет наличие токена в заголовках запроса.
    2. Получает payload токена через AuthService.
    3. Сравнивает роль пользователя с переданными допустимыми ролями.
    """
    async def _check_role(
        request_id: str = Depends(get_request_id),
        token: str = Security(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> dict:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        payload = await auth_service.varify_token_with_cache(token, request_id)
        if payload.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

        return payload

    return _check_role
