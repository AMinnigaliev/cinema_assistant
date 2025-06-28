from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/check", summary="Проверить токен")
async def check_token(user=Depends(get_current_user)):
    """
    Эхо-ендпойнт: возвращает payload пользователя.
    """
    return {"user": user}
