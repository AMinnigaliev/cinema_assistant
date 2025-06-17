from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, jwt

from src.core.config import settings


def create_access_token(
    user_id: str | UUID,
    role: str,
    expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, Any] = {
        "user_id": str(user_id),
        "role": role,
        "exp": datetime.now(UTC) + (expires_delta or timedelta(
            minutes=settings.access_token_expire_minutes
        )),
    }
    return jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )


def create_refresh_token(
    user_id: str | UUID,
    role: str,
    expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, Any] = {
        "user_id": str(user_id),
        "role": role,
        "exp": datetime.now(UTC) + (expires_delta or timedelta(
            days=settings.refresh_token_expire_days
        )),
    }
    return jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )


def verify_token(token: str) -> dict:
    """Проверяет валидность JWT-токена."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    else:
        # Список обязательных полей, которые должен содержать токен
        required_fields = ["user_id", "role", "exp"]

        for field in required_fields:
            if field not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        return payload
