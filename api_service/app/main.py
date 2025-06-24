from fastapi import FastAPI
from app.api.v1.voice import router as voice_router
from app.services.rabbitmq import start_response_consumer

app = FastAPI()
app.include_router(voice_router, prefix="/api")
@app.on_event("startup")
async def on_start():
    await start_response_consumer()
