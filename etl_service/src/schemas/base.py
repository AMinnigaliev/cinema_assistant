from uuid import UUID

from pydantic import BaseModel


class Base(BaseModel):
    id: UUID
