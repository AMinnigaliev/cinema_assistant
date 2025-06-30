from fastapi import APIRouter, Depends

from .auth import router as auth_router
from .voice import router as voice_router
from ...dependencies import get_current_user

router = APIRouter()
router.include_router(
    voice_router,
    prefix="/voice",
    tags=["voice"],
    dependencies=[Depends(get_current_user)]
)
router.include_router(auth_router, prefix="/auth", tags=["auth"])
