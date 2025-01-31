from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User, UserRole
from src.services.users import UsersService
from src.schemas.users import ResponseAvatarModel
from src.utils.authenticate import authenticate
from src.utils.role_guard import role_guard
from src.utils.exceptions import (
    bad_request_response_docs,
    unauthorized_response_docs,
    forbidden_response_docs,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.put(
    "/avatars",
    status_code=status.HTTP_200_OK,
    response_model=ResponseAvatarModel,
    responses={
        **bad_request_response_docs,
        **unauthorized_response_docs,
        **forbidden_response_docs,
    },
)
async def change_avatar(
    avatar: UploadFile = File(),
    user: User = Depends(role_guard([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    users_service = UsersService(db)
    return await users_service.change_user_avatar_by_id(id=user.id, avatar=avatar)
