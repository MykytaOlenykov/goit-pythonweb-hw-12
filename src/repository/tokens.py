from typing import List, Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Token
from src.schemas.tokens import TokenCreateModel


class TokensRepository:
    """
    TokensRepository is responsible for interacting with the Token database model.
    It provides methods to perform CRUD operations and batch deletions for tokens.

    Args:
        - session: AsyncSession - The database session for executing queries.

    Methods:
        - get_all: Fetches all tokens based on filters, ordering, and pagination options.
        - get_one_or_none: Fetches a single token matching the provided filters or returns None.
        - create: Creates a new token in the database.
        - delete: Deletes a specific token object.
        - delete_many: Deletes multiple tokens based on a list of token strings.
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_all(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
        offset: int | None = None,
        limit: int | None = None,
    ):
        """
        Fetches all tokens based on provided filters, ordering, and pagination options.

        Args:
            - filters: List[Any] | None - SQLAlchemy filter conditions (default: None).
            - order_by: Any - Field to order by (default: "id").
            - offset: int | None - Offset for pagination (default: None).
            - limit: int | None - Limit for pagination (default: None).

        Returns:
            - List[Token] - A list of tokens matching the criteria.
        """

        filters = filters or []

        query = select(Token).filter(*filters).order_by(order_by)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        return (await self.db.execute(query)).scalars().all()

    async def get_one_or_none(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
    ):
        """
        Fetches a single token matching the provided filters, or returns None if not found.

        Args:
            - filters: List[Any] | None - SQLAlchemy filter conditions (default: None).
            - order_by: Any - Field to order by (default: "id").

        Returns:
            - Token | None - A token object if found, otherwise None.
        """

        return (
            await self.db.execute(select(Token).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, body: TokenCreateModel):
        """
        Creates a new token in the database.

        Args:
            - body: TokenCreateModel - The data for the new token.

        Returns:
            - Token - The created token object.
        """

        token = Token(**body.model_dump())
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def delete(self, token: Token):
        """
        Deletes a specific token object from the database.

        Args:
            - token: Token - The token object to delete.

        Returns:
            - Token - The deleted token object.
        """

        await self.db.delete(token)
        await self.db.commit()
        return token

    async def delete_many(self, tokens: list[str]):
        """
        Deletes multiple tokens based on a list of token strings.

        Args:
            - tokens: list[str] - A list of token strings to delete.

        Returns:
            - int - The number of rows affected (i.e., deleted tokens).
        """

        stmt = delete(Token).where(Token.token.in_(tokens))
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
