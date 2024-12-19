from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactsRepository
from src.database.models import Contact


class ContactsService:
    def __init__(self, db: AsyncSession):
        self.contacts_repository = ContactsRepository(db)

    async def get_all(
        self,
        search: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ):
        filters = None

        if search is not None:
            filters = [
                or_(
                    Contact.first_name.like(f"%{search}%"),
                    Contact.last_name.like(f"%{search}%"),
                    Contact.email.like(f"%{search}%"),
                ),
            ]

        return await self.contacts_repository.get_all(
            filters=filters,
            offset=offset,
            limit=limit,
        )

    async def get_by_id(self):
        pass

    async def create(self):
        pass

    async def update_by_id(self):
        pass

    async def remove_by_id(self):
        pass
