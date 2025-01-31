from typing import List

from fastapi import Depends

from src.database.models import User, UserRole
from src.utils.authenticate import authenticate
from src.utils.exceptions import HTTPForbiddenException


def role_guard(allowed_roles: List[UserRole]):
    def _role_guard(
        user: User = Depends(authenticate),
    ):
        if user.role not in allowed_roles:
            raise HTTPForbiddenException(detail="Forbidden: insufficient permissions")
        return user

    return _role_guard
