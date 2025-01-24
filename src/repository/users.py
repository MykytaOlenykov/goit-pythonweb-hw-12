from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.database.models import User
from src.schemas.users import UserCreateModel


class UsersRepository:
    """
    UsersRepository provides methods to interact with the User database model.
    It includes operations for retrieving, creating, and updating user records.

    Args:
        - session: AsyncSession - The database session for executing queries.

    Methods:
        - get_one_or_none: Fetches a single user matching the provided filters or returns None.
        - create: Adds a new user to the database.
        - update: Updates an existing user's data in the database.
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_one_or_none(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
    ):
        """
        Fetches a single user matching the provided filters, or returns None if not found.

        Args:
            - filters: List[Any] | None - SQLAlchemy filter conditions (default: None).
            - order_by: Any - Field to order by (default: "id").

        Returns:
            - User | None - A user object if found, otherwise None.
        """

        return (
            await self.db.execute(select(User).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, body: UserCreateModel):
        """
        Creates a new user in the database.

        Args:
            - body: UserCreateModel - The data for the new user.

        Returns:
            - User - The created user object.
        """

        user = User(**body.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, body: BaseModel):
        """
        Updates an existing user's data in the database.

        Args:
            - user_id: int - The ID of the user to update.
            - body: BaseModel - A Pydantic model containing the updated user data.

        Returns:
            - User | None - The updated user object if found, otherwise None.
        """

        user = await self.get_one_or_none(filters=[User.id == user_id])

        if user is None:
            return None

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user
