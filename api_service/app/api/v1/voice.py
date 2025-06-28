from uuid import uuid4
from pathlib import Path
from datetime import datetime

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    Depends,
    HTTPException,
)

from app.dependencies.auth import get_current_user
from app.services.voice import send_to_voice_service
from app.core.config import settings

router = APIRouter()


@router.post("/request", summary="Отправить аудио на распознавание")
async def handle_request(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    user=Depends(get_current_user),
):
    if audio.content_type not in ("audio/wav", "audio/x-wav", "audio/mpeg"):
        raise HTTPException(status_code=415, detail="Unsupported audio format")

    req_id = str(uuid4())
    iso_ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    dst_path: Path = settings.incoming_file_path / f"in_{req_id}_{iso_ts}.wav"
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    dst_path.write_bytes(await audio.read())

    background_tasks.add_task(send_to_voice_service, dst_path, req_id, user_id)
    return {"request_id": req_id, "status": "processing"}
