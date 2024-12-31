from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactsRepository
from src.database.models import Contact
from src.schemas import ContactCreateModel, ContactUpdateModel


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

    async def get_by_id(self, id: int):
        filters = [Contact.id == id]
        contact = await self.contacts_repository.get_one_or_none(filters=filters)

        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )

        return contact

    async def create(self, body: ContactCreateModel):
        return await self.contacts_repository.create(body)

    async def update_by_id(self, body: ContactUpdateModel, id: int):
        await self.get_by_id(id)
        return await self.contacts_repository.update(body=body, contact_id=id)

    async def delete_by_id(self, id):
        contact = await self.get_by_id(id)
        return await self.contacts_repository.delete(contact)
