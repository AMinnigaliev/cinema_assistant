from fastapi import Depends

from app.dependencies.token import get_token
from app.services.auth_service import AuthService, get_auth_service


async def get_current_user(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Делегирует проверку токена сервису авторизации.
    При валидном JWT возвращает payload (dict).
    При ошибке — 401.
    """
    payload = await auth_service.varify_token_with_cache(token, False)

    return payload
