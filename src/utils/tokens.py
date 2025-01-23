from datetime import UTC, datetime, timedelta
from typing import Any

from jwt import PyJWTError, decode, encode

from src.settings import settings


def create_jwt(
    data: dict[str, Any] | None = None,
    expire_time_seconds: int | None = None,
) -> str:
    """
    Create a JSON Web Token (JWT) with optional data and expiration time.

    Args:
        - data (dict[str, Any] | None): The payload to include in the JWT. Defaults to an empty dictionary if not provided.
        - expire_time_seconds (int | None): The number of seconds until the token expires. If not provided, the token will not include an expiration time.

    Returns:
        - str: The encoded JWT as a string.

    Example:
        >>> create_jwt({"user_id": 123}, 3600)
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """

    data = data or {}
    if expire_time_seconds:
        data.update({"exp": datetime.now(UTC) + timedelta(seconds=expire_time_seconds)})
    return encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(
    token: str,
) -> dict[str, Any] | None:
    """
    Decode a JSON Web Token (JWT) and return its payload.

    Args:
        - token (str): The encoded JWT string to decode.

    Returns:
        - dict[str, Any] | None: The decoded payload as a dictionary if the token is valid. Returns None if decoding fails.

    Example:
        >>> decode_jwt("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        {"user_id": 123, "exp": 1693483200}
    """

    try:
        return decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
    except PyJWTError:
        return None
