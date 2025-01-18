from datetime import UTC, datetime, timedelta
from typing import Any

from jwt import PyJWTError, decode, encode

from src.settings import settings


def create_jwt(
    data: dict[str, Any] | None = None,
    expire_time_seconds: int | None = None,
) -> str:
    data = data or {}
    if expire_time_seconds:
        data.update({"exp": datetime.now(UTC) + timedelta(seconds=expire_time_seconds)})
    return encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(
    token: str,
) -> dict[str, Any] | None:
    try:
        return decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
    except PyJWTError:
        return None
