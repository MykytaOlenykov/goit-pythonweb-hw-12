from pydantic import BaseModel

from src.database.models import TokenType


class TokenCreateModel(BaseModel):
    type: TokenType
    token: str
    user_id: int


class BaseTokenPayloadCreateModel(BaseModel):
    user_id: int


class BaseTokenPayloadModel(BaseModel):
    token_type: TokenType
    user_id: int
