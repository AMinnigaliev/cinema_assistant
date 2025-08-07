from fastapi import APIRouter

from .voice import router as voice_router

router = APIRouter()
router.include_router(
    voice_router,
    prefix="/voice",
    tags=["voice"],
)
