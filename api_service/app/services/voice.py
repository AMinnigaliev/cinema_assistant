import httpx, json, time
from app.core.logger import logger
from uuid import UUID
from pathlib import Path
from app.core.config import settings

async def send_to_voice_service(audio_path: Path, request_id: str, user_id: str, language: str):
    metadata = {
        "request_id": request_id,
        "user_id": user_id,
        "language": language,
        "audio_format": {
            "codec": "pcm_s16le",
            "sample_rate": 16000,
            "channels": 1
        },
        "timestamp": int(time.time())
    }
    files = {
        "audio": (audio_path.name, open(audio_path, "rb"), "audio/wav"),
        "metadata": ("metadata.json", json.dumps(metadata), "application/json")
    }
    async with httpx.AsyncClient() as client:
        logger.info(f"Sending audio {audio_path.name} to voice_service")
        response = await client.post(settings.VOICE_SERVICE_URL, files=files)
        logger.info(f"Received response from voice_service: {response.status_code}")
        response.raise_for_status()
