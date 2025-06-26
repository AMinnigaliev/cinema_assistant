from pydantic import BaseModel


class BaseUser(BaseModel):
    first_name: str
    last_name: str


class UserCreateRequest(BaseUser):
    login: str
    password: str


class UserResponse(BaseUser):
    id: str
    role: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserUpdateRequest(BaseUser):
    password: str


class UserLogoutRequest(BaseModel):
    refresh_token: str


class UserLogoutResponse(BaseModel):
    message: str = "Successfully logged out"


class UserHistoryResponse(BaseModel):
    user_id: str
    login_time: str
    user_agent: str
