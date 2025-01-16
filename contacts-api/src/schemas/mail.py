from pydantic import BaseModel


class VerificationMail(BaseModel):
    username: str
    email: str
    verification_url: str
