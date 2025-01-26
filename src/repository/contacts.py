from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas.contacts import ContactCreateModel, ContactUpdateModel


class ContactsRepository:
    """
    ContactsRepository is responsible for interacting with the Contact database model.
    It provides methods to perform CRUD operations on the Contact table.

    Args:
        - session: AsyncSession - The database session for executing queries.

    Methods:
        - get_all: Fetches all contacts based on filters, ordering, and pagination options.
        - get_one_or_none: Fetches a single contact matching the provided filters or returns None.
        - create: Creates a new contact associated with a user.
        - update: Updates an existing contact by its ID.
        - delete: Deletes a given contact.
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
        Fetches all contacts based on provided filters, ordering, and pagination options.

        Args:
            - filters: List[Any] | None - SQLAlchemy filter conditions (default: None).
            - order_by: Any - Field to order by (default: "id").
            - offset: int | None - Offset for pagination (default: None).
            - limit: int | None - Limit for pagination (default: None).

        Returns:
            - List[Contact] - A list of contacts matching the criteria.
        """

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
        """
        Fetches a single contact matching the provided filters, or returns None if not found.

        Args:
            - filters: List[Any] | None - SQLAlchemy filter conditions (default: None).
            - order_by: Any - Field to order by (default: "id").

        Returns:
            - Contact | None - A contact object if found, otherwise None.
        """

        return (
            await self.db.execute(select(Contact).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, user_id: int, body: ContactCreateModel):
        """
        Creates a new contact for a specific user.

        Args:
            - user_id: int - The ID of the user to associate the contact with.
            - body: ContactCreateModel - The data for the new contact.

        Returns:
            - Contact - The created contact object.
        """

        contact = Contact(**body.model_dump(), user_id=user_id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update(self, contact_id: int, body: ContactUpdateModel):
        """
        Updates an existing contact by its ID.

        Args:
            - contact_id: int - The ID of the contact to update.
            - body: ContactCreateModel - The updated data for the contact.

        Returns:
            - Contact | None - The updated contact object if found, otherwise None.
        """

        contact = await self.get_one_or_none(filters=[Contact.id == contact_id])

        if contact is None:
            return None

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact: Contact):
        """
        Deletes a given contact from the database.

        Args:
            - contact: Contact - The contact object to delete.

        Returns:
            - Contact - The deleted contact object.
        """

        await self.db.delete(contact)
        await self.db.commit()
        return contact
