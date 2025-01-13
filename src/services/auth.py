from urllib.parse import urljoin

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TokenType, UserStatus
from src.services.users import UsersService
from src.services.tokens import TokensService
from src.services.mail import MailService, conf
from src.schemas.users import UserCreateModel
from src.schemas.tokens import BaseTokenPayloadCreateModel, BaseTokenPayloadModel
from src.schemas.mail import VerificationMail
from src.utils.exceptions import HTTPUnauthorizedException, HTTPConflictException
from src.utils.hashing import hash_secret
from src.utils.tokens import decode_jwt
from src.settings import settings


class AuthService:

    def __init__(self, db: AsyncSession):
        self.users_service = UsersService(db)
        self.tokens_service = TokensService(db)
        self.mail_service = MailService(conf)

    async def signup(self, background_tasks: BackgroundTasks, body: UserCreateModel):
        user = await self.users_service.get_by_email_or_none(email=body.email)

        if user:
            raise HTTPConflictException("User exists")

        hashed_password = hash_secret(body.email)
        body.password = hashed_password

        created_user = await self.users_service.create(body)

        payload = BaseTokenPayloadCreateModel(user_id=created_user.id)
        token = await self.tokens_service.create_verification_token(payload)

        verification_url = urljoin(settings.BASE_URL, f"api/auth/verify/{token.token}")
        mail_body = VerificationMail(
            verification_url=verification_url,
            email=body.email,
            username=body.username,
        )
        self.mail_service.send_verification_mail(background_tasks, mail_body)
