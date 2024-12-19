from datetime import date

from pydantic import BaseModel, Field


class ResponseContactModel(BaseModel):
    id: int = Field(examples=[1])
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
