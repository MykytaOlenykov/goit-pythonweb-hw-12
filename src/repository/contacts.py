from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactCreateModel


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

    async def get_one_or_none(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
    ):
        return (
            await self.db.execute(select(Contact).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, body: ContactCreateModel):
        contact = Contact(**body.model_dump())
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update(self, contact_id: int, body: ContactCreateModel):
        contact = await self.get_one_or_none(filters=[Contact.id == contact_id])

        if contact is None:
            return None

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact: Contact):
        await self.db.delete(contact)
        await self.db.commit()
        return contact
