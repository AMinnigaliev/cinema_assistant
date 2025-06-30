from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (APIRouter, BackgroundTasks, File, Form,
                     HTTPException, status, UploadFile)
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services.clickhouse_client import get_voice_request
from app.services.voice import send_to_voice_service

router = APIRouter(prefix="/voice", tags=["voice"])


# ---------- POST /request ----------
@router.post(
    "/request",
    summary="Отправить аудио на распознавание (RabbitMQ → nlu_voice_service)",
    status_code=status.HTTP_202_ACCEPTED,
)
async def handle_request(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: str = Form(...),
):
    if audio.content_type not in ("audio/wav", "audio/x-wav"):
        raise HTTPException(415, "Unsupported audio format")

    req_id = str(uuid4())
    iso_ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    dst_path: Path = settings.incoming_file_path / f"in_{req_id}_{iso_ts}.wav"
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_bytes(await audio.read())

    # Публикация задачи в RabbitMQ + запись "queued" в ClickHouse
    background_tasks.add_task(send_to_voice_service, dst_path, req_id, user_id)

    return {"request_id": req_id, "status": "processing"}


# ---------- GET /response ----------
@router.get(
    "/response",
    summary="Статус и MP3 по request_id (читает ClickHouse)",
    response_class=FileResponse,
    responses={
        200: {"description": "MP3 готов или статус обработки"},
        404: {"description": "Не найдено"},
    },

)
async def get_response(request_id: str):
    record = await get_voice_request(request_id)
    if not record:
        raise HTTPException(404, "Request not found")

    if record.status != "done":
        # Пока идёт обработка
        return {"status": record.status}

    tts_path = settings.outgoing_file_path / record.tts_file_path
    if not tts_path.exists():
        raise HTTPException(404, "File not found on disk")

    return FileResponse(
        path=str(tts_path),
        media_type="audio/mpeg",
        filename=f"{request_id}.mp3",
    )
