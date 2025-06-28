import asyncio
from fastapi import FastAPI

from app.api.v1.voice import router as voice_router
from app.services.rabbitmq import start_response_consumer

app = FastAPI(title="Cinema Assistant API")
app.include_router(voice_router)

@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(start_response_consumer())
