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
    """
    Creates a new contact.

    :param body: The contact data to be created.
    :type body: ContactSchema
    :param db: The database session.
    :type db: AsyncSession, optional
    :param user: The current user.
    :type user: User, optional

    :return: The created contact.
    :rtype: ContactResponse
    """
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
    """
   Retrieves contacts based on the provided filters.

   :param name: Filter contacts by name. Must be between 1 and 50 characters long.
   :type name: str
   :param surname: Filter contacts by surname. Must be between 1 and 50 characters long.
   :type surname: str
   :param email: Filter contacts by email. Must be between 1 and 50 characters long.
   :type email: str
   :param birthdays: If True, only show contacts with birthdays in the next 7 days.
   :type birthdays: bool
   :param limit: Maximum number of contacts to retrieve. Must be between 10 and 500.
   :type limit: int
   :param offset: Number of contacts to skip before retrieving the results. Must be greater than or equal to 0.
   :type offset: int
   :param db: Database session to use for retrieving contacts.
   :type db: AsyncSession
   :param user: User object representing the current active user.
   :type user: User

   :return: List of contacts that match the provided filters.
   :rtype: list[ContactResponse]
   """
    contacts = await repo_book.get_contacts(name, surname, email, birthdays, limit, offset, db, user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(current_active_user)):
    """
    Retrieves a contact using the specified contact ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The current active user.
    :type user: User

    :return: The retrieved contact.
    :rtype: ContactResponse

    :raises HTTPException: If the contact is not found (HTTP 404 NOT FOUND).
    """
    contact = await repo_book.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.put('/{contact_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(current_active_user)):
    """
    Update a contact in the database.

    :param body: The updated contact information.
    :type body: ContactSchema
    :param contact_id: The ID of the contact to be updated.
    :type contact_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The authenticated user.
    :type user: User

    :returns: The updated contact information.
    :rtype: ContactResponse

    :raises HTTPException: If the contact is not found in the database.
    """
    contact = await repo_book.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete('/{contact_id}', response_model=ContactResponse,
               dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(current_active_user)):
    """
    Delete a contact by its ID.

    :param contact_id: The ID of the contact to be deleted.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The current authenticated user.
    :type user: User

    :return: The deleted contact.
    :rtype: ContactResponse
    """
    contact = await repo_book.delete_contact(contact_id, db, user)
    return contact
