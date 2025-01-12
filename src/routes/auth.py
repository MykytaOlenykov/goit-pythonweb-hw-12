from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import AuthService
from src.schemas.auth import ResponseSignupModel
from src.schemas.users import UserCreateModel
from src.utils.exceptions import bad_request_response_docs, conflict_response_docs

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSignupModel,
    responses={**bad_request_response_docs, **conflict_response_docs},
)
async def create_contact(
    body: UserCreateModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.signup(body)
    return {"message": "ok"}
