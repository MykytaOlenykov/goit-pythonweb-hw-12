from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UsersRepository
from src.database.models import User, UserStatus
from src.schemas.users import UserCreateModel, UserStatusUpdateModel
from src.utils.exceptions import HTTPNotFoundException


class UsersService:

    def __init__(self, db: AsyncSession):
        self.users_repository = UsersRepository(db)

    async def get_by_email_or_none(self, email: str):
        filters = [User.email == email]
        return await self.users_repository.get_one_or_none(filters=filters)

    async def get_by_id_or_fail(self, id: int):
        filters = [User.id == id]
        user = await self.users_repository.get_one_or_none(filters=filters)

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
