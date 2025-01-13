from pydantic import BaseModel


class VerifyModel(BaseModel):
    email: str


class ResponseSignupModel(BaseModel):
    message: str


class ResponseVerifyModel(BaseModel):
    message: str
