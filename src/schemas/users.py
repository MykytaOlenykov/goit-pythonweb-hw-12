from pydantic import BaseModel, Field, EmailStr

from src.database.models import UserStatus


class UserCreateModel(BaseModel):
    username: str = Field(max_length=100)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)


class UserStatusUpdateModel(BaseModel):
    status: UserStatus


class UserAvatarUpdateModel(BaseModel):
    avatar_url: str


class ChangePasswordModel(BaseModel):
    password: str = Field(min_length=8)


class ResponseAvatarModel(BaseModel):
    avatar_url: str
