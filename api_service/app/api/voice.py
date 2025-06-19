from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from pathlib import Path
from app.services.voice import send_to_voice_service
from app.core.config import settings

router = APIRouter()

@router.post("/request")
async def handle_audio_request(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    language: str = Form("ru-RU"),
):
    request_id = str(uuid4())
    input_path = Path(settings.MEDIA_ROOT) / f"{request_id}_input.wav"
    with open(input_path, "wb") as f:
        f.write(await audio.read())
    try:
        await send_to_voice_service(input_path, request_id, user_id, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"request_id": request_id, "status": "processing"}

@router.post("/response")
async def handle_voice_response(
    request_id: str = Form(...),
    response_audio: UploadFile = File(...)
):
    output_path = Path(settings.MEDIA_ROOT) / f"{request_id}_response.wav"
    with open(output_path, "wb") as f:
        f.write(await response_audio.read())
    return {"status": "received"}

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    file_path = Path(settings.MEDIA_ROOT) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="audio/wav", filename=filename)
