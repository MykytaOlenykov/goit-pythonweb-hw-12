from typing import List

from fastapi import APIRouter, Query, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts import ContactsService
from src.schemas import ContactCreateModel, ContactUpdateModel, ResponseContactModel

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ResponseContactModel])
async def get_contacts(
    search: str | None = Query(
        default=None, description="Search by first_name, last_name and email"
    ),
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.get_all(search=search)


@router.get("/{id}", response_model=ResponseContactModel)
async def get_contacts(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.get_by_id(id)


@router.post(
    "/",
    response_model=ResponseContactModel,
    status_code=status.HTTP_201_CREATED,
)
async def get_contacts(
    body: ContactCreateModel,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.create(body)


@router.put("/{id}", response_model=ResponseContactModel)
async def get_contacts(
    body: ContactUpdateModel,
    id: int,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    return await contacts_service.update_by_id(body, id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def get_contacts(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    await contacts_service.delete_by_id(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
