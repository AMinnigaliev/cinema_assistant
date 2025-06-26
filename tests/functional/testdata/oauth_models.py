from pydantic import BaseModel


class AuthHeaders(BaseModel):
    Authorization: str
    Content_Type: str = "application/json"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str
