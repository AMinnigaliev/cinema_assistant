from pydantic import BaseModel


class GetUserRoleResponse(BaseModel):
    role: str
