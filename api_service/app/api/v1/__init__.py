from fastapi import APIRouter

from .auth import router as auth_router
from .voice import router as voice_router

router = APIRouter()
router.include_router(voice_router, prefix="/voice", tags=["voice"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
