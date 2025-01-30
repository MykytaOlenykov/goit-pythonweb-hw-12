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
        - delete_token: Deletes a token by its string value.
        - delete_many_tokens: Deletes multiple tokens by their string values.
        - create_token: Creates a token.
        - generate_token: Generates a token.
    """

    __TOKENS_EXPIRATIONS = {
        TokenType.REFRESH: settings.JWT_REFRESH_EXPIRATION_SECONDS,
        TokenType.ACCESS: settings.JWT_ACCESS_EXPIRATION_SECONDS,
        TokenType.VERIFICATION: settings.JWT_VERIFICATION_EXPIRATION_SECONDS,
        TokenType.RESET: settings.JWT_REFRESH_EXPIRATION_SECONDS,
    }

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

    def generate_token(
        self,
        token_type: TokenType,
        payload: BaseTokenPayloadCreateModel,
    ):
        """
        Generates a JWT token.

        Args:
            - token_type (TokenType): The type of token to generate (e.g., ACCESS, REFRESH, VERIFICATION, RESET).
            - payload (BaseTokenPayloadCreateModel): The payload data containing user-specific information.

        Returns:
            - str: The generated JWT token.
        """

        data = {
            **payload.model_dump(),
            "token_type": token_type,
        }
        return create_jwt(
            data=data,
            expire_time_seconds=self.__TOKENS_EXPIRATIONS[token_type],
        )

    async def create_token(
        self,
        token_type: TokenType,
        payload: BaseTokenPayloadCreateModel,
    ):
        """
        Creates and stores a new authentication token.

        Args:
            - token_type (TokenType): The type of token to create.
            - payload (BaseTokenPayloadCreateModel): The payload containing user-related data.

        Returns:
            - Token: The created token record from the database.
        """

        token = self.generate_token(token_type=token_type, payload=payload)
        body = TokenCreateModel(
            token=token,
            type=token_type,
            user_id=payload.user_id,
        )
        return await self.tokens_repository.create(body)
