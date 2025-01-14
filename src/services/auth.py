from urllib.parse import urljoin

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TokenType, UserStatus
from src.services.users import UsersService
from src.services.tokens import TokensService
from src.services.mail import MailService, conf
from src.schemas.auth import LoginModel, VerifyModel
from src.schemas.users import UserCreateModel
from src.schemas.tokens import BaseTokenPayloadCreateModel, BaseTokenPayloadModel
from src.schemas.mail import VerificationMail
from src.utils.hashing import hash_secret
from src.utils.tokens import decode_jwt
from src.settings import settings
from src.utils.exceptions import (
    HTTPUnauthorizedException,
    HTTPNotFoundException,
    HTTPConflictException,
)


class AuthService:

    def __init__(self, db: AsyncSession):
        self.users_service = UsersService(db)
        self.tokens_service = TokensService(db)
        self.mail_service = MailService(conf)

    async def signup(self, background_tasks: BackgroundTasks, body: UserCreateModel):
        user = await self.users_service.get_by_email_or_none(email=body.email)

        if user:
            raise HTTPConflictException("This email is already signed up")

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

    async def verify_user(self, token: str):
        payload = decode_jwt(token=token)

        try:
            verified_payload = BaseTokenPayloadModel(**payload)
        except Exception:
            raise HTTPUnauthorizedException("Invalid token")

        if verified_payload.token_type != TokenType.VERIFICATION:
            raise HTTPUnauthorizedException("Invalid token")

        try:
            await self.tokens_service.get_token_or_fail(token)
        except HTTPNotFoundException:
            raise HTTPUnauthorizedException("Invalid token")

        user = await self.users_service.get_by_id_or_fail(verified_payload.user_id)

        if user.status != UserStatus.REGISTERED:
            raise HTTPConflictException("User is already verified")

        await self.users_service.change_user_status_by_id(
            id=verified_payload.user_id,
            status=UserStatus.VERIFIED,
        )
        await self.tokens_service.delete_token(token)

    async def resend_verification_email(
        self,
        background_tasks: BackgroundTasks,
        body: VerifyModel,
    ):
        user = await self.users_service.get_by_email_or_none(body.email)
        user_id = user.id
        username = user.username
        email = user.email

        if user is None:
            raise HTTPNotFoundException("Invalid email")

        if user.status != UserStatus.REGISTERED:
            raise HTTPConflictException("User is already verified")

        tokens = list(filter(lambda x: x.type == TokenType.VERIFICATION, user.tokens))
        await self.tokens_service.delete_many_tokens([token.token for token in tokens])

        payload = BaseTokenPayloadCreateModel(user_id=user_id)
        token = await self.tokens_service.create_verification_token(payload)

        verification_url = urljoin(settings.BASE_URL, f"api/auth/verify/{token.token}")
        mail_body = VerificationMail(
            verification_url=verification_url,
            email=email,
            username=username,
        )
        self.mail_service.send_verification_mail(background_tasks, mail_body)
