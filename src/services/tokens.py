from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.tokens import TokensRepository
from src.database.models import Token, TokenType
from src.schemas.tokens import BaseTokenPayloadCreateModel, TokenCreateModel
from src.utils.exceptions import HTTPNotFoundException
from src.utils.tokens import create_jwt
from src.settings import settings


class TokensService:
    """
    TokensService manages the creation, retrieval, and deletion of tokens.

    Args:
        - db: AsyncSession - The database session to perform CRUD operations.

    Methods:
        - get_tokens: Retrieves tokens based on filters.
        - get_token_or_none: Retrieves a single token if it exists.
        - get_token_or_fail: Retrieves a single token, raises HTTPNotFoundException if not found.
        - create: Creates a new token.
        - delete_token: Deletes a token by its string value.
        - delete_many_tokens: Deletes multiple tokens by their string values.
        - create_verification_token: Creates a verification token.
        - create_refresh_token: Creates a refresh token.
        - generate_access_token: Generates an access token.
    """

    def __init__(self, db: AsyncSession):
        self.tokens_repository = TokensRepository(db)

    async def get_tokens(
        self,
        user_id: int | None = None,
        type: TokenType | None = None,
    ):
        """
        Retrieves tokens based on optional filters.

        Args:
            - user_id: int | None - Optional user ID to filter tokens by.
            - type: TokenType | None - Optional type to filter tokens by.

        Returns:
            - List[Token] - A list of tokens matching the filters.
        """

        filters = []

        if user_id:
            filters.append(Token.user_id == user_id)

        if type:
            filters.append(Token.type == type)

        return await self.tokens_repository.get_all(filters=filters)

    async def get_token_or_none(self, token: str):
        """
        Retrieves a single token if it exists.

        Args:
            - token: str - The token string to retrieve.

        Returns:
            - Token | None - The token if found, otherwise None.
        """

        filters = [Token.token == token]
        return await self.tokens_repository.get_one_or_none(filters=filters)

    async def get_token_or_fail(self, token: str):
        """
        Retrieves a single token, raises HTTPNotFoundException if not found.

        Args:
            - token: str - The token string to retrieve.

        Returns:
            - Token - The token if found.

        Raises:
            - HTTPNotFoundException - If the token is not found.
        """

        token = await self.get_token_or_none(token)

        if token is None:
            raise HTTPNotFoundException("Token not found")

        return token

    async def create(self, body: TokenCreateModel):
        """
        Creates a new token.

        Args:
            - body: TokenCreateModel - The data for creating a token.

        Returns:
            - Token - The created token.
        """

        return await self.tokens_repository.create(body)

    async def delete_token(self, token: str):
        """
        Deletes a token by its string value.

        Args:
            - token: str - The token string to delete.

        Returns:
            - bool - True if token was deleted successfully.

        Raises:
            - HTTPNotFoundException - If the token is not found.
        """

        token = await self.get_token_or_fail(token)
        return await self.tokens_repository.delete(token)

    async def delete_many_tokens(self, tokens: List[str]):
        """
        Deletes multiple tokens by their string values.

        Args:
            - tokens: List[str] - List of token strings to delete.

        Returns:
            - bool - True if tokens were deleted successfully.
        """

        await self.tokens_repository.delete_many(tokens)

    async def create_verification_token(self, payload: BaseTokenPayloadCreateModel):
        """
        Creates a verification token.

        Args:
            - payload: BaseTokenPayloadCreateModel - The payload data for the verification token.

        Returns:
            - Token - The created verification token.
        """

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

    async def create_refresh_token(self, payload: BaseTokenPayloadCreateModel):
        """
        Creates a refresh token.

        Args:
            - payload: BaseTokenPayloadCreateModel - The payload data for the refresh token.

        Returns:
            - Token - The created refresh token.
        """

        data = {
            **payload.model_dump(),
            "token_type": TokenType.REFRESH,
        }
        jwt = create_jwt(
            data=data,
            expire_time_seconds=settings.JWT_REFRESH_EXPIRATION_SECONDS,
        )
        body = TokenCreateModel(
            token=jwt,
            type=TokenType.REFRESH,
            user_id=payload.user_id,
        )
        return await self.create(body)

    def generate_access_token(self, payload: BaseTokenPayloadCreateModel):
        """
        Generates an access token.

        Args:
            - payload: BaseTokenPayloadCreateModel - The payload data for the access token.

        Returns:
            - str - The generated access token.
        """

        data = {
            **payload.model_dump(),
            "token_type": TokenType.ACCESS,
        }
        return create_jwt(
            data=data,
            expire_time_seconds=settings.JWT_ACCESS_EXPIRATION_SECONDS,
        )
