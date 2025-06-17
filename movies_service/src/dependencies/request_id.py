from fastapi import Header


async def get_request_id(
    x_request_id: str = Header(
        ..., description="Запрос идентификатора для отслеживания"
    )
) -> str:
    return x_request_id
