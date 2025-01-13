from pydantic import BaseModel


class ResponseSignupModel(BaseModel):
    message: str


class ResponseVerifyModel(BaseModel):
    message: str
