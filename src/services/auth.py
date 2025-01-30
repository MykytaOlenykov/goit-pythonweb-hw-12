from urllib.parse import urljoin

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.database.models import TokenType, UserStatus
from src.services.users import UsersService
from src.services.tokens import TokensService
from src.services.mail import MailService, conf
from src.schemas.auth import (
    LoginModel,
    VerifyModel,
    ResetPasswordModel,
)
from src.schemas.users import UserCreateModel, ChangePasswordModel
from src.schemas.tokens import BaseTokenPayloadCreateModel, BaseTokenPayloadModel
from src.schemas.mail import VerificationMail, ResetPasswordMail
from src.utils.hashing import hash_secret, verify_secret
from src.utils.tokens import decode_jwt
from src.settings import settings
from src.utils.exceptions import (
    HTTPUnauthorizedException,
    HTTPNotFoundException,
    HTTPConflictException,
)


class AuthService:
    """
    AuthService handles user authentication, registration, and token management.

    Args:
        - db: AsyncSession instance for database interaction.

    Methods:
        - signup: Registers a new user and sends a verification email.
        - login: Authenticates a user and generates access and refresh tokens.
        - refresh: Refreshes an expired access token using a refresh token.
        - logout: Logs out a user by invalidating the refresh token.
        - verify_user: Verifies a user's email using the provided verification token.
        - resend_verification_email: Resends the verification email to the user if the account is not verified.
    """

    def __init__(self, db: AsyncSession):
        self.users_service = UsersService(db)
        self.tokens_service = TokensService(db)
        self.mail_service = MailService(conf)

    async def signup(self, background_tasks: BackgroundTasks, body: UserCreateModel):
        """
        Handles user signup by creating a new user, hashing the password, and sending a verification email.

        Args:
            - background_tasks: BackgroundTasks instance for background operations.
            - body: UserCreateModel containing the user's signup information.

        Raises:
            - HTTPConflictException: If the email is already registered.
        """

        user = await self.users_service.get_by_email_or_none(email=body.email)

        if user:
            raise HTTPConflictException("This email is already signed up")

        hashed_password = hash_secret(body.password)
        body.password = hashed_password

        created_user = await self.users_service.create(body)

        payload = BaseTokenPayloadCreateModel(user_id=created_user.id)
        token = await self.tokens_service.create_token(
            token_type=TokenType.VERIFICATION,
            payload=payload,
        )

        verification_url = urljoin(settings.BASE_URL, f"api/auth/verify/{token.token}")
        mail_body = VerificationMail(
            verification_url=verification_url,
            email=body.email,
            username=body.username,
        )
        self.mail_service.send_verification_mail(background_tasks, mail_body)

    async def login(self, body: LoginModel):
        """
        Authenticates the user with the provided email and password.

        Args:
            - body: LoginModel containing the user's email and password.

        Returns:
            - Dictionary containing the access and refresh tokens.

        Raises:
            - HTTPUnauthorizedException: If the credentials are invalid or the account is not verified.
        """

        user = await self.users_service.get_by_email_or_none(email=body.email)

        if user is None:
            raise HTTPUnauthorizedException("Invalid email or password")

        if user.status == UserStatus.REGISTERED:
            raise HTTPUnauthorizedException("User needs to verify their account")

        if user.status == UserStatus.DELETED:
            raise HTTPUnauthorizedException("User account is deleted")

        password_verified = verify_secret(body.password, user.password)

        if not password_verified:
            raise HTTPUnauthorizedException("Invalid email or password")

        payload = BaseTokenPayloadCreateModel(user_id=user.id)
        access_token = self.tokens_service.generate_token(
            token_type=TokenType.ACCESS,
            payload=payload,
        )
        refresh_token = await self.tokens_service.create_token(
            token_type=TokenType.REFRESH,
            payload=payload,
        )

        return {"access_token": access_token, "refresh_token": refresh_token.token}

    async def refresh(self, refresh_token: str | None):
        """
        Refreshes the access token using a valid refresh token.

        Args:
            - refresh_token: str - The refresh token to be used for generating a new access token.

        Returns:
            - Dictionary containing the new access and refresh tokens.

        Raises:
            - HTTPUnauthorizedException: If the refresh token is invalid or expired.
        """

        if not refresh_token:
            raise HTTPUnauthorizedException("Invalid refresh token")

        payload = decode_jwt(token=refresh_token)
        token = await self.tokens_service.get_token_or_none(refresh_token)

        if not token:
            raise HTTPUnauthorizedException("Invalid refresh token")

        if not payload:
            await self.tokens_service.delete_token(refresh_token)
            raise HTTPUnauthorizedException("Invalid refresh token")

        try:
            verified_payload = BaseTokenPayloadModel(**payload)
        except ValidationError:
            await self.tokens_service.delete_token(refresh_token)
            raise HTTPUnauthorizedException("Invalid refresh token")

        if verified_payload.token_type != TokenType.REFRESH:
            raise HTTPUnauthorizedException("Invalid refresh token")

        new_payload = BaseTokenPayloadCreateModel(user_id=verified_payload.user_id)
        new_access_token = self.tokens_service.generate_token(
            token_type=TokenType.ACCESS,
            payload=new_payload,
        )
        new_refresh_token = await self.tokens_service.create_token(
            token_type=TokenType.REFRESH,
            payload=new_payload,
        )
        data = {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token.token,
        }

        await self.tokens_service.delete_token(refresh_token)

        return data

    async def logout(self, refresh_token: str | None):
        """
        Logs out the user by invalidating the refresh token.

        Args:
            - refresh_token: str - The refresh token to be invalidated.

        Raises:
            - HTTPUnauthorizedException: If the refresh token is invalid or not provided.
        """

        if not refresh_token:
            raise HTTPUnauthorizedException("Invalid refresh token")

        token = await self.tokens_service.get_token_or_none(
            refresh_token,
            token_type=TokenType.REFRESH,
        )

        if not token:
            raise HTTPUnauthorizedException("Invalid refresh token")

        await self.tokens_service.delete_token(refresh_token)

    async def verify_user(self, token: str):
        """
        Verifies a user's email using the provided verification token.

        Args:
            - token: str - The verification token.

        Raises:
            - HTTPUnauthorizedException: If the token is invalid or expired.
            - HTTPConflictException: If the user's email is already verified.
        """

        payload = decode_jwt(token=token)

        if not payload:
            raise HTTPUnauthorizedException("Invalid token")

        try:
            verified_payload = BaseTokenPayloadModel(**payload)
        except ValidationError:
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
        """
        Resends the verification email to a user if the account is not verified.

        Args:
            - background_tasks: BackgroundTasks - BackgroundTasks instance for background operations.
            - body: VerifyModel - Contains the email to resend the verification to.

        Raises:
            - HTTPNotFoundException: If the email is not registered.
            - HTTPConflictException: If the user is already verified.
        """

        user = await self.users_service.get_by_email_or_none(body.email)

        if user is None:
            raise HTTPUnauthorizedException("Invalid email")

        if user.status != UserStatus.REGISTERED:
            raise HTTPConflictException("User is already verified")

        user_id = user.id
        username = user.username
        email = user.email

        tokens = await self.tokens_service.get_tokens(
            user_id=user_id,
            type=TokenType.VERIFICATION,
        )
        await self.tokens_service.delete_many_tokens([token.token for token in tokens])

        payload = BaseTokenPayloadCreateModel(user_id=user_id)
        token = await self.tokens_service.create_token(
            token_type=TokenType.VERIFICATION,
            payload=payload,
        )

        verification_url = urljoin(settings.BASE_URL, f"api/auth/verify/{token.token}")
        mail_body = VerificationMail(
            verification_url=verification_url,
            email=email,
            username=username,
        )
        self.mail_service.send_verification_mail(background_tasks, mail_body)

    async def reset_password(self, token: str, body: ChangePasswordModel):
        """
        Resets the password for a user using a provided reset token.

        This method validates the provided reset token, verifies that it is a valid and unexpired reset token,
        decodes the token to get the user ID, and allows the user to reset their password.
        If any validation fails (e.g., invalid token or expired token), an HTTPUnauthorizedException is raised.
        Upon success, the user's password is updated and the token is deleted.

        Args:
            - token: str - The reset token sent to the user for password reset.
            - body: ChangePasswordModel - The new password details, typically containing the user's new password.

        Raises:
            - HTTPUnauthorizedException: If the token is invalid, expired, or doesn't match the expected reset token type.
            - HTTPNotFoundException: If the token is not found in the system or has already been used.
            - ValidationError: If the payload in the token cannot be validated correctly.

        Returns:
            - None: The method does not return anything. It updates the user's password and deletes the token.
        """

        payload = decode_jwt(token=token)

        if not payload:
            raise HTTPUnauthorizedException("Invalid token")

        try:
            verified_payload = BaseTokenPayloadModel(**payload)
        except ValidationError:
            raise HTTPUnauthorizedException("Invalid token")

        if verified_payload.token_type != TokenType.RESET:
            raise HTTPUnauthorizedException("Invalid token")

        try:
            await self.tokens_service.get_token_or_fail(token)
        except HTTPNotFoundException:
            raise HTTPUnauthorizedException("Invalid token")

        user = await self.users_service.get_by_id_or_fail(verified_payload.user_id)

        hashed_password = hash_secret(body.password)
        body.password = hashed_password

        await self.users_service.change_user_password_by_id(user.id, body=body)
        await self.tokens_service.delete_token(token)

    async def forgot_password(
        self,
        background_tasks: BackgroundTasks,
        body: ResetPasswordModel,
    ):
        """
        Handles the password reset request for a user.

        This method checks if a user exists by the provided email. If the user is found but hasn't verified their account,
        it raises an exception. If the user exists and is registered, it generates a new reset token, invalidates old tokens,
        and sends a reset password email to the user.

        Args:
            background_tasks: BackgroundTasks - The background tasks for sending the email asynchronously.
            body: ResetPasswordModel - The body of the reset password request containing the user's email.

        Raises:
            HTTPUnauthorizedException: If the user has not verified their account.

        Returns:
            None: The method does not return any data but sends an email with a reset password token if the process succeeds.
        """

        user = await self.users_service.get_by_email_or_none(email=body.email)

        if user is None:
            return

        if user.status == UserStatus.REGISTERED:
            raise HTTPUnauthorizedException("User needs to verify their account")

        user_id = user.id
        username = user.username
        email = user.email

        tokens = await self.tokens_service.get_tokens(
            user_id=user_id,
            type=TokenType.RESET,
        )
        await self.tokens_service.delete_many_tokens([token.token for token in tokens])

        payload = BaseTokenPayloadCreateModel(user_id=user_id)
        token = await self.tokens_service.create_token(
            token_type=TokenType.RESET,
            payload=payload,
        )

        mail_body = ResetPasswordMail(
            reset_token=token.token,
            email=email,
            username=username,
        )
        self.mail_service.send_reset_password_mail(background_tasks, mail_body)
