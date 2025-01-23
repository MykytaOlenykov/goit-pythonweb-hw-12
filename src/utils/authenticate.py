from fastapi import Depends, Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.database.db import get_db
from src.services.users import UsersService
from src.schemas.tokens import BaseTokenPayloadModel
from src.utils.tokens import decode_jwt


async def authenticate(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Function to authenticate the user based on a JWT token.

    Args:
        authorization (str | None): The Authorization header containing the JWT token.
        db (AsyncSession): The database session to fetch user information.

    Returns:
        User object if authentication is successful.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Steps:
        1. Extracts the JWT token from the `Authorization` header.
        2. Verifies the token and decodes it.
        3. Validates the decoded payload using `BaseTokenPayloadModel`.
        4. Fetches the user from the database using `UsersService` with the `user_id` from the token payload.
        5. If any step fails (e.g., missing token, invalid token, user not found), raises an `HTTP_401_UNAUTHORIZED` exception.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    scheme, token = get_authorization_scheme_param(authorization)

    if not (authorization and scheme and token):
        raise credentials_exception

    if scheme != "Bearer" or not token:
        raise credentials_exception

    try:
        payload = decode_jwt(token) or {}
        verified_payload = BaseTokenPayloadModel(**payload)
    except ValidationError:
        raise credentials_exception

    users_service = UsersService(db)
    user = await users_service.get_by_id_or_none(id=verified_payload.user_id)

    if not user:
        raise credentials_exception

    return user
