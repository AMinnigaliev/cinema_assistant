from uuid import UUID

from pydantic import BaseModel, Field


class PayloadResponse(BaseModel):
    """Модель для представления payload токена."""
    user_id: UUID = Field(
        ..., description="Уникальный идентификатор пользователя"
    )
    role: str = Field(..., description="Роль пользователя")
    exp: int = Field(
        ..., description="Срок действия токена в секундах от эпохи"
    )

    model_config = {"from_attributes": True}
