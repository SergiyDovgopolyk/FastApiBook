import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Contact, User
from src.schemas.contact import ContactSchema


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(name: str | None, surname: str | None, email: str | None, birthdays: bool, limit: int,
                       offset: int, db: AsyncSession, user: User):
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
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
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
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
