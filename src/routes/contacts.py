from typing import List

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts import ContactsService
from src.schemas import ResponseContactModel

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ResponseContactModel])
async def get_contacts(
    search: str | None = Query(
        default=None, description="Search by first_name, last_name and email"
    ),
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    contacts = await contacts_service.get_all(search=search)
    return contacts
