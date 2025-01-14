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


class ResponseVerifyModel(BaseModel):
    message: str
