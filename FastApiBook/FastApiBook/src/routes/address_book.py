from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.fu_db import get_db
from src.models.models import User
from src.repository import address_book as repo_book
from src.schemas.contact import ContactSchema, ContactResponse
from src.services.auth import current_active_user

router = APIRouter(prefix='/address_book', tags=['address_book'])


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(current_active_user)):
    contact = await repo_book.create_contact(body, db, user)
    return contact


@router.get('/', response_model=list[ContactResponse], dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contacts(name: str = Query(None, min_length=1, max_length=50),  # filter by name
                       surname: str = Query(None, min_length=1, max_length=50),  # filter by surname
                       email: str = Query(None, min_length=1, max_length=50),  # filter by email
                       birthdays: bool = Query(False),  # show next 7 days birthdays
                       limit: int = Query(10, ge=10, le=500),
                       offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(current_active_user)):
    contacts = await repo_book.get_contacts(name, surname, email, birthdays, limit, offset, db, user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(current_active_user)):
    contact = await repo_book.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.put('/{contact_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(current_active_user)):
    contact = await repo_book.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete('/{contact_id}', response_model=ContactResponse,
               dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(current_active_user)):
    contact = await repo_book.delete_contact(contact_id, db, user)
    return contact
