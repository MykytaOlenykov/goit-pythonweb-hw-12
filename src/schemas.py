from datetime import datetime, date

from typing import Any
from pydantic import BaseModel, Field, EmailStr, model_validator


def validate_birthday(value: Any):
    if isinstance(value, str):
        try:
            datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")


class ContactCreateModel(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=255)
    phone: str = Field(min_length=3, max_length=50)
    birthday: date

    @model_validator(mode="before")
    def validate_birthday(cls, values):
        value = values.get("birthday")
        validate_birthday(value)
        return values


class ContactUpdateModel(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, min_length=3, max_length=50)
    birthday: date | None = None

    @model_validator(mode="before")
    def check_not_none(cls, values):
        for field, value in values.items():
            if value is None:
                raise ValueError(f"{field} cannot be null if explicitly provided.")
        return values

    @model_validator(mode="before")
    def validate_birthday(cls, values):
        value = values.get("birthday")
        validate_birthday(value)
        return values


class ResponseContactModel(BaseModel):
    id: int = Field(examples=[1])
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
