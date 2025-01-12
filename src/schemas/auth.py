from pydantic import BaseModel


class ResponseSignupModel(BaseModel):
    message: str = "ok"
