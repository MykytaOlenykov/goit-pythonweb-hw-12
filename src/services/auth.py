from sqlalchemy.ext.asyncio import AsyncSession

from src.services.users import UsersService
from src.services.tokens import TokensService
from src.schemas.users import UserCreateModel
from src.schemas.tokens import BaseTokenPayloadCreateModel
from src.utils.exceptions import HTTPConflictException
from src.utils.hashing import hash_secret


class AuthService:

    def __init__(self, db: AsyncSession):
        self.users_service = UsersService(db)
        self.tokens_service = TokensService(db)

    async def signup(self, body: UserCreateModel):
        user = await self.users_service.get_by_email_or_none(email=body.email)

        if user:
            raise HTTPConflictException("User exists")

        hashed_password = hash_secret(body.email)
        body.password = hashed_password

        created_user = await self.users_service.create(body)

        payload = BaseTokenPayloadCreateModel(user_id=created_user.id)
        token = await self.tokens_service.create_activation_token(payload)

        # send email...
