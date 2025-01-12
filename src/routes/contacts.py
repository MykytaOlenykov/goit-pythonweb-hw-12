from typing import List

from fastapi import APIRouter, Query, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts import ContactsService
from src.schemas.contacts import (
    ContactCreateModel,
    ContactUpdateModel,
    ResponseContactModel,
)
from src.utils.exceptions import bad_request_response_docs, not_found_response_docs

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ResponseContactModel])
async def get_contacts(
    search: str | None = Query(
        default=None, description="Search by first_name, last_name and email"
    ),
    birthdays_within: int | None = Query(
        default=None,
        description="Filter contacts with birthdays within the given number of days",
    ),
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.get_all(
        search=search,
        birthdays_within=birthdays_within,
    )


@router.get(
    "/{id}",
    response_model=ResponseContactModel,
    responses={**not_found_response_docs},
)
async def get_contact_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.get_by_id(id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseContactModel,
    responses={**bad_request_response_docs},
)
async def create_contact(
    body: ContactCreateModel,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.create(body)


@router.put(
    "/{id}",
    response_model=ResponseContactModel,
    responses={
        **bad_request_response_docs,
        **not_found_response_docs,
    },
)
async def update_contact_by_id(
    body: ContactUpdateModel,
    id: int,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.update_by_id(body, id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**not_found_response_docs},
)
async def delete_contact_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    await contacts_service.delete_by_id(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
