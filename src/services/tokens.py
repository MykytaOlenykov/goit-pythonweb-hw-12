from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.tokens import TokensRepository
from src.database.models import Token, TokenType
from src.schemas.tokens import BaseTokenPayloadCreateModel, TokenCreateModel
from src.utils.exceptions import HTTPNotFoundException
from src.utils.tokens import create_jwt
from src.settings import settings


class TokensService:

    def __init__(self, db: AsyncSession):
        self.tokens_repository = TokensRepository(db)

    async def get_token_or_none(self, token: str):
        filters = [Token.token == token]
        return await self.tokens_repository.get_one_or_none(filters=filters)

    async def get_token_or_fail(self, token: str):
        token = await self.get_token_or_none(token)

        if token is None:
            raise HTTPNotFoundException("Token not found")

        return token

    async def create(self, body: TokenCreateModel):
        return await self.tokens_repository.create(body)

    async def delete_by_id(self, token: str):
        token = await self.get_token_or_fail(token)
        return await self.tokens_repository.delete(token)

    async def create_verification_token(self, payload: BaseTokenPayloadCreateModel):
        data = {
            **payload.model_dump(),
            "token_type": TokenType.VERIFICATION,
        }
        jwt = create_jwt(
            data=data,
            expire_time_seconds=settings.JWT_VERIFICATION_EXPIRATION_SECONDS,
        )
        body = TokenCreateModel(
            token=jwt,
            type=TokenType.VERIFICATION,
            user_id=payload.user_id,
        )
        return await self.create(body)
