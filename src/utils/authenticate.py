import json

from fastapi import Depends, Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from pydantic import ValidationError

from src.database.db import get_db
from src.database.models import TokenType
from src.redis.redis import get_redis
from src.services.users import UsersService
from src.schemas.users import UserBaseModel
from src.schemas.tokens import BaseTokenPayloadModel
from src.utils.tokens import decode_jwt


async def authenticate(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Function to authenticate the user based on a JWT token.

    Args:
        - authorization (str | None): The Authorization header containing the JWT token.
        - db (AsyncSession): The database session to fetch user information.

    Returns:
        - User object if authentication is successful.

    Raises:
        - HTTPException: If the token is invalid or the user is not found.

    Steps:
        1. Extracts the JWT token from the `Authorization` header.
        2. Verifies the token and decodes it.
        3. Validates the decoded payload using `BaseTokenPayloadModel`.
        4. Checks if the user is cached in Redis.
        5. If not cached, fetches the user from the database using `UsersService` with the `user_id` from the token payload.
        6. Caches the user data if it was fetched from the database.
        7. If any step fails (e.g., missing token, invalid token, user not found), raises an `HTTP_401_UNAUTHORIZED` exception.
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

    if verified_payload.token_type != TokenType.ACCESS:
        raise credentials_exception

    user_id = verified_payload.user_id

    cached_user = await redis.get(f"user:{user_id}")
    if cached_user:
        user_data = json.loads(cached_user)
        user = UserBaseModel(**user_data)
    else:
        users_service = UsersService(db)
        user_data = await users_service.get_by_id_or_none(id=user_id)

        if not user_data:
            raise credentials_exception

        user = UserBaseModel(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            status=user_data.status,
            role=user_data.role,
            avatar_url=user_data.avatar_url,
        )

        await redis.set(f"user:{user_id}", user.model_dump_json(), ex=3600)

    return user
