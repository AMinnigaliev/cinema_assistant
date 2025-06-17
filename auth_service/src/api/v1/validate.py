from fastapi import APIRouter, Depends

from src.dependencies.auth import oauth2_scheme
from src.schemas.payload import PayloadResponse
from src.services.validate_service import ValidateService, get_validate_service

router = APIRouter()


@router.post(
    "",
    response_model=PayloadResponse,
    summary="Валидация токена пользователя",
    description="Валидация предоставленного токена пользователя. "
                "Возвращает payload токена."
)
async def validate_token(
    token: str = Depends(oauth2_scheme),
    validate_service: ValidateService = Depends(get_validate_service),
) -> PayloadResponse:
    """Валидация токена пользователя"""
    return await validate_service.validate_token(token)
