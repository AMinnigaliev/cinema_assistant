from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from app.services.voice import send_to_voice_service
from app.core.config import settings

router = APIRouter()

@router.post("/request")
async def handle_request(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    user_id: str = Form(...),
):
    req_id = str(uuid4())
    iso = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    inp = settings.INCOMING_FILE_PATH / f"in_{req_id}_{iso}.wav"
    inp.parent.mkdir(parents=True, exist_ok=True)
    data = await audio.read()
    inp.write_bytes(data)
    background_tasks.add_task(send_to_voice_service, inp, req_id, user_id)
    return {"request_id": req_id, "status": "processing"}
