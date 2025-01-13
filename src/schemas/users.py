from pydantic import BaseModel, Field

from src.database.models import UserStatus


class UserCreateModel(BaseModel):
    username: str = Field(max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)


class UserStatusUpdateModel(BaseModel):
    status: UserStatus
