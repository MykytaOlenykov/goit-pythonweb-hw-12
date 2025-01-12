from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Token
from src.schemas.tokens import TokenCreateModel


class TokensRepository:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_one_or_none(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
    ):
        return (
            await self.db.execute(select(Token).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, body: TokenCreateModel):
        token = Token(**body.model_dump())
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def delete(self, token: Token):
        await self.db.delete(token)
        await self.db.commit()
        return token
