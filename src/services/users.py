from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.upload_file import UploadFileService
from src.repository.users import UsersRepository
from src.database.models import User, UserStatus
from src.schemas.users import (
    UserCreateModel,
    UserStatusUpdateModel,
    UserAvatarUpdateModel,
)
from src.utils.exceptions import HTTPNotFoundException
from src.settings import settings


class UsersService:

    def __init__(self, db: AsyncSession):
        self.users_repository = UsersRepository(db)
        self.upload_file_service = UploadFileService(
            cloud_name=settings.CLOUDINARY_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

    async def get_by_email_or_none(self, email: str):
        filters = [User.email == email]
        return await self.users_repository.get_one_or_none(filters=filters)

    async def get_by_id_or_none(self, id: int):
        filters = [User.id == id]
        return await self.users_repository.get_one_or_none(filters=filters)

    async def get_by_id_or_fail(self, id: int):
        user = await self.get_by_id_or_none(id)

        if user is None:
            raise HTTPNotFoundException("User not found")

        return user

    async def create(self, body: UserCreateModel):
        return await self.users_repository.create(body)

    async def change_user_status_by_id(self, id: int, status: UserStatus):
        body = UserStatusUpdateModel(status=status)
        user = await self.users_repository.update(user_id=id, body=body)

        if user is None:
            raise HTTPNotFoundException("User not found")

        return user

    async def change_user_avatar_by_id(self, id: int, avatar: UploadFile):
        avatar_url = self.upload_file_service.upload_file(file=avatar, user_id=id)
        body = UserAvatarUpdateModel(avatar_url=avatar_url)
        await self.users_repository.update(user_id=id, body=body)
        return {"avatar_url": avatar_url}
