import os

import httpx
from fastapi import Depends, Header, HTTPException, status

AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")


async def get_current_user(
    authorization: str = Header(..., description="Bearer <JWT>"),
    client: httpx.AsyncClient = Depends(httpx.AsyncClient),
):
    """
    Делегирует проверку токена сервису авторизации.
    При валидном JWT возвращает payload (dict).
    При ошибке — 401.
    """
    try:
        resp = await client.get(
            f"{AUTH_URL}/internal/verify",
            headers={"Authorization": authorization},
            timeout=3,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"auth_service unreachable: {exc}",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return resp.json()
