from pydantic import BaseModel, Field


class ResponseSignupModel(BaseModel):
    message: str = "ok"
