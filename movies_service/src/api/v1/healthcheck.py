from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def root():
    return {"message": "Movies API is running"}
