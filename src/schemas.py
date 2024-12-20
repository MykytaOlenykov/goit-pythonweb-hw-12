from datetime import datetime, date

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, EmailStr, model_validator


class ContactModel(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=255)
    phone: str = Field(min_length=3, max_length=50)
    birthday: date

    @model_validator(mode="before")
    def validate_birthday(cls, values):
        value = values.get("birthday")

        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Expected YYYY-MM-DD.")

        return values


class ResponseContactModel(BaseModel):
    id: int = Field(examples=[1])
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
