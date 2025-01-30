from fastapi import (
    Request,
    Response,
    BackgroundTasks,
    APIRouter,
    Depends,
    Cookie,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.database.db import get_db
from src.database.models import User
from src.services.auth import AuthService
from src.settings import settings
from src.schemas.users import UserCreateModel
from src.schemas.auth import (
    LoginModel,
    VerifyModel,
    ResetPasswordModel,
    ResponseSignupModel,
    ResponseLoginModel,
    ResponseRefreshModel,
    ResponseCurrentUserModel,
    ResponseVerifyModel,
    ResponseResetPasswordModel,
)
from src.utils.authenticate import authenticate
from src.utils.exceptions import (
    bad_request_response_docs,
    unauthorized_response_docs,
    not_found_response_docs,
    conflict_response_docs,
    too_many_requests_response_docs,
)

router = APIRouter(prefix="/auth", tags=["auth"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/signup",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSignupModel,
    responses={**bad_request_response_docs, **conflict_response_docs},
)
async def signup(
    background_tasks: BackgroundTasks,
    body: UserCreateModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.signup(background_tasks, body)
    return {
        "message": "Registration successful. Please check your email to activate your account."
    }


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ResponseLoginModel,
    responses={**bad_request_response_docs, **unauthorized_response_docs},
)
async def login(
    response: Response,
    body: LoginModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    tokens = await auth_service.login(body)
    response.set_cookie(
        "refresh_token",
        tokens.get("refresh_token"),
        max_age=settings.JWT_REFRESH_EXPIRATION_SECONDS,
        httponly=True,
        secure=True,
    )
    return {"access_token": tokens.get("access_token"), "token_type": "bearer"}


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authenticate)],
    responses={**unauthorized_response_docs},
)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.logout(refresh_token)
    response.delete_cookie("refresh_token", httponly=True, secure=True)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=ResponseRefreshModel,
    responses={**unauthorized_response_docs},
)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    tokens = await auth_service.refresh(refresh_token)
    response.set_cookie(
        "refresh_token",
        tokens.get("refresh_token"),
        max_age=settings.JWT_REFRESH_EXPIRATION_SECONDS,
        httponly=True,
        secure=True,
    )
    return {"access_token": tokens.get("access_token"), "token_type": "bearer"}


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ResponseCurrentUserModel,
    responses={**unauthorized_response_docs, **too_many_requests_response_docs},
)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(authenticate)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }


@router.get(
    "/verify/{token}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseVerifyModel,
    responses={
        **not_found_response_docs,
        **unauthorized_response_docs,
        **conflict_response_docs,
    },
)
async def verify_user(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.verify_user(token)
    return {
        "message": "Your email has been successfully verified. You can now log in to your account."
    }


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=ResponseVerifyModel,
    responses={
        **bad_request_response_docs,
        **not_found_response_docs,
        **conflict_response_docs,
    },
)
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    body: VerifyModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.resend_verification_email(background_tasks, body)
    return {"message": "Please check your email to activate your account."}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    response_model=ResponseResetPasswordModel,
    responses={**bad_request_response_docs, **unauthorized_response_docs},
)
async def forgot_password(
    background_tasks: BackgroundTasks,
    body: ResetPasswordModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.forgot_password(background_tasks, body)
    return {
        "message": "If this email exists, we have sent password reset instructions."
    }
