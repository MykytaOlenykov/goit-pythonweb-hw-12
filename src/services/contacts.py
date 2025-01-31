from datetime import date, timedelta

from sqlalchemy import or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactsRepository
from src.database.models import Contact
from src.schemas.users import UserBaseModel
from src.schemas.contacts import ContactCreateModel, ContactUpdateModel
from src.utils.exceptions import HTTPNotFoundException


class ContactsService:
    """
    ContactsService provides functionalities to manage user contacts.

    Args:
        - db: AsyncSession instance for database interaction.

    Methods:
        - get_all: Retrieves all contacts for a user with optional search and filtering.
        - get_by_id: Retrieves a specific contact by ID and user.
        - create: Creates a new contact for the user.
        - update_by_id: Updates an existing contact by ID.
        - delete_by_id: Deletes a contact by ID.
    """

    def __init__(self, db: AsyncSession):
        self.contacts_repository = ContactsRepository(db)

    async def get_all(
        self,
        user: UserBaseModel,
        search: str | None = None,
        birthdays_within: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ):
        """
        Retrieves all contacts for a specific user with optional search and filtering by name or email,
        and filtering by upcoming birthdays.

        Args:
            - user: UserBaseModel - The user whose contacts need to be fetched.
            - search: str | None - Optional search string for filtering contacts by name or email.
            - birthdays_within: int | None - Optional number of days to filter contacts by upcoming birthdays.
            - offset: int | None - Optional offset for pagination.
            - limit: int | None - Optional limit for pagination.

        Returns:
            - List of Contact objects that match the search and filter criteria.
        """

        filters = [Contact.user_id == user.id]

        if search is not None:
            filters.append(
                or_(
                    Contact.first_name.like(f"%{search}%"),
                    Contact.last_name.like(f"%{search}%"),
                    Contact.email.like(f"%{search}%"),
                )
            )

        if birthdays_within is not None:
            today = date.today()
            current_year = today.year

            birthday_month = func.extract("month", Contact.birthday)
            birthday_day = func.extract("day", Contact.birthday)
            birthday_this_year = func.date(
                func.concat(current_year, "-", birthday_month, "-", birthday_day)
            )

            end_date = today + timedelta(days=birthdays_within)
            filters.append(birthday_this_year.between(today, end_date))

        return await self.contacts_repository.get_all(
            filters=filters,
            offset=offset,
            limit=limit,
        )

    async def get_by_id(self, user: UserBaseModel, id: int):
        """
        Retrieves a contact by its ID and associated user.

        Args:
            - user: UserBaseModel - The user to whom the contact belongs.
            - id: int - The ID of the contact.

        Returns:
            - Contact object if found.

        Raises:
            - HTTPNotFoundException: If the contact with the specified ID is not found.
        """

        filters = [Contact.id == id, Contact.user_id == user.id]
        contact = await self.contacts_repository.get_one_or_none(filters=filters)

        if contact is None:
            raise HTTPNotFoundException("Contact not found")

        return contact

    async def create(self, user: UserBaseModel, body: ContactCreateModel):
        """
        Creates a new contact for the specified user.

        Args:
            - user: UserBaseModel - The user to whom the contact will be added.
            - body: ContactCreateModel - Contains information for the new contact.

        Returns:
            - Created Contact object.
        """

        return await self.contacts_repository.create(user_id=user.id, body=body)

    async def update_by_id(
        self,
        user: UserBaseModel,
        body: ContactUpdateModel,
        id: int,
    ):
        """
        Updates an existing contact identified by ID.

        Args:
            - user: UserBaseModel - The user to whom the contact belongs.
            - body: ContactUpdateModel - Contains updated information for the contact.
            - id: int - The ID of the contact to be updated.

        Returns:
            - Updated Contact object.

        Raises:
            - HTTPNotFoundException: If the contact with the specified ID is not found.
        """

        await self.get_by_id(user=user, id=id)
        return await self.contacts_repository.update(body=body, contact_id=id)

    async def delete_by_id(self, user: UserBaseModel, id: int):
        """
        Deletes a contact identified by ID for the specified user.

        Args:
            - user: UserBaseModel - The user to whom the contact belongs.
            - id: int - The ID of the contact to be deleted.

        Returns:
            - Boolean indicating successful deletion.

        Raises:
            - HTTPNotFoundException: If the contact with the specified ID is not found.
        """

        contact = await self.get_by_id(user=user, id=id)
        return await self.contacts_repository.delete(contact)
