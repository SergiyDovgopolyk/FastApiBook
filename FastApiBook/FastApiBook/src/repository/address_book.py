import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Contact, User
from src.schemas.contact import ContactSchema


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    Creates a new contact in the database.

    :param body: The contact information to be created.
    :type body: ContactSchema
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user creating the contact.
    :type user: User

    :return: The created contact object.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(name: str | None, surname: str | None, email: str | None, birthdays: bool, limit: int,
                       offset: int, db: AsyncSession, user: User):
    """
    Retrieves contacts based on the given search criteria.

    :param name: The name to search for in the contacts.
    :type name: str or None
    :param surname: The surname to search for in the contacts.
    :type surname: str or None
    :param email: The email to search for in the contacts.
    :type email: str or None
    :param birthdays: Specifies if contacts with upcoming birthdays should be included.
    :type birthdays: bool
    :param limit: The maximum number of contacts to retrieve.
    :type limit: int
    :param offset: The number of contacts to skip before retrieving.
    :type offset: int
    :param db: The database session to use for executing the query.
    :type db: AsyncSession
    :param user: The user associated with the contacts.
    :type user: User

    :return: A list of contacts that match the search criteria.
    :rtype: List[Contact]
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    if name:
        stmt = stmt.filter(Contact.name.like(f'%{name}%'))
    if surname:
        stmt = stmt.filter(Contact.surname.like(f'%{surname}%'))
    if email:
        stmt = stmt.filter(Contact.email.like(f'%{email}%'))
    if birthdays:
        current_date = datetime.date.today()
        today = current_date.strftime('%m-%d')
        seven_days = (current_date + datetime.timedelta(7)).strftime('%m-%d')
        stmt = stmt.filter(func.to_char(Contact.birthday, 'MM-DD').between(today, seven_days))  # Thanks "AusAura"
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Retrieves a contact from the database based on the provided contact ID and user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user object.
    :type user: User

    :return: The retrieved contact, or None if not found.
    :rtype: Contact or None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
    Update a contact with the given contact ID.

    :param contact_id: The ID of the contact to be updated.
    :type contact_id: int
    :param body: The updated contact information.
    :type body: ContactSchema
    :param db: The database session.
    :type db: AsyncSession
    :param user: The user performing the update.
    :type user: User

    :return: The updated contact object.
    :rtype: Contact
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.number = body.number
        contact.birthday = body.birthday
        contact.description = body.description
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Delete a contact from the database.

    :param contact_id: The ID of the contact to be deleted.
    :type contact_id: int
    :param db: The database session object.
    :type db: AsyncSession
    :param user: The user object associated with the contact.
    :type user: User

    :return: The deleted contact object if it exists, otherwise None.
    :rtype: Contact or None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
