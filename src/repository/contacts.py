from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact


class ContactsRepository:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_all(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
        offset: int | None = None,
        limit: int | None = None,
    ):
        filters = filters or []

        query = select(Contact).filter(*filters).order_by(order_by)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        return (await self.db.execute(query)).scalars().all()

    async def get_one(self):
        pass

    async def create(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass
