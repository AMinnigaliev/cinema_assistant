from fastapi import FastAPI
from app.api.routes import router as api_router
from app.services.rabbitmq import start_response_consumer

app = FastAPI(
    title="My API Service",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def on_startup() -> None:
    """Инициализируем подключения (RabbitMQ и т. д.)."""
    await start_response_consumer()
