from pydantic import BaseModel, Field, EmailStr


class LoginModel(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str


class VerifyModel(BaseModel):
    email: EmailStr = Field(max_length=255)


class ResponseSignupModel(BaseModel):
    message: str


class ResponseLoginModel(BaseModel):
    access_token: str
    token_type: str = Field(examples=["bearer"])


class ResponseRefreshModel(ResponseLoginModel):
    pass


class ResponseCurrentUserModel(BaseModel):
    id: int = Field(examples=[1])
    username: str
    email: EmailStr
    avatar_url: str | None


class ResponseVerifyModel(BaseModel):
    message: str
