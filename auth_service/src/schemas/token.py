from pydantic import BaseModel, Field


class Token(BaseModel):
    """Модель токена для аутентификации."""
    access_token: str = Field(..., description="Токен доступа")
    refresh_token: str = Field(..., description="Токен обновления")
    token_type: str = Field(default="bearer", description="Тип токена")
