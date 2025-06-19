from fastapi import APIRouter, Depends, HTTPException, Header
from app.services.auth import verify_token

router = APIRouter()

@router.get("/check")
async def check_token(authorization: str = Header(...)):
    user = await verify_token(authorization)
    return {"user_id": user["user_id"], "role": user["role"]}
