from pydantic import BaseModel, EmailStr


class VerificationMail(BaseModel):
    username: str
    email: EmailStr
    verification_url: str


class ResetPasswordMail(BaseModel):
    username: str
    email: EmailStr
    reset_token: str
