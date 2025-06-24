from uuid import uuid4
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException

from app.services.voice import send_to_voice_service
from app.core.config import settings

router = APIRouter()

@router.post("/request")
async def handle_audio_request(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: str = Form(...),
):
    request_id = str(uuid4())
    iso = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    dst = settings.INCOMING_FILE_PATH / f"in_{request_id}_{iso}.wav"

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        dst.write_bytes(await audio.read())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    background_tasks.add_task(send_to_voice_service, dst, request_id, user_id)
    return {"request_id": request_id, "status": "processing"}
