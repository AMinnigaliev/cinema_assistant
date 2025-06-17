from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.core.security import verify_token
from src.db.redis_client import get_redis_auth
from src.models.user import UserRoleEnum
from src.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


def role_dependency(required_roles: tuple[UserRoleEnum]):
    """
    Создаёт зависимость для проверки роли пользователя.

    Эта зависимость выполняет следующие проверки:
    1. Проверяет наличие токена в заголовках запроса.
    2. Расшифровывает токен и получает его payload.
    3. Проверяет, был ли токен отозван (сохраняется в Redis).
    4. Сравнивает роль пользователя с переданными допустимыми ролями.
    """
    async def _check_role(
        token: str = Security(oauth2_scheme),
        redis_client: AuthService = Depends(get_redis_auth)
    ):
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        payload = verify_token(token)
        if await redis_client.check_value(token, settings.token_revoke):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or revoked",
            )

        if payload.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

    return _check_role
