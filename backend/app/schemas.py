from pydantic import BaseModel, Field


class LoginBody(BaseModel):
    username: str
    password: str
    role: str


class RegisterBody(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class MeResponse(BaseModel):
    user: UserOut
