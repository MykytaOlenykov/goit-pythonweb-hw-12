from pydantic import BaseModel


class ActivationMail(BaseModel):
    username: str
    email: str
    activation_url: str
