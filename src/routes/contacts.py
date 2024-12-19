from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.contacts import ContactsService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/")
async def get_contacts(
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    contacts_service = ContactsService(db)
    contacts = await contacts_service.get_all(search=search)
    return contacts
