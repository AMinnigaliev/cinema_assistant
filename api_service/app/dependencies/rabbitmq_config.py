from app.core.config import settings


def get_rabbitmq_url() -> str:
    return (
        f"amqp://{settings.rabbitmq_user}:"
        f"{settings.rabbitmq_password}@"
        f"{settings.rabbitmq_host}:"
        f"{settings.rabbitmq_port}/"
    )
