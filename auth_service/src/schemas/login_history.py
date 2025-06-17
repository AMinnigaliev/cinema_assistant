from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LoginHistory(BaseModel):
    """Модель истории входов пользователя."""
    user_id: UUID = Field(
        ..., description="Уникальный идентификатор пользователя"
    )
    login_time: datetime = Field(..., description="Время входа пользователя")
    user_agent: str = Field(
        ..., description="Информация о браузере или устройстве пользователя"
    )

    model_config = {"from_attributes": True}
