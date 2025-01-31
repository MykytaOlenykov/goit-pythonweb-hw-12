from typing import List

from fastapi import Depends

from src.database.models import UserRole
from src.schemas.users import UserBaseModel
from src.utils.authenticate import authenticate
from src.utils.exceptions import HTTPForbiddenException


def role_guard(allowed_roles: List[UserRole]):
    """
    Middleware function to enforce role-based access control.

    Args:
        - allowed_roles (List[UserRole]): A list of roles that are allowed to access the resource.

    Returns:
        - Callable function that acts as a dependency in FastAPI routes.

    Raises:
        - HTTPForbiddenException: If the user's role is not in the list of allowed roles.

    Steps:
        1. Retrieves the authenticated user using the `authenticate` dependency.
        2. Checks if the user's role is in the `allowed_roles` list.
        3. If the user has sufficient permissions, returns the `User` object.
        4. If the user does not have the required role, raises an `HTTP_403_FORBIDDEN` exception.
    """

    def _role_guard(
        user: UserBaseModel = Depends(authenticate),
    ):
        if user.role not in allowed_roles:
            raise HTTPForbiddenException(detail="Forbidden: insufficient permissions")
        return user

    return _role_guard
