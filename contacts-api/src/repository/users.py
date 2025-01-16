from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.database.models import User
from src.schemas.users import UserCreateModel


class UsersRepository:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_one_or_none(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
    ):
        return (
            await self.db.execute(select(User).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, body: UserCreateModel):
        user = User(**body.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, body: BaseModel):
        user = await self.get_one_or_none(filters=[User.id == user_id])

        if user is None:
            return None

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user
