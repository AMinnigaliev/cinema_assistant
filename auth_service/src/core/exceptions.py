from fastapi import HTTPException, status


class RedisUnavailable(HTTPException):
    """
    Исключение, поднимаемое, при ошибке обращения к Redis.

    Возвращает HTTP 503 Service_Unavailable с сообщением
    "Service temporarily unavailable. Please try again later.".
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Service temporarily unavailable. Please try again later."
            )
        )


class TokenRevokedException(HTTPException):
    """
    Исключение, поднимаемое, когда токен отозван.

    Возвращает HTTP 401 Unauthorized с сообщением "Token has been revoked".
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
