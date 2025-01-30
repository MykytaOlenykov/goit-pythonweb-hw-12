from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.upload_file import UploadFileService
from src.repository.users import UsersRepository
from src.database.models import User, UserStatus
from src.schemas.users import (
    UserCreateModel,
    UserStatusUpdateModel,
    UserAvatarUpdateModel,
    ChangePasswordModel,
)
from src.utils.exceptions import HTTPNotFoundException
from src.settings import settings


class UsersService:
    """
    UsersService handles user-related operations such as retrieving, creating, updating, and managing users.

    Args:
        - db: AsyncSession - The database session used for user-related queries and updates.

    Methods:
        - get_by_email_or_none: Retrieves a user by their email, or returns None if not found.
        - get_by_id_or_none: Retrieves a user by their ID, or returns None if not found.
        - get_by_id_or_fail: Retrieves a user by their ID, raises an exception if not found.
        - create: Creates a new user in the database.
        - change_user_status_by_id: Updates the status of a user by their ID.
        - change_user_avatar_by_id: Updates the avatar of a user by their ID.
    """

    def __init__(self, db: AsyncSession):
        self.users_repository = UsersRepository(db)
        self.upload_file_service = UploadFileService(
            cloud_name=settings.CLOUDINARY_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

    async def get_by_email_or_none(self, email: str):
        """
        Retrieves a user by their email.

        Args:
            - email: str - The email address to search for.

        Returns:
            - User or None - The user object if found, or None if no user is found.
        """

        filters = [User.email == email]
        return await self.users_repository.get_one_or_none(filters=filters)

    async def get_by_id_or_none(self, id: int):
        """
        Retrieves a user by their ID.

        Args:
            - id: int - The ID of the user to search for.

        Returns:
            - User or None - The user object if found, or None if no user is found.
        """

        filters = [User.id == id]
        return await self.users_repository.get_one_or_none(filters=filters)

    async def get_by_id_or_fail(self, id: int):
        """
        Retrieves a user by their ID, raises an exception if not found.

        Args:
            - id: int - The ID of the user to search for.

        Returns:
            - User - The user object if found.

        Raises:
            - HTTPNotFoundException: If no user is found with the given ID.
        """

        user = await self.get_by_id_or_none(id)

        if user is None:
            raise HTTPNotFoundException("User not found")

        return user

    async def create(self, body: UserCreateModel):
        """
        Creates a new user in the database.

        Args:
            - body: UserCreateModel - The user creation data.

        Returns:
            - User - The created user object.
        """

        return await self.users_repository.create(body)

    async def change_user_status_by_id(self, id: int, status: UserStatus):
        """
        Updates the status of a user by their ID.

        Args:
            - id: int - The ID of the user to update.
            - status: UserStatus - The new status to set.

        Returns:
            - User - The updated user object.

        Raises:
            - HTTPNotFoundException: If no user is found with the given ID.
        """

        body = UserStatusUpdateModel(status=status)
        user = await self.users_repository.update(user_id=id, body=body)

        if user is None:
            raise HTTPNotFoundException("User not found")

        return user

    async def change_user_password_by_id(self, id: int, body: ChangePasswordModel):
        """
        Changes the password of a user by their ID.

        This method updates the user's password using the provided ID and new password details.
        If the user is not found, it raises a `HTTPNotFoundException`. If successful, it returns the updated user object.

        Args:
            - id: int - The ID of the user whose password needs to be changed.
            - body: ChangePasswordModel - The new password details for the user, typically including the current password and the new one.

        Raises:
            - HTTPNotFoundException: If no user with the provided ID is found.

        Returns:
            - User: The updated user object after changing the password.
        """

        user = await self.users_repository.update(user_id=id, body=body)

        if user is None:
            raise HTTPNotFoundException("User not found")

        return user

    async def change_user_avatar_by_id(self, id: int, avatar: UploadFile):
        """
        Updates the avatar of a user by their ID.

        Args:
            - id: int - The ID of the user to update.
            - avatar: UploadFile - The new avatar file to upload.

        Returns:
            - dict - A dictionary containing the new avatar URL.

        Raises:
            - HTTPNotFoundException: If no user is found with the given ID.
        """

        avatar_url = self.upload_file_service.upload_file(file=avatar, user_id=id)
        body = UserAvatarUpdateModel(avatar_url=avatar_url)
        await self.users_repository.update(user_id=id, body=body)
        return {"avatar_url": avatar_url}
